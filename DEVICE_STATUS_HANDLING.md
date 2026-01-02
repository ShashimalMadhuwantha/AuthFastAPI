# Device Status Handling (Birth & LWT)

## Overview
The system now properly handles MQTT Birth messages and Last Will Testament (LWT) for real-time device status updates (online/offline) with WebSocket broadcasting.

## How It Works

### 1. Birth Message (Device Comes Online)
```
Simulator starts
    ↓
Sends Birth message: sensegrid/LR1/status = "online"
    ↓
Backend MQTT Service receives
    ↓
Updates database: device.status = "online"
    ↓
Broadcasts via WebSocket: {type: "device_status", device_id: "LR1", status: "online"}
    ↓
Frontend receives and updates indicator: 🟢 Green circle
```

### 2. LWT Message (Device Goes Offline)
```
Simulator stops (Ctrl+C or crashes)
    ↓
MQTT Broker sends LWT: sensegrid/LR1/status = "offline"
    ↓
Backend MQTT Service receives
    ↓
Updates database: device.status = "offline"
    ↓
Broadcasts via WebSocket: {type: "device_status", device_id: "LR1", status: "offline"}
    ↓
Frontend receives and updates indicator: 🔴 Red circle
```

### 3. Auto-Recovery (Sensor Data Arrives While Offline)
```
Device marked as offline in database
    ↓
Sensor data arrives: sensegrid/LR1/sensors/CT1 = 3.45 A
    ↓
Backend detects: device.status == "offline" but receiving data
    ↓
Automatically updates: device.status = "online"
    ↓
Broadcasts via WebSocket: {type: "device_status", device_id: "LR1", status: "online"}
    ↓
Frontend updates indicator: 🔴 → 🟢
```

## Implementation Details

### Backend - MQTT Service

**Birth/LWT Handler:**
```python
def _handle_status_message(self, device_id: str, payload: str):
    status = payload.lower()  # "online" or "offline"
    
    # Update database
    DeviceService.update_device_status(db, device_id, status)
    
    # Broadcast via WebSocket
    websocket_service.broadcast_device_status(device_id, status)
```

**Auto-Recovery Handler:**
```python
def _handle_sensor_message(self, device_id: str, sensor_type: str, payload: str):
    device = DeviceService.get_device_by_device_id(db, device_id)
    
    # If receiving data but marked offline, auto-recover
    if device.status == "offline":
        DeviceService.update_device_status(db, device_id, "online")
        websocket_service.broadcast_device_status(device_id, "online")
```

### Backend - WebSocket Service

```python
async def broadcast_device_status(self, device_id: str, status: str):
    message = {
        "type": "device_status",
        "device_id": device_id,
        "status": status
    }
    
    # Send to all connected clients
    for connection in self.active_connections:
        await connection.send_json(message)
```

### Frontend - WebSocket Handler

```javascript
this.ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'sensor_reading') {
        this.handleWebSocketUpdate(data);
    } else if (data.type === 'device_status') {
        this.handleDeviceStatusUpdate(data);
    }
};
```

**Status Update Handler:**
```javascript
handleDeviceStatusUpdate(data) {
    const { device_id, status } = data;
    const indicator = document.getElementById(`indicator-${device_id}`);
    
    if (status === 'online') {
        indicator.classList.remove('offline');
        console.log(`🟢 Device ${device_id} is now ONLINE`);
    } else {
        indicator.classList.add('offline');
        console.log(`🔴 Device ${device_id} is now OFFLINE`);
    }
}
```

## Simulator Configuration

```python
def setup_lwt(self):
    """Set up Last Will Testament"""
    topic = f"{MQTT_TOPIC_PREFIX}/{self.device_id}/status"
    self.client.will_set(topic, "offline", qos=1, retain=True)

def send_birth_message(self):
    """Send Birth message"""
    topic = f"{MQTT_TOPIC_PREFIX}/{self.device_id}/status"
    self.client.publish(topic, "online", qos=1, retain=True)
```

## Testing

### Test 1: Normal Start/Stop
1. Start simulator: `python sensor_simulator.py`
   - ✅ Device indicator turns green (Birth message)
2. Stop simulator: `Ctrl+C`
   - ✅ Device indicator turns red (LWT message)

### Test 2: Auto-Recovery
1. Stop backend while simulator is running
2. Restart backend
   - Device shows as offline (no Birth message received)
3. Wait for sensor data to arrive
   - ✅ Device automatically goes online (auto-recovery)

### Test 3: Crash Simulation
1. Kill simulator process forcefully
   - ✅ LWT triggers, device goes offline

## Console Messages

### Backend:
```
Device LR1 status updated to online
Broadcasted device status: LR1 = online
```

### Frontend:
```
🟢 Device LR1 is now ONLINE
🔴 Device LR2 is now OFFLINE
```

## Benefits

✅ **Real-time Status** - Instant online/offline updates via WebSocket  
✅ **Automatic Recovery** - Devices auto-recover when data arrives  
✅ **Crash Detection** - LWT detects unexpected disconnections  
✅ **No Polling** - Status updates pushed via WebSocket  
✅ **Visual Feedback** - Clear green/red indicators  

## Future Enhancements

- Add "last seen" timestamp
- Add connection quality indicator
- Add device reconnection notifications
- Add status history/logs
