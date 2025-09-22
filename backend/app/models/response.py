from typing import TypeVar, Optional
from fastapi.responses import ORJSONResponse

T = TypeVar('T')

class ApiResponse(ORJSONResponse):

    def __init__(self, *, code: int = 200, message: str = "success", data: Optional[T] = None, **kwargs):
        content = {
            "code": code,
            "message": message,
            "data": data,
        }
        super().__init__(content=content, **kwargs)
