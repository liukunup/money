# -*- coding: UTF-8 -*-

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, create_engine, select
from app.config import settings
from app.internal import user as user_service
from app.models.user import User, UserCreate


# 创建数据库引擎
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI), connect_args={"check_same_thread": False} if settings.DB_TYPE == 'sqlite' else {})


# 获取数据库会话
def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


# 定义依赖项，用于注入数据库会话
SessionDep = Annotated[Session, Depends(get_db)]


# 初始化数据库
def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = user_service.create_user(session=session, user_create=user_in)
