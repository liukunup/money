# -*- coding: UTF-8 -*-

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy.orm import Session
from ..constant import JWTConfig, Role as RoleEnum
from ..database import SessionDep
from ..models.user import User, Role
from ..utils.auth import get_password_hash, authenticate_user, create_access_token
from ..utils.email import send_email
import secrets
from ..response import Response

router = APIRouter()

def get_admin_role(session: Session):
    admin_role = session.query(Role).filter(Role.name == RoleEnum.ADMIN).first()
    if not admin_role:
        admin_role = Role(name=RoleEnum.ADMIN)
        session.add(admin_role)
        session.commit()
        session.refresh(admin_role)
    return admin_role

@router.post("/register", tags=["User"], summary="用户注册", description="使用邮箱和密码进行用户注册")
async def register(email: str, password: str, session: SessionDep) -> Response:
    """
    用户注册接口

    - **email**:    邮箱
    - **password**: 密码
    """
    # 检查邮箱是否已存在
    if session.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    # 创建新用户
    hashed_password = get_password_hash(password)
    new_user = User(email=email, hashed_password=hashed_password, disabled=False)
    # 检查是否为第一个用户
    first_user = session.query(User).first() is None
    if first_user:  # 将第一个用户设置为管理员
        admin_role = get_admin_role(session)
        new_user.roles.append(admin_role)
    # 保存用户
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    # 移除敏感字段再进行返回
    new_user.hashed_password = None
    return Response(code=200, message="success", data=new_user)

@router.post("/login", tags=["User"], summary="用户登录", description="使用用户名/邮箱和密码进行用户登录")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: SessionDep = Depends()) -> Response:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires, session=session)
    return Response(code=200, message="success", data={"accessToken": access_token, "tokenType": "bearer"})

@router.post("/logout", tags=["User"], summary="用户登出", description="JWT是无状态的，通常前端处理令牌删除")
async def logout() -> Response:
    return Response(code=200, message="success", data=None)

@router.post("/forgot-password", tags=["User"], summary="忘记密码", description="发送重置密码链接到用户邮箱")
async def forgot_password(email: str, session: SessionDep) -> Response:
    user = session.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    # 生成重置密码令牌
    reset_token = secrets.token_urlsafe(32)
    # 这里可以将令牌存储到数据库，以便后续验证
    reset_link = f"https://yourdomain.com/reset-password?token={reset_token}"
    # 构建邮件内容
    subject = "重置密码请求"
    message = f"您收到此邮件是因为您请求重置密码。请点击以下链接重置您的密码：\n{reset_link}\n如果您没有请求重置密码，请忽略此邮件。"
    # 发送邮件
    if send_email(email, subject, message):
        return {"message": "Password reset instructions sent to your email"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send email")

@router.get("/users/", tags=["User"], summary="获取用户列表", description="获取所有用户的列表")
async def list_users(page_num: int = 1, page_size: int = 10, db: Session = Depends(get_db)) -> Response:
    users = db.query(User).offset((page_num - 1) * page_size).limit(page_size).all()
    return Response(code=200, message="success", data=users)

# 通过jwt获取当前用户信息
@router.get("/users/me", tags=["User"], summary="获取当前用户信息", description="获取当前登录用户的信息")
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)],):
    return current_user