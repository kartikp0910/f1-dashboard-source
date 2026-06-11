"""Health check routes"""
from fastapi import APIRouter
from app.models import HealthCheckResponse

router = APIRouter()


@router.get("/healthz", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return HealthCheckResponse(status="ok")
