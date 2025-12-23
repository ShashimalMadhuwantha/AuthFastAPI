from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.sensor import Device
from app.schemas.device import DeviceCreate
from datetime import datetime
from app.core.logger import logger

class DeviceService:
    @staticmethod
    def get_all_devices(db: Session):
        """Get all devices"""
        try:
            devices = db.query(Device).all()
            return devices
        except Exception as e:
            logger.error(f"Error getting all devices: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving devices: {str(e)}"
            )
    
    @staticmethod
    def get_device_by_id(db: Session, device_id: int):
        """Get device by database ID"""
        device = db.query(Device).filter(Device.id == device_id).first()
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device with id {device_id} not found"
            )
        return device
    
    @staticmethod
    def get_device_by_device_id(db: Session, device_id: str):
        """Get device by device_id (e.g., 'LR1')"""
        device = db.query(Device).filter(Device.device_id == device_id).first()
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device {device_id} not found"
            )
        return device
    
    @staticmethod
    def create_device(db: Session, device: DeviceCreate):
        """Create a new device"""
        # Check if device already exists
        existing_device = db.query(Device).filter(Device.device_id == device.device_id).first()
        if existing_device:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Device {device.device_id} already exists"
            )
        
        try:
            db_device = Device(
                device_id=device.device_id,
                name=device.name,
                device_type=device.device_type,
                status="offline"
            )
            db.add(db_device)
            db.commit()
            db.refresh(db_device)
            logger.info(f"Created device: {device.device_id}")
            return db_device
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating device: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating device: {str(e)}"
            )
    
    @staticmethod
    def update_device_status(db: Session, device_id: str, status: str):
        """Update device online/offline status"""
        device = DeviceService.get_device_by_device_id(db, device_id)
        try:
            device.status = status
            device.last_seen = datetime.utcnow()
            db.commit()
            db.refresh(device)
            logger.info(f"Updated device {device_id} status to {status}")
            return device
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating device status: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating device status: {str(e)}"
            )
    
    @staticmethod
    def delete_device(db: Session, device_id: int):
        """Delete a device"""
        device = DeviceService.get_device_by_id(db, device_id)
        try:
            db.delete(device)
            db.commit()
            logger.info(f"Deleted device: {device.device_id}")
            return {"message": f"Device {device.device_id} deleted successfully"}
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting device: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting device: {str(e)}"
            )
