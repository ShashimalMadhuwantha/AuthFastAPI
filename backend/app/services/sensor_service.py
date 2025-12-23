from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from fastapi import HTTPException, status
from app.models.sensor import SensorReading, Device
from app.schemas.device import SensorReadingCreate, SensorStats, TimeSeriesPoint, TimeSeriesResponse
from datetime import datetime, timedelta
from typing import Optional
from app.core.logger import logger

class SensorService:
    @staticmethod
    def create_sensor_reading(db: Session, device_id: str, reading: SensorReadingCreate):
        """Store a new sensor reading"""
        # Get device
        device = db.query(Device).filter(Device.device_id == device_id).first()
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device {device_id} not found"
            )
        
        try:
            db_reading = SensorReading(
                device_id=device.id,
                sensor_type=reading.sensor_type,
                value=reading.value,
                unit=reading.unit
            )
            db.add(db_reading)
            db.commit()
            db.refresh(db_reading)
            return db_reading
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating sensor reading: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error storing sensor reading: {str(e)}"
            )
    
    @staticmethod
    def get_latest_reading(db: Session, device_id: str, sensor_type: str):
        """Get the latest sensor reading for a device and sensor type"""
        device = db.query(Device).filter(Device.device_id == device_id).first()
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device {device_id} not found"
            )
        
        reading = db.query(SensorReading).filter(
            and_(
                SensorReading.device_id == device.id,
                SensorReading.sensor_type == sensor_type
            )
        ).order_by(SensorReading.timestamp.desc()).first()
        
        if not reading:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No readings found for {sensor_type} on device {device_id}"
            )
        
        return reading
    
    @staticmethod
    def get_sensor_stats(
        db: Session, 
        device_id: str, 
        sensor_type: str, 
        hours: Optional[int] = 24
    ) -> SensorStats:
        """Get min, max, avg statistics for a sensor over a time period"""
        device = db.query(Device).filter(Device.device_id == device_id).first()
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device {device_id} not found"
            )
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        stats = db.query(
            func.min(SensorReading.value).label('min_value'),
            func.max(SensorReading.value).label('max_value'),
            func.avg(SensorReading.value).label('avg_value'),
            func.count(SensorReading.id).label('count')
        ).filter(
            and_(
                SensorReading.device_id == device.id,
                SensorReading.sensor_type == sensor_type,
                SensorReading.timestamp >= start_time,
                SensorReading.timestamp <= end_time
            )
        ).first()
        
        if stats.count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No readings found for {sensor_type} in the last {hours} hours"
            )
        
        return SensorStats(
            sensor_type=sensor_type,
            min_value=stats.min_value,
            max_value=stats.max_value,
            avg_value=stats.avg_value,
            count=stats.count,
            start_time=start_time,
            end_time=end_time
        )
    
    @staticmethod
    def get_time_series(
        db: Session, 
        device_id: str, 
        sensor_type: str, 
        hours: Optional[int] = 24
    ) -> TimeSeriesResponse:
        """Get time series data for graphing"""
        device = db.query(Device).filter(Device.device_id == device_id).first()
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device {device_id} not found"
            )
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        readings = db.query(SensorReading).filter(
            and_(
                SensorReading.device_id == device.id,
                SensorReading.sensor_type == sensor_type,
                SensorReading.timestamp >= start_time,
                SensorReading.timestamp <= end_time
            )
        ).order_by(SensorReading.timestamp.asc()).all()
        
        if not readings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No readings found for {sensor_type} in the last {hours} hours"
            )
        
        data_points = [
            TimeSeriesPoint(timestamp=reading.timestamp, value=reading.value)
            for reading in readings
        ]
        
        return TimeSeriesResponse(
            sensor_type=sensor_type,
            unit=readings[0].unit if readings else None,
            data=data_points
        )
