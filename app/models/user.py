# -*- coding: UTF-8 -*-

from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

class User(SQLModel, table=True):
    __tablename__ = 'users'

    id: int = Field(primary_key=True, autoincrement=True)
    username: Optional[str] = Field(default=None, comment="用户名")
    email: str = Field(unique=True, comment="用户邮箱")
    hashed_password: str = Field(default=None, comment="密码")
    fullname: Optional[str] = Field(default=None, comment="全名")
    disabled: Optional[bool] = Field(default=None, comment="是否禁用")
    roles: List["Role"] = Relationship(back_populates="users", link_model=UserRoleLink)

class Role(SQLModel, table=True):
    __tablename__ = 'roles'

    id: int = Field(primary_key=True, autoincrement=True)
    name: str = Field(unique=True, comment="角色")
    users: List[User] = Relationship(back_populates="roles", link_model=UserRoleLink)
    permissions: List["Permission"] = Relationship(back_populates="role")

class Permission(SQLModel, table=True):
    __tablename__ = 'permissions'

    id: int = Field(primary_key=True, autoincrement=True)
    name: str = Field(unique=True, comment="权限")
    role: Optional[Role] = Relationship(back_populates="permissions")

class UserRoleLink(SQLModel, table=True):
    user_id: Optional[str] = Field(default=None, foreign_key="users.id", primary_key=True)
    role_id: Optional[str] = Field(default=None, foreign_key="roles.id", primary_key=True)