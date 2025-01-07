from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import JSONResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize application state on startup.
    """
    app.state.boot_time = datetime.utcnow()
    yield

app = FastAPI(
    title="Status Service",
    description="Health check service for joseserver.com",
    version="0.1.0",
    lifespan=lifespan
)

@app.get("/health")
async def health_check() -> JSONResponse:
    """
    Health check endpoint that returns the service status.
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "version": app.version,
            "timestamp": str(app.state.boot_time)
        },
        status_code=200
    )