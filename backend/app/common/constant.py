from enum import Enum

class Role(str, Enum):
    """ 角色枚举类 """
    ADMIN = "admin"
    GUEST = "guest"
    USER = "user"

class JWTConfig:
    """ JWT 配置类 """
    SECRET_KEY: str = "your-secret-key"  # 替换为实际的密钥
    ALGORITHM: str = "HS256"  # 算法，这里使用 HS256
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 访问令牌过期时间，单位为分钟