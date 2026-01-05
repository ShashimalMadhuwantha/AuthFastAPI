"""
Data Retention Service
Handles data retention logic and database cleanup operations
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.models.sensor import SensorReading
from app.core.logger import logger


class RetentionService:
    """Service for managing data retention and cleanup"""
    
    @staticmethod
    def get_database_stats(db: Session) -> dict:
        """Get database statistics"""
        try:
            total = db.query(SensorReading).count()
            
            if total == 0:
                return {
                    "total_readings": 0,
                    "oldest_date": None,
                    "newest_date": None,
                    "data_age_days": 0
                }
            
            oldest = db.query(SensorReading.timestamp).order_by(
                SensorReading.timestamp.asc()
            ).first()[0]
            
            newest = db.query(SensorReading.timestamp).order_by(
                SensorReading.timestamp.desc()
            ).first()[0]
            
            age_days = (newest - oldest).days if oldest and newest else 0
            
            return {
                "total_readings": total,
                "oldest_date": oldest.isoformat(),
                "newest_date": newest.isoformat(),
                "data_age_days": age_days
            }
            
        except Exception as e:
            logger.error(f"[RetentionService] Error getting stats: {str(e)}")
            raise
    
    @staticmethod
    def cleanup_old_data(db: Session, days: int) -> dict:
        """Delete sensor readings older than specified days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Count records to delete
            count = db.query(SensorReading).filter(
                SensorReading.timestamp < cutoff_date
            ).count()
            
            if count == 0:
                return {
                    "success": True,
                    "message": f"No data older than {days} days",
                    "deleted": 0
                }
            
            # Delete old records
            db.query(SensorReading).filter(
                SensorReading.timestamp < cutoff_date
            ).delete()
            
            db.commit()
            
            logger.info(f"[RetentionService] Deleted {count} records older than {days} days")
            
            return {
                "success": True,
                "message": f"Deleted {count} old records",
                "deleted": count,
                "cutoff_date": cutoff_date.isoformat()
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"[RetentionService] Error during cleanup: {str(e)}")
            raise
