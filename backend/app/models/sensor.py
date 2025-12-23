from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, index=True, nullable=False)  # e.g., "LR1", "LR2"
    name = Column(String, nullable=False)
    device_type = Column(String, nullable=True)  # e.g., "sensor_node", "gateway"
    status = Column(String, default="offline")  # "online" or "offline"
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to sensor readings
    sensor_readings = relationship("SensorReading", back_populates="device", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Device(id={self.id}, device_id={self.device_id}, name={self.name}, status={self.status})>"


class SensorReading(Base):
    __tablename__ = "sensor_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    sensor_type = Column(String, nullable=False)  # e.g., "CT1", "CT2", "IR", "K-Type"
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=True)  # e.g., "A", "°C"
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship to device
    device = relationship("Device", back_populates="sensor_readings")
    
    def __repr__(self):
        return f"<SensorReading(id={self.id}, sensor_type={self.sensor_type}, value={self.value}, timestamp={self.timestamp})>"
