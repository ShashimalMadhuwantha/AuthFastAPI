"""
MQTT Test Client
Simple script to test MQTT broker connectivity and view messages
"""

import paho.mqtt.client as mqtt
import time

# Configuration
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "sensegrid/#"  # Subscribe to all sensegrid topics

def on_connect(client, userdata, flags, rc):
    """Callback when connected"""
    if rc == 0:
        print("✅ Connected to MQTT broker successfully!")
        print(f"📡 Subscribing to topic: {MQTT_TOPIC}")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"❌ Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    """Callback when message received"""
    print(f"\n📨 Topic: {msg.topic}")
    print(f"📄 Payload: {msg.payload.decode()}")
    print("-" * 60)

def on_disconnect(client, userdata, rc):
    """Callback when disconnected"""
    print(f"⚠️ Disconnected from broker (code: {rc})")

def main():
    print("=" * 60)
    print("MQTT Test Client")
    print("=" * 60)
    print(f"Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"Topic: {MQTT_TOPIC}")
    print("=" * 60)
    print()
    
    # Create client
    client = mqtt.Client(client_id="test_client_" + str(time.time()))
    
    # Set callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    # Connect
    print(f"🔌 Connecting to {MQTT_BROKER}...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    
    # Start loop
    print("👂 Listening for messages... (Press Ctrl+C to stop)\n")
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping client...")
        client.disconnect()
        print("✅ Disconnected. Goodbye!")

if __name__ == "__main__":
    main()
