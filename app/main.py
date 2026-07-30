from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import health, chat, ingest, usage, documents, config

app = FastAPI(title="Answer.ly API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "null",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(ingest.router)
app.include_router(documents.router)
app.include_router(usage.router)
app.include_router(config.router)