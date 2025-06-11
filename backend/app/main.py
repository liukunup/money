from fastapi import Depends, FastAPI

from .routers import system, users

app = FastAPI()

app.include_router(users.router)
app.include_router(system.router)

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}
