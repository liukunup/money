# -*- coding: UTF-8 -*-

from fastapi import APIRouter
from pydantic import BaseModel

from app.dependencies import SessionDep
from app.models.user import User, UserPublic
from app.utils.security import get_password_hash


router = APIRouter(tags=["private"], prefix="/private")


class PrivateUserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    is_verified: bool = False


@router.post("/users", response_model=UserPublic)
def create_user(user_req: PrivateUserCreate, session: SessionDep):
    """
    Create a new user (for testing purposes only)
    """
    user = User(
        email=user_req.email,
        full_name=user_req.full_name,
        hashed_password=get_password_hash(user_req.password),
    )
    session.add(user)
    session.commit()
    return user
