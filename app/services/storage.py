import os
import hashlib
from typing import Optional
from pathlib import Path
from minio import Minio
from minio.error import S3Error
from app.core.config import settings


class StorageService:
    """存储服务 - 支持本地和MinIO"""
    
    def __init__(self):
        self.use_minio = getattr(settings, 'MINIO_ENABLED', False)
        self.base_path = Path("data/imports")
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        if self.use_minio:
            self.minio_client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE
            )
            self.bucket_name = settings.MINIO_BUCKET
    
    def _compute_hash(self, content: bytes) -> str:
        """计算文件SHA256哈希"""
        return hashlib.sha256(content).hexdigest()
    
    def save_file(self, user_id: int, file_content: bytes, filename: str) -> tuple[str, str]:
        """
        保存文件，返回(file_path, file_hash)
        """
        file_hash = self._compute_hash(file_content)
        
        if self.use_minio:
            return self._save_to_minio(user_id, file_content, filename, file_hash)
        else:
            return self._save_to_local(user_id, file_content, filename, file_hash)
    
    def _save_to_local(self, user_id: int, content: bytes, filename: str, file_hash: str) -> tuple[str, str]:
        user_dir = self.base_path / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        
        # 使用hash作为文件名避免重复
        ext = Path(filename).suffix
        safe_filename = f"{file_hash[:16]}{ext}"
        file_path = user_dir / safe_filename
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        return str(file_path), file_hash
    
    def _save_to_minio(self, user_id: int, content: bytes, filename: str, file_hash: str) -> tuple[str, str]:
        import io
        ext = Path(filename).suffix
        object_name = f"{user_id}/{file_hash[:16]}{ext}"
        
        try:
            if not self.minio_client.bucket_exists(self.bucket_name):
                self.minio_client.make_bucket(self.bucket_name)
        except S3Error:
            self.minio_client.make_bucket(self.bucket_name)
        
        self.minio_client.put_object(
            self.bucket_name,
            object_name,
            io.BytesIO(content),
            len(content)
        )
        
        return f"minio://{self.bucket_name}/{object_name}", file_hash
    
    def get_file(self, file_path: str) -> Optional[bytes]:
        """获取文件内容"""
        if self.use_minio and file_path.startswith("minio://"):
            return self._get_from_minio(file_path)
        else:
            return self._get_from_local(file_path)
    
    def _get_from_local(self, file_path: str) -> Optional[bytes]:
        path = Path(file_path)
        if path.exists():
            return path.read_bytes()
        return None
    
    def _get_from_minio(self, minio_path: str) -> Optional[bytes]:
        parts = minio_path.replace("minio://", "").split("/", 1)
        if len(parts) != 2:
            return None
        bucket, object_name = parts
        try:
            response = self.minio_client.get_object(bucket, object_name)
            return response.read()
        except S3Error:
            return None
    
    def delete_file(self, file_path: str) -> bool:
        """删除文件"""
        if self.use_minio and file_path.startswith("minio://"):
            return self._delete_from_minio(file_path)
        else:
            return self._delete_from_local(file_path)
    
    def _delete_from_local(self, file_path: str) -> bool:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            return True
        return False
    
    def _delete_from_minio(self, minio_path: str) -> bool:
        parts = minio_path.replace("minio://", "").split("/", 1)
        if len(parts) != 2:
            return False
        bucket, object_name = parts
        try:
            self.minio_client.remove_object(bucket, object_name)
            return True
        except S3Error:
            return False


storage_service = StorageService()
