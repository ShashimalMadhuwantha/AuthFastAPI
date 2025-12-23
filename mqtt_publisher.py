# IMPORTS 
import os       
import json
import time
import random
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

# Load .env file, reads values from a .env file (MQTT Config part)
load_dotenv()

# MQTT Configuration:
MQTT_BROKER       = os.getenv("MQTT_BROKER", "broker.hivemq.com") #connected to public mqtt server
MQTT_PORT         = int(os.getenv("MQTT_PORT", 1883)) 
MQTT_TOPIC_PREFIX = os.getenv("MQTT_TOPIC_PREFIX", "sensegrid")

# One machine:
DEVICE_ID = "C27_01"

# Formats the topics sent 
STATUS_TOPIC = f"{MQTT_TOPIC_PREFIX}/{DEVICE_ID}/status"
DATA_TOPIC   = f"{MQTT_TOPIC_PREFIX}/{DEVICE_ID}/data"

MAX_RETRIES = 5
RETRY_DELAY = 5

connected = False

# MQTT Callbacks 
def on_connect(client, userdata, flags, rc, properties = None):
    global connected 
    if rc == 0:
        connected = True 
        print("Connected to HiveMQ broker")
    
        client.publish(STATUS_TOPIC, "online", qos = 1, retain = True )
        print("Birth message sent: Online")

    else:
        print(f"Connection failed with code {rc}")

# Create MQTT Client 
def create_mqtt_client():
    client = mqtt.Client(
        client_id = DEVICE_ID, callback_api_version = mqtt.CallbackAPIVersion.VERSION2
    )

    # Last Will & Testament
    client.will_set(
        STATUS_TOPIC,
        payload = "offline",
        qos = 1,
        retain = True
    )

    client.on_connect = on_connect 
    return client

def connect_with_retry(client):
    global connected 
    client.loop_start()

    attempt = 0 
    while not connected and attempt < MAX_RETRIES:
        try: 
            attempt += 1
            print(f"Attempt {attempt} to connect to HiveMQ...")
            client.connect(MQTT_BROKER, MQTT_PORT, keepalive = 60)
            time.sleep(3)
        except Exception as e:
            print(f"Connection error: {e}")
        
        if not connected:
            print(f"Retrying in {RETRY_DELAY} seconds...\n")
            time.sleep(RETRY_DELAY)

    if not connected:
        print("Failed to connect after multiple attempts. Exiting.")
        client.loop_stop()
        exit(1)

# Publish random machine data
def publish_data(client):
    try:
        while True:
            payload = {
                "machine_id": DEVICE_ID,
                "production_count": random.randint(1000, 5000),
                "oee": round(random.uniform(70, 95), 2),
                "downtime_reason": random.choice([
                    "None", 
                    "Electrical", 
                    "Mechanical", 
                    "Material Jam"
                ]),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # converts python to json string, publisher sends data
            client.publish(DATA_TOPIC, json.dumps(payload), qos = 1) 

            print("Data sent:", payload)

            time.sleep(5) # delay to publish every 5 seconds 

    except KeyboardInterrupt:
        print("\nPublisher stopped")
        client.disconnect()
        client.loop_stop()

def main():
    client = create_mqtt_client()
    connect_with_retry(client)
    publish_data(client)

if __name__ == "__main__":
    main()
