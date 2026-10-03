"""app/main.py — FastAPI Application Entry Point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import health_router, product_router
from app.cache.redis_client import cache
from app.db.database import init_db

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url=settings.DOCS_URL
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(health_router.router)
app.include_router(product_router.router, prefix=settings.API_V1_STR)


@app.on_event("startup")
def startup():
    print(f"🚀 Starting... Cache: {cache.status}")
    init_db()


@app.get("/")
def root():
    return {
        "message": settings.PROJECT_NAME,
        "cache": cache.status,
        "docs": f"http://localhost:8000{settings.DOCS_URL}"
    }