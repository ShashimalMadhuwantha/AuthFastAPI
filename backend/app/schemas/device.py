from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# Device Schemas
class DeviceBase(BaseModel):
    device_id: str
    name: str
    device_type: Optional[str] = None

class DeviceCreate(DeviceBase):
    pass

class DeviceResponse(DeviceBase):
    id: int
    status: str
    last_seen: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z' if v else None
        }

# Sensor Reading Schemas
class SensorReadingCreate(BaseModel):
    sensor_type: str
    value: float
    unit: Optional[str] = None

class SensorReadingResponse(BaseModel):
    id: int
    device_id: int
    sensor_type: str
    value: float
    unit: Optional[str] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z' if v else None
        }

# Statistics Schema
class SensorStats(BaseModel):
    sensor_type: str
    min_value: float
    max_value: float
    avg_value: float
    count: int
    start_time: datetime
    end_time: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z' if v else None
        }

# Time Series Data Point
class TimeSeriesPoint(BaseModel):
    timestamp: datetime
    value: float

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z' if v else None
        }

class TimeSeriesResponse(BaseModel):
    sensor_type: str
    unit: Optional[str] = None
    data: List[TimeSeriesPoint]
