# -*- coding: UTF-8 -*-

from ..response import Response
from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["Health"], summary="健康检查", description="检查系统是否正常运行")
async def health_check() -> Response:
    return Response(code=200, message="success", data={"status": "healthy"})