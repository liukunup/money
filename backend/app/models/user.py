# -*- coding: UTF-8 -*-

from gc import enable
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

from enum import Enum

class Role(str, Enum):
    """ 角色枚举类 """
    ADMIN = "admin"
    GUEST = "guest"
    USER = "user"
    
class UserRoleLink(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: Optional[str] = Field(default=None, foreign_key="users.id", primary_key=True)
    role_id: Optional[str] = Field(default=None, foreign_key="roles.id", primary_key=True)

class User(SQLModel, table=True):
    __tablename__ = 'users'

    id: int = Field(primary_key=True)
    username: Optional[str] = Field(default=None)
    email: str = Field(unique=True)
    hashed_password: str = Field(default=None)
    fullname: Optional[str] = Field(default=None)
    is_active: bool = True
    is_superuser: bool = False
    roles: List["Role"] = Relationship(back_populates="users", link_model=UserRoleLink)

class Role(SQLModel, table=True):
    __tablename__ = 'roles'

    id: int = Field(primary_key=True)
    name: str = Field(unique=True)
    users: List[User] = Relationship(back_populates="roles", link_model=UserRoleLink)
    permissions: List["Permission"] = Relationship(back_populates="role")

class Permission(SQLModel, table=True):
    __tablename__ = 'permissions'

    id: int = Field(primary_key=True)
    name: str = Field(unique=True)
    role: Optional[Role] = Relationship(back_populates="permissions")