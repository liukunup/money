# -*- coding: UTF-8 -*-

import jwt
from jwt.exceptions import InvalidTokenError
from typing import Optional, Annotated
from datetime import datetime, timedelta
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from ..constant import JWTConfig
from ..models.user import User
from ..database import SessionDep

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class TokenData(BaseModel):
    username: str | None = None

# 哈希密码
def get_password_hash(password: str):
    return pwd_context.hash(password)

# 验证密码
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# 获取用户
def get_user(session: Session, username: str, email: str):
    return session.query(User).filter((User.username == username) | (User.email == email)).first()

# 验证用户
def authenticate_user(session: Session, username: str, password: str):
    user = get_user(session, username, username)  # 用户名和邮箱都可以作为登录凭证
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# 获取用户角色和权限
def get_roles_and_permissions(session: Session, username: str):
    user = session.query(User).filter(User.username == username).first()
    if not user:
        return [], []
    roles = [role.name for role in user.roles]
    permissions = []
    for role in user.roles:
        for permission in role.permissions:
            permissions.append(permission.name)
    return roles, permissions

# 创建访问令牌
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, session: Session = None):
    to_encode = data.copy()
    if session:
        roles, permissions = get_roles_and_permissions(session, data["sub"])
        to_encode.update({"roles": roles, "permissions": permissions})
    if expires_delta:
        expire = datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.now(datetime.timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWTConfig.SECRET_KEY, algorithm=JWTConfig.ALGORITHM)
    return encoded_jwt

# 获取当前用户
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWTConfig.SECRET_KEY, algorithms=[JWTConfig.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(session, username=token_data.username, email=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# 获取当前活跃用户
async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)],):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# 检查权限
def has_permission(required_permission: str):
    def check_permission(user: User = Depends(get_current_user), token: str = Depends(oauth2_scheme)):
        try:
            payload = jwt.decode(token, JWTConfig.SECRET_KEY, algorithms=[JWTConfig.ALGORITHM])
            permissions = payload.get("permissions", [])
            if required_permission not in permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions",
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    return check_permission