from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.schemas.device import (
    DeviceCreate, 
    DeviceResponse, 
    SensorReadingCreate,
    SensorReadingResponse,
    SensorStats,
    TimeSeriesResponse
)
from app.services.device_service import DeviceService
from app.services.sensor_service import SensorService
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


# Device endpoints
@router.get("/", response_model=List[DeviceResponse])
async def get_all_devices(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Get all devices with their current status"""
    logger.info(f"[API] Get all devices request by {current_user}")
    devices = DeviceService.get_all_devices(db)
    return devices

@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: str, 
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Get a specific device by device_id"""
    logger.info(f"[API] Get device {device_id} request by {current_user}")
    device = DeviceService.get_device_by_device_id(db, device_id)
    return device

@router.post("/", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(
    device: DeviceCreate, 
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Create a new device"""
    logger.info(f"[API] Create device request: {device.device_id} by {current_user}")
    new_device = DeviceService.create_device(db, device)
    return new_device

@router.put("/{device_id}/status", response_model=DeviceResponse)
async def update_device_status(
    device_id: str, 
    status: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Update device online/offline status"""
    logger.info(f"[API] Update device {device_id} status to {status} by {current_user}")
    if status not in ["online", "offline"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be 'online' or 'offline'"
        )
    device = DeviceService.update_device_status(db, device_id, status)
    return device

# Sensor endpoints
@router.post("/{device_id}/sensors", response_model=SensorReadingResponse, status_code=status.HTTP_201_CREATED)
async def create_sensor_reading(
    device_id: str,
    reading: SensorReadingCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Store a new sensor reading"""
    logger.info(f"[API] Create sensor reading for {device_id}/{reading.sensor_type} by {current_user}")
    new_reading = SensorService.create_sensor_reading(db, device_id, reading)
    return new_reading

@router.get("/{device_id}/sensors/{sensor_type}/latest", response_model=SensorReadingResponse)
async def get_latest_sensor_reading(
    device_id: str,
    sensor_type: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Get the latest sensor reading for a device and sensor type"""
    logger.info(f"[API] Get latest reading for {device_id}/{sensor_type} by {current_user}")
    reading = SensorService.get_latest_reading(db, device_id, sensor_type)
    return reading

@router.get("/{device_id}/sensors/{sensor_type}/stats", response_model=SensorStats)
async def get_sensor_stats(
    device_id: str,
    sensor_type: str,
    hours: Optional[int] = Query(None, description="Time period in hours"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Get min, max, avg statistics for a sensor over a time period"""
    if start_date and end_date:
        logger.info(f"[API] Get stats for {device_id}/{sensor_type} from {start_date} to {end_date} by {current_user}")
        stats = SensorService.get_sensor_stats_by_date_range(db, device_id, sensor_type, start_date, end_date)
    else:
        hours = hours or 24  # Default to 24 hours if not specified
        logger.info(f"[API] Get stats for {device_id}/{sensor_type} (last {hours} hours) by {current_user}")
        stats = SensorService.get_sensor_stats(db, device_id, sensor_type, hours)
    return stats

@router.get("/{device_id}/sensors/{sensor_type}/timeseries", response_model=TimeSeriesResponse)
async def get_sensor_timeseries(
    device_id: str,
    sensor_type: str,
    hours: Optional[int] = Query(None, description="Time period in hours"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    quota_limit: Optional[int] = Query(None, description="Maximum data points to return (quota limit)"),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Get time series data for graphing with optional quota limiting"""
    if start_date and end_date:
        logger.info(f"[API] Get timeseries for {device_id}/{sensor_type} from {start_date} to {end_date} (quota: {quota_limit}) by {current_user}")
        timeseries = SensorService.get_time_series_by_date_range(db, device_id, sensor_type, start_date, end_date, quota_limit)
    else:
        hours = hours or 24  # Default to 24 hours if not specified
        logger.info(f"[API] Get timeseries for {device_id}/{sensor_type} (last {hours} hours) by {current_user}")
        timeseries = SensorService.get_time_series(db, device_id, sensor_type, hours)
    return timeseries
