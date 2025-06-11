from typing import Generic, TypeVar, Optional
from pydantic.generics import GenericModel

T = TypeVar('T')

# Generic response
class Response(GenericModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: Optional[T] = None
