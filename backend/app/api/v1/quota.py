"""
Data Quota API
Endpoints for managing and monitoring data quotas
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.quota_service import DataQuotaService
from app.services.auth_service import AuthService
from app.schemas.quota import QuotaStatsResponse, DateRangeQuotaCheckResponse, QuotaApiResponse
from app.core.logger import logger
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/signin")

def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    return AuthService.get_current_user_from_token(token)


@router.get("/stats", response_model=QuotaApiResponse)
async def get_quota_stats(
    quota_limit: int = Query(25000, description="Quota limit (default: 25000 DPM)"),
    start_date: str = Query(None, description="Optional start date (ISO format)"),
    end_date: str = Query(None, description="Optional end date (ISO format)"),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get data quota statistics
    
    If start_date and end_date provided, returns stats for that date range only.
    Otherwise, returns stats for all data.
    """
    logger.info(f"[API] Quota stats requested by {current_user} (range: {start_date} to {end_date})")
    
    if start_date and end_date:
        stats = DataQuotaService.get_quota_stats_for_range(db, start_date, end_date, quota_limit)
    else:
        stats = DataQuotaService.get_quota_stats(db, quota_limit)
    
    return {
        "status": "success",
        "data": stats
    }


@router.get("/check-date-range", response_model=QuotaApiResponse)
async def check_date_range_quota(
    start_date: str = Query(..., description="Start date (ISO format)"),
    end_date: str = Query(..., description="End date (ISO format)"),
    quota_limit: int = Query(25000, description="Quota limit (default: 25000 DPM)"),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if a date range would exceed the quota
    
    Returns:
        - would_exceed: Whether the range exceeds quota
        - data_points_in_range: Number of data points in range
        - quota_limit: Current quota limit
        - suggested_quota: Suggested quota if exceeded
        - should_limit: Whether to limit data
        - limit_to: Number of points to limit to
    """
    logger.info(f"[API] Date range quota check by {current_user}: {start_date} to {end_date}")
    result = DataQuotaService.check_date_range_quota(db, start_date, end_date, quota_limit)
    return {
        "status": "success",
        "data": result
    }
