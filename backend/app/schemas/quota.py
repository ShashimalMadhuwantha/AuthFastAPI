"""
Quota Schemas
Pydantic models for quota-related API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class QuotaStatsResponse(BaseModel):
    """Response model for quota statistics"""
    total_data_points: int = Field(..., description="Total data points in range")
    quota_limit: int = Field(..., description="Configured quota limit")
    quota_exceeded: bool = Field(..., description="Whether quota is exceeded")
    usage_percent: float = Field(..., description="Percentage of quota used")
    remaining_quota: int = Field(..., description="Remaining quota available")
    oldest_timestamp: Optional[str] = Field(None, description="Oldest data point timestamp")
    newest_timestamp: Optional[str] = Field(None, description="Newest data point timestamp")
    date_range_applied: bool = Field(False, description="Whether date range filter was applied")
    start_date: Optional[str] = Field(None, description="Start date if range applied")
    end_date: Optional[str] = Field(None, description="End date if range applied")

    class Config:
        json_schema_extra = {
            "example": {
                "total_data_points": 15000,
                "quota_limit": 25000,
                "quota_exceeded": False,
                "usage_percent": 60.0,
                "remaining_quota": 10000,
                "oldest_timestamp": "2026-01-02T00:00:00",
                "newest_timestamp": "2026-01-09T00:00:00",
                "date_range_applied": True,
                "start_date": "2026-01-02T00:00:00",
                "end_date": "2026-01-09T00:00:00"
            }
        }


class DateRangeQuotaCheckResponse(BaseModel):
    """Response model for date range quota check"""
    would_exceed: bool = Field(..., description="Whether the date range exceeds quota")
    data_points_in_range: int = Field(..., description="Number of data points in the range")
    quota_limit: int = Field(..., description="Current quota limit")
    suggested_quota: int = Field(..., description="Suggested quota to accommodate the range")
    should_limit: bool = Field(..., description="Whether data should be limited")
    limit_to: int = Field(..., description="Number of points to limit to")
    message: str = Field(..., description="Human-readable message")

    class Config:
        json_schema_extra = {
            "example": {
                "would_exceed": True,
                "data_points_in_range": 50000,
                "quota_limit": 25000,
                "suggested_quota": 60000,
                "should_limit": True,
                "limit_to": 25000,
                "message": "Date range contains 50000 data points. Quota limit is 25000."
            }
        }


class QuotaApiResponse(BaseModel):
    """Generic API response wrapper for quota endpoints"""
    status: str = Field(..., description="Response status")
    data: dict = Field(..., description="Response data")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "data": {}
            }
        }
