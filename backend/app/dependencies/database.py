# -*- coding: UTF-8 -*-

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, create_engine
from ..config import settings


# 创建数据库引擎
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI), connect_args={"check_same_thread": False} if settings.DB_TYPE == 'sqlite' else {})


# 获取数据库会话
def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


# 定义依赖项，用于注入数据库会话
SessionDep = Annotated[Session, Depends(get_db)]
