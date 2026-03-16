from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import users, categories, transactions, budgets, tags, time_periods, recycle_bin, text_parse, ai, imports, files, household, ocr, analytics, anomalies, anomaly_settings

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["transactions"])
app.include_router(budgets.router, prefix="/api/budgets", tags=["budgets"])
app.include_router(tags.router, prefix="/api/tags", tags=["tags"])
app.include_router(time_periods.router, prefix="/api/time-periods", tags=["time-periods"])
app.include_router(recycle_bin.router, prefix="/api/recycle-bin", tags=["recycle-bin"])
app.include_router(text_parse.router, prefix="/api/text-parse", tags=["text-parse"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(imports.router, prefix="/api/imports", tags=["imports"])
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(household.router, prefix="/api/households", tags=["households"])
app.include_router(ocr.router, prefix="/api/ocr", tags=["ocr"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(anomalies.router, prefix="/api", tags=["anomalies"])
app.include_router(anomaly_settings.router, prefix="/api", tags=["settings"])

@app.get("/")
async def root():
    return {"message": "Money API", "version": settings.APP_VERSION}
