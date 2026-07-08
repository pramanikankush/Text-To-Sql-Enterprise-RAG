import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.router import router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.on_event("startup")
def on_startup():
    init_db()
    logging.info("Database initialized.")


@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Text-to-SQL API!",
        "health": "/health",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "ok"}

