# -*- coding: UTF-8 -*-

import os
from typing import Annotated
from fastapi import Depends
from sqlmodel import SQLModel, Session, create_engine

# 从环境变量获取数据库连接信息，默认使用 sqlite3
DB_TYPE = os.getenv('DB_TYPE', 'sqlite')
DB_USERNAME = os.getenv('DB_USERNAME', '')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', '')
DB_NAME = os.getenv('DB_NAME', 'money.db')

# 构建数据库连接 URL
if DB_TYPE == 'sqlite':
    SQLALCHEMY_DATABASE_URL = f"sqlite:///./{DB_NAME}"
elif DB_TYPE == 'mysql':
    SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
else:
    raise ValueError("Unsupported database type")

# 创建数据库引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} if DB_TYPE == 'sqlite' else {}
)

# 创建数据库和表
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# 获取数据库会话
def get_session():
    with Session(engine) as session:
        yield session
# 定义依赖项，用于注入数据库会话
SessionDep = Annotated[Session, Depends(get_session)]
