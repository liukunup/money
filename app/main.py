from fastapi import FastAPI
from app.core.config import settings
from app.api import users, categories

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])

@app.get("/")
async def root():
    return {"message": "Money API", "version": settings.APP_VERSION}
