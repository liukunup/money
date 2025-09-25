# -*- coding: UTF-8 -*-

import uuid
from enum import Enum
from typing import List, Optional

from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship

# Relation table for many-to-many relationship between User and Role
class UserRoleLink(SQLModel, table=True):
    __tablename__ = "userrolelink"

    user_id: uuid.UUID = Field(default=None, foreign_key="user.id", primary_key=True)
    role_id: int       = Field(default=None, foreign_key="role.id", primary_key=True)


# Shared properties
class UserBase(SQLModel):
    username: str = Field(unique=True, index=True, max_length=255)
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    fullname: str | None = Field(default=None, max_length=255)
    is_active: bool = True
    is_superuser: bool = False


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    fullname: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    __tablename__ = "user"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str

    roles: List["Role"] = Relationship(back_populates="users", link_model=UserRoleLink)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


class RoleEnum(str, Enum):
    """ 角色枚举类 """
    ADMIN = "admin"
    GUEST = "guest"
    USER = "user"


class Role(SQLModel, table=True):
    __tablename__ = "role"

    id: int = Field(primary_key=True)
    name: str = Field(unique=True)

    users: List[User] = Relationship(back_populates="roles", link_model=UserRoleLink)
    permissions: List["Permission"] = Relationship(back_populates="role")


class Permission(SQLModel, table=True):
    __tablename__ = "permission"

    id: int = Field(primary_key=True)
    name: str = Field(unique=True)

    role: Optional[Role] = Relationship(back_populates="permissions")
