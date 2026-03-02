from contextlib import asynccontextmanager
from fastapi import FastAPI
import structlog
from config.settings import settings

from api.routers import scores, anomalies, history, export

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up API", version=settings.project_name)
    yield
    logger.info("Shutting down API")

app = FastAPI(title=settings.project_name, lifespan=lifespan)

app.include_router(scores.router, prefix="/api/v1")
app.include_router(anomalies.router, prefix="/api/v1")
app.include_router(history.router, prefix="/api/v1")
app.include_router(export.router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}
