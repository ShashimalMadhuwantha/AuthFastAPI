"""
Data Quota Service
Manages data point quotas with priority over date-based retention
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.sensor import SensorReading, Device
from app.core.logger import logger
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


class DataQuotaService:
    """
    Quota-based data retention service
    
    Priority: Quota Limit > Date Range
    """
    
    DEFAULT_QUOTA_DPM = 25000  # Data Points per Month
    
    @staticmethod
    def get_total_data_points(db: Session) -> int:
        """Get total number of sensor readings"""
        try:
            count = db.query(func.count(SensorReading.id)).scalar()
            return count or 0
        except Exception as e:
            logger.error(f"[Quota] Error getting total data points: {e}")
            return 0
    
    @staticmethod
    def get_quota_stats(db: Session, quota_limit: int = DEFAULT_QUOTA_DPM) -> Dict:
        """Get quota statistics"""
        try:
            total = DataQuotaService.get_total_data_points(db)
            exceeded, _, _ = DataQuotaService.check_quota_exceeded(db, quota_limit)
            
            oldest = db.query(func.min(SensorReading.timestamp)).scalar()
            newest = db.query(func.max(SensorReading.timestamp)).scalar()
            
            usage_percent = (total / quota_limit * 100) if quota_limit > 0 else 0
            
            return {
                'total_data_points': total,
                'quota_limit': quota_limit,
                'quota_exceeded': exceeded,
                'usage_percent': round(usage_percent, 2),
                'remaining_quota': max(0, quota_limit - total),
                'oldest_timestamp': oldest.isoformat() if oldest else None,
                'newest_timestamp': newest.isoformat() if newest else None
            }
        except Exception as e:
            logger.error(f"[Quota] Error getting stats: {e}")
            return {'error': str(e)}
    
    @staticmethod
    def check_date_range_quota(
        db: Session, 
        start_date: str, 
        end_date: str, 
        quota_limit: int = DEFAULT_QUOTA_DPM
    ) -> Dict:
        """
        Check if a date range would exceed the quota
        
        Args:
            start_date: ISO format start date
            end_date: ISO format end date
            quota_limit: Quota limit to check against
            
        Returns:
            - would_exceed: Whether the date range exceeds quota
            - data_points_in_range: Number of data points in the range
            - quota_limit: The quota limit
            - suggested_quota: Suggested quota to accommodate the range
            - should_limit: Whether to limit/sample data
            - limit_to: How many points to show if limiting
        """
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            
            # Count data points in the date range
            count = db.query(func.count(SensorReading.id)).filter(
                SensorReading.timestamp >= start_dt,
                SensorReading.timestamp <= end_dt
            ).scalar() or 0
            
            would_exceed = count > quota_limit
            
            # Suggest a quota that's 20% higher than the range
            suggested_quota = int(count * 1.2) if would_exceed else quota_limit
            
            return {
                'would_exceed': would_exceed,
                'data_points_in_range': count,
                'quota_limit': quota_limit,
                'suggested_quota': suggested_quota,
                'should_limit': would_exceed,  # Should we limit the data?
                'limit_to': quota_limit if would_exceed else count,  # Limit to quota
                'message': f'Date range contains {count} data points. Quota limit is {quota_limit}.'
            }
            
        except Exception as e:
            logger.error(f"[Quota] Error checking date range: {e}")
            return {'error': str(e)}
    
    @staticmethod
    def get_quota_stats_for_range(
        db: Session,
        start_date: str = None,
        end_date: str = None,
        quota_limit: int = DEFAULT_QUOTA_DPM
    ) -> Dict:
        """
        Get quota statistics for a specific date range
        
        If no date range provided, returns stats for all data
        """
        try:
            # Build query
            query = db.query(func.count(SensorReading.id))
            
            if start_date and end_date:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                query = query.filter(
                    SensorReading.timestamp >= start_dt,
                    SensorReading.timestamp <= end_dt
                )
                
                # Get oldest and newest in range
                oldest = db.query(func.min(SensorReading.timestamp)).filter(
                    SensorReading.timestamp >= start_dt,
                    SensorReading.timestamp <= end_dt
                ).scalar()
                
                newest = db.query(func.max(SensorReading.timestamp)).filter(
                    SensorReading.timestamp >= start_dt,
                    SensorReading.timestamp <= end_dt
                ).scalar()
            else:
                # All data
                oldest = db.query(func.min(SensorReading.timestamp)).scalar()
                newest = db.query(func.max(SensorReading.timestamp)).scalar()
            
            total = query.scalar() or 0
            exceeded = total > quota_limit
            usage_percent = (total / quota_limit * 100) if quota_limit > 0 else 0
            
            return {
                'total_data_points': total,
                'quota_limit': quota_limit,
                'quota_exceeded': exceeded,
                'usage_percent': round(usage_percent, 2),
                'remaining_quota': max(0, quota_limit - total),
                'oldest_timestamp': oldest.isoformat() if oldest else None,
                'newest_timestamp': newest.isoformat() if newest else None,
                'date_range_applied': bool(start_date and end_date),
                'start_date': start_date,
                'end_date': end_date
            }
        except Exception as e:
            logger.error(f"[Quota] Error getting range stats: {e}")
            return {'error': str(e)}
