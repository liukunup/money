from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from pydantic.networks import EmailStr

from datetime import datetime

from app.dependencies import get_current_active_superuser
from app.utils.email import generate_test_email, send_email


router = APIRouter(tags=["system"])


@router.get("/ready", description="就绪检查", response_class=ORJSONResponse)
async def readiness():
    content={
        "code": 200,
        "message": "ok",
    }
    # 这里可以添加更多的就绪检查逻辑，比如数据库连接检查等
    return ORJSONResponse(content=content)


@router.get("/healthz", description="存活检查", response_class=ORJSONResponse)
async def healthcheck():
    content={
        "code": 200,
        "status": "ok",
        "timestamp": datetime.now(datetime.timezone.utc),
    }
    return ORJSONResponse(content=content)


@router.post(
    "/test-email/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
)
def test_email(email_to: EmailStr):
    """
    Test emails.
    """
    email_data = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    content={"message": "Test email sent"}
    return ORJSONResponse(content=content)
