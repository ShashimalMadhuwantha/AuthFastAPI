import paho.mqtt.client as mqtt
from app.core.config import settings
from app.core.logger import logger
from app.db.database import SessionLocal
from app.services.device_service import DeviceService
from app.services.sensor_service import SensorService
from app.schemas.device import SensorReadingCreate
import json
from typing import Optional

class MQTTService:
    def __init__(self):
        self.client: Optional[mqtt.Client] = None
        self.connected = False
        
    def on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            logger.info("Connected to MQTT broker successfully")
            self.connected = True
            
            # Subscribe to device status topics
            client.subscribe(f"{settings.MQTT_TOPIC_PREFIX}/+/status")
            client.subscribe(f"{settings.MQTT_TOPIC_PREFIX}/+/sensors/#")
            logger.info(f"Subscribed to topics: {settings.MQTT_TOPIC_PREFIX}/+/status and sensors")
        else:
            logger.error(f"Failed to connect to MQTT broker, return code {rc}")
            self.connected = False
    
    def on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker"""
        logger.warning(f"Disconnected from MQTT broker with code {rc}")
        self.connected = False
    
    def on_message(self, client, userdata, msg):
        """Callback when a message is received"""
        try:
            # Ignore retained messages (old messages from previous sessions)
            # Only process fresh messages from active simulators
            if msg.retain:
                logger.debug(f"Ignoring retained message on topic {msg.topic}")
                return
            
            topic = msg.topic
            payload = msg.payload.decode()
            logger.info(f"Received message on topic {topic}: {payload}")
            
            # Parse topic: sensegrid/DEVICE_ID/status or sensegrid/DEVICE_ID/sensors/SENSOR_TYPE
            parts = topic.split('/')
            if len(parts) < 3:
                return
            
            device_id = parts[1]
            
            # Handle status messages (Birth/LWT)
            if parts[2] == "status":
                self._handle_status_message(device_id, payload)
            
            # Handle sensor data
            elif parts[2] == "sensors" and len(parts) >= 4:
                sensor_type = parts[3]
                self._handle_sensor_message(device_id, sensor_type, payload)
                
        except Exception as e:
            logger.error(f"Error processing MQTT message: {str(e)}")
    
    def _handle_status_message(self, device_id: str, payload: str):
        """Handle device status messages (online/offline)"""
        try:
            db = SessionLocal()
            try:
                status = payload.lower()
                if status in ["online", "offline"]:
                    try:
                        # Try to update existing device
                        DeviceService.update_device_status(db, device_id, status)
                        logger.info(f"Device {device_id} status updated to {status}")
                    except Exception as e:
                        # If device doesn't exist and status is online (Birth message), create it
                        if status == "online" and "not found" in str(e).lower():
                            from app.schemas.device import DeviceCreate
                            logger.info(f"Device {device_id} not found, creating new device")
                            new_device = DeviceCreate(
                                device_id=device_id,
                                name=f"Device {device_id}",
                                device_type="sensor_node"
                            )
                            DeviceService.create_device(db, new_device)
                            DeviceService.update_device_status(db, device_id, status)
                            logger.info(f"Device {device_id} created and set to {status}")
                        elif status == "offline" and "not found" in str(e).lower():
                            # Silently ignore offline messages for non-existent devices
                            # This happens when retained offline messages are received before device is created
                            logger.debug(f"Ignoring offline message for non-existent device {device_id}")
                        else:
                            raise e
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error handling status message for {device_id}: {str(e)}")

    
    def _handle_sensor_message(self, device_id: str, sensor_type: str, payload: str):
        """Handle sensor data messages"""
        try:
            db = SessionLocal()
            try:
                # Parse JSON payload
                data = json.loads(payload)
                value = float(data.get('value', 0))
                unit = data.get('unit', None)
                
                reading = SensorReadingCreate(
                    sensor_type=sensor_type,
                    value=value,
                    unit=unit
                )
                
                SensorService.create_sensor_reading(db, device_id, reading)
                logger.info(f"Stored sensor reading: {device_id}/{sensor_type} = {value} {unit}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error handling sensor message for {device_id}/{sensor_type}: {str(e)}")
    
    def start(self):
        """Start MQTT client"""
        try:
            self.client = mqtt.Client()
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_message = self.on_message
            
            logger.info(f"Connecting to MQTT broker at {settings.MQTT_BROKER}:{settings.MQTT_PORT}")
            self.client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, 60)
            self.client.loop_start()
            
        except Exception as e:
            logger.error(f"Error starting MQTT client: {str(e)}")
    
    def stop(self):
        """Stop MQTT client"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("MQTT client stopped")
    
    def publish(self, topic: str, payload: str):
        """Publish a message to MQTT broker"""
        if self.client and self.connected:
            self.client.publish(topic, payload)
            logger.info(f"Published to {topic}: {payload}")
        else:
            logger.warning("Cannot publish: MQTT client not connected")

# Global MQTT service instance
mqtt_service = MQTTService()
