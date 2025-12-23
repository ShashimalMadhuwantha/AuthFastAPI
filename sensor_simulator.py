"""
IoT Sensor Data Simulator

This script simulates multiple IoT devices (LR1, LR2) sending sensor data via MQTT.
It implements:
- MQTT Birth messages (device comes online)
- MQTT Last Will Testament (LWT) for offline detection
- Periodic sensor data publishing (CT1, CT2, IR, K-Type temperature)
"""

import paho.mqtt.client as mqtt
import time
import random
import json
import os
from datetime import datetime

# Configuration from environment variables
MQTT_BROKER = os.getenv("MQTT_BROKER", "broker.hivemq.com")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC_PREFIX = os.getenv("MQTT_TOPIC_PREFIX", "sensegrid")

# Device configurations
DEVICES = [
    {
        "device_id": "LR1",
        "name": "Living Room Sensor 1",
        "sensors": {
            "CT1": {"min": 0, "max": 5, "unit": "A"},
            "CT2": {"min": 0, "max": 5, "unit": "A"},
            "IR": {"min": 20, "max": 30, "unit": "°C"},
            "K-Type": {"min": 90, "max": 110, "unit": "°C"}
        }
    },
    {
        "device_id": "LR2",
        "name": "Living Room Sensor 2",
        "sensors": {
            "CT1": {"min": 0, "max": 3, "unit": "A"},
            "CT2": {"min": 0, "max": 3, "unit": "A"},
            "IR": {"min": 0, "max": 10, "unit": "°C"},
            "K-Type": {"min": 0, "max": 10, "unit": "°C"}
        }
    }
]

class SensorSimulator:
    def __init__(self, device_config):
        self.device_id = device_config["device_id"]
        self.name = device_config["name"]
        self.sensors = device_config["sensors"]
        self.client = None
        self.running = False
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"[{self.device_id}] Connected to MQTT broker")
            # Send Birth message
            self.send_birth_message()
        else:
            print(f"[{self.device_id}] Failed to connect, return code {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        print(f"[{self.device_id}] Disconnected from MQTT broker")
    
    def send_birth_message(self):
        """Send Birth message to indicate device is online"""
        topic = f"{MQTT_TOPIC_PREFIX}/{self.device_id}/status"
        self.client.publish(topic, "online", qos=1, retain=True)
        print(f"[{self.device_id}] Sent Birth message: online")
    
    def setup_lwt(self):
        """Set up Last Will Testament for offline detection"""
        topic = f"{MQTT_TOPIC_PREFIX}/{self.device_id}/status"
        self.client.will_set(topic, "offline", qos=1, retain=True)
        print(f"[{self.device_id}] LWT configured")
    
    def generate_sensor_reading(self, sensor_type, config):
        """Generate realistic sensor reading with some variation"""
        # Generate value with slight random variation
        base_value = (config["min"] + config["max"]) / 2
        variation = (config["max"] - config["min"]) * 0.3
        value = base_value + random.uniform(-variation, variation)
        
        # Clamp to min/max
        value = max(config["min"], min(config["max"], value))
        
        return round(value, 2)
    
    def publish_sensor_data(self):
        """Publish sensor readings for all sensors"""
        for sensor_type, config in self.sensors.items():
            value = self.generate_sensor_reading(sensor_type, config)
            
            payload = json.dumps({
                "value": value,
                "unit": config["unit"],
                "timestamp": datetime.utcnow().isoformat() + 'Z'  # Add Z to indicate UTC
            })
            
            topic = f"{MQTT_TOPIC_PREFIX}/{self.device_id}/sensors/{sensor_type}"
            self.client.publish(topic, payload, qos=0)
            print(f"[{self.device_id}] {sensor_type}: {value} {config['unit']}")
    
    def start(self):
        """Start the simulator"""
        self.client = mqtt.Client(client_id=f"{self.device_id}_simulator")
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        
        # Set up Last Will Testament before connecting
        self.setup_lwt()
        
        print(f"[{self.device_id}] Connecting to {MQTT_BROKER}:{MQTT_PORT}...")
        self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
        self.client.loop_start()
        
        self.running = True
    
    def stop(self):
        """Stop the simulator"""
        if self.client:
            # Send offline status before disconnecting
            topic = f"{MQTT_TOPIC_PREFIX}/{self.device_id}/status"
            self.client.publish(topic, "offline", qos=1, retain=True)
            time.sleep(0.5)
            
            self.client.loop_stop()
            self.client.disconnect()
            print(f"[{self.device_id}] Stopped")
        self.running = False

def main():
    print("=" * 60)
    print("IoT Sensor Data Simulator")
    print("=" * 60)
    print(f"MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"Topic Prefix: {MQTT_TOPIC_PREFIX}")
    print(f"Devices: {', '.join([d['device_id'] for d in DEVICES])}")
    print("=" * 60)
    print()
    
    # Wait a bit for backend to be ready (especially in Docker)
    print("Waiting 5 seconds for backend to initialize...")
    time.sleep(5)
    
    # Create simulators for all devices
    simulators = [SensorSimulator(device) for device in DEVICES]
    
    # Start all simulators
    for sim in simulators:
        sim.start()
        time.sleep(1)  # Stagger startup
    
    print("\nAll devices started. Publishing sensor data every 1 second...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            # Publish sensor data for all devices
            for sim in simulators:
                if sim.running:
                    sim.publish_sensor_data()
            
            print(f"--- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            time.sleep(1)  # Publish every 1 second
            
    except KeyboardInterrupt:
        print("\n\nStopping simulators...")
        for sim in simulators:
            sim.stop()
        print("All simulators stopped. Goodbye!")

if __name__ == "__main__":
    main()
