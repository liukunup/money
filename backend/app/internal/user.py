# -*- coding: UTF-8 -*-

from typing import Any

from sqlmodel import Session, select
from pydantic import EmailStr

from app.models.user import User, UserCreate, UserUpdate
from app.utils.security import get_password_hash, verify_password


# 创建用户
def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


# 更新用户
def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


# 获取用户
def get_user(*, session: Session, username: str, email: EmailStr) -> User | None:
    statement = select(User).where((User.username == username) | (User.email == email))
    user = session.exec(statement).first()
    return user


# 验证用户
def authenticate(*, session: Session, username: str, password: str) -> User | None:
    # 用户名和邮箱都可以作为登录凭证
    user = get_user(session=session, username=username, email=username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user