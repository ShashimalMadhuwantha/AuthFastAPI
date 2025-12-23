"""
Clear retained MQTT messages from the broker
This removes old device status messages so they don't auto-create devices
"""

import paho.mqtt.client as mqtt
import time

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC_PREFIX = "sensegrid"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT broker")
        
        # Clear retained messages for common device IDs
        devices_to_clear = ["C27_01", "LR1", "LR2"]
        
        for device_id in devices_to_clear:
            topic = f"{MQTT_TOPIC_PREFIX}/{device_id}/status"
            # Publish empty message with retain=True to clear retained message
            client.publish(topic, "", qos=1, retain=True)
            print(f"   Cleared retained message for {device_id}")
        
        print("\n✅ All retained messages cleared!")
        print("You can now restart the backend and run the simulator.")
        
        # Disconnect after clearing
        time.sleep(1)
        client.disconnect()
    else:
        print(f"❌ Failed to connect, return code {rc}")

def clear_retained_messages():
    client = mqtt.Client(client_id="cleanup_client")
    client.on_connect = on_connect
    
    print("=" * 60)
    print("MQTT Retained Message Cleanup")
    print("=" * 60)
    print(f"Connecting to {MQTT_BROKER}:{MQTT_PORT}...")
    print()
    
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

if __name__ == "__main__":
    clear_retained_messages()
