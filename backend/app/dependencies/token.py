# -*- coding: UTF-8 -*-

from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from ..config import settings

# OAuth2
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/token"
)

TokenDep = Annotated[str, Depends(reusable_oauth2)]
