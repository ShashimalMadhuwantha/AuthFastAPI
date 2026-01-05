"""
Data Retention API
Endpoints for viewing statistics and cleaning up old data
"""

from fastapi import APIRouter, Depends, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.retention_service import RetentionService
from app.services.auth_service import AuthService
from app.core.logger import logger

router = APIRouter()

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/signin")

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> str:
    return AuthService.get_current_user_from_token(token)


@router.get("/stats")
async def get_stats(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Get database statistics"""
    logger.info(f"[Retention API] Get stats request by {current_user}")
    return RetentionService.get_database_stats(db)


@router.post("/cleanup")
async def cleanup_old_data(
    days: int = Query(default=30, ge=1, le=365, description="Delete data older than this many days"),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Delete sensor readings older than specified days"""
    logger.info(f"[Retention API] Cleanup request by {current_user} for {days} days")
    result = RetentionService.cleanup_old_data(db, days)
    logger.info(f"[Retention API] Cleanup completed by {current_user}: {result.get('deleted', 0)} records deleted")
    return result
