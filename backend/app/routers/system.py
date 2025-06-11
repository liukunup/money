# -*- coding: UTF-8 -*-

from fastapi import APIRouter, Depends
from pydantic.networks import EmailStr

from app.dependencies import get_current_active_superuser
from app.models.response import Response
from app.utils.email import generate_test_email, send_email


router = APIRouter(tags=["system"])


@router.get("/health", summary="健康检查", description="检查系统是否正常运行")
async def health_check() -> Response:
    return Response(code=200, message="success", data={"status": "healthy"})

@router.post(
    "/test-email/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
)
def test_email(email_to: EmailStr) -> Message:
    """
    Test emails.
    """
    email_data = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Response(message="Test email sent")
