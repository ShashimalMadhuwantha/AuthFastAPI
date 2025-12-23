// MQTT Dashboard - Direct MQTT Connection
// Configuration
const MQTT_CONFIG = {
    BROKER: 'wss://broker.hivemq.com:8884/mqtt', // WebSocket URL for browser
    TOPIC_PREFIX: 'sensegrid',
    DEVICES: ['LR1', 'LR2'],
    SENSOR_TYPES: ['CT1', 'CT2', 'IR', 'K-Type']
};

// Device data storage
const devicesData = {
    LR1: {
        status: 'offline',
        sensors: {
            'CT1': { values: [], latest: null, min: Infinity, max: -Infinity, sum: 0, count: 0 },
            'CT2': { values: [], latest: null, min: Infinity, max: -Infinity, sum: 0, count: 0 },
            'IR': { values: [], latest: null, min: Infinity, max: -Infinity, sum: 0, count: 0 },
            'K-Type': { values: [], latest: null, min: Infinity, max: -Infinity, sum: 0, count: 0 }
        }
    },
    LR2: {
        status: 'offline',
        sensors: {
            'CT1': { values: [], latest: null, min: Infinity, max: -Infinity, sum: 0, count: 0 },
            'CT2': { values: [], latest: null, min: Infinity, max: -Infinity, sum: 0, count: 0 },
            'IR': { values: [], latest: null, min: Infinity, max: -Infinity, sum: 0, count: 0 },
            'K-Type': { values: [], latest: null, min: Infinity, max: -Infinity, sum: 0, count: 0 }
        }
    }
};

// Charts storage
const charts = {};

// MQTT Client
let mqttClient = null;

// Initialize MQTT Connection
function initMQTT() {
    console.log('🔌 Connecting to MQTT broker:', MQTT_CONFIG.BROKER);

    mqttClient = mqtt.connect(MQTT_CONFIG.BROKER, {
        clientId: 'mqtt_dashboard_' + Math.random().toString(16).substr(2, 8),
        clean: true,
        reconnectPeriod: 5000
    });

    mqttClient.on('connect', () => {
        console.log('✅ Connected to MQTT broker');
        updateConnectionStatus('connected');

        // Subscribe to all device topics
        MQTT_CONFIG.DEVICES.forEach(deviceId => {
            const statusTopic = `${MQTT_CONFIG.TOPIC_PREFIX}/${deviceId}/status`;
            const sensorsTopic = `${MQTT_CONFIG.TOPIC_PREFIX}/${deviceId}/sensors/#`;

            mqttClient.subscribe(statusTopic, (err) => {
                if (!err) console.log(`📡 Subscribed to ${statusTopic}`);
            });

            mqttClient.subscribe(sensorsTopic, (err) => {
                if (!err) console.log(`📡 Subscribed to ${sensorsTopic}`);
            });
        });

        // Initial render
        renderDashboard();
    });

    mqttClient.on('message', (topic, message) => {
        handleMQTTMessage(topic, message.toString());
    });

    mqttClient.on('error', (error) => {
        console.error('❌ MQTT Error:', error);
        updateConnectionStatus('disconnected');
    });

    mqttClient.on('offline', () => {
        console.log('📴 MQTT Offline');
        updateConnectionStatus('disconnected');
    });

    mqttClient.on('reconnect', () => {
        console.log('🔄 Reconnecting to MQTT...');
        updateConnectionStatus('connecting');
    });
}

// Handle MQTT Messages
function handleMQTTMessage(topic, payload) {
    const parts = topic.split('/');
    if (parts.length < 3) return;

    const deviceId = parts[1];
    const messageType = parts[2];

    if (!devicesData[deviceId]) return;

    if (messageType === 'status') {
        // Device status message
        devicesData[deviceId].status = payload.toLowerCase();
        updateDeviceStatus(deviceId, payload.toLowerCase());
        console.log(`📊 ${deviceId} status: ${payload}`);
    } else if (messageType === 'sensors' && parts.length >= 4) {
        // Sensor data message
        const sensorType = parts[3];
        try {
            const data = JSON.parse(payload);
            updateSensorData(deviceId, sensorType, data);
        } catch (e) {
            console.error('Failed to parse sensor data:', e);
        }
    }
}

// Update sensor data
function updateSensorData(deviceId, sensorType, data) {
    const sensor = devicesData[deviceId].sensors[sensorType];
    if (!sensor) return;

    const value = parseFloat(data.value);
    const timestamp = new Date(data.timestamp || new Date());

    // Update latest
    sensor.latest = { value, unit: data.unit, timestamp };

    // Update stats
    sensor.min = Math.min(sensor.min, value);
    sensor.max = Math.max(sensor.max, value);
    sensor.sum += value;
    sensor.count++;

    // Store for chart (keep last 50 points)
    sensor.values.push({ value, timestamp });
    if (sensor.values.length > 50) {
        sensor.values.shift();
    }

    // Update UI
    updateSensorUI(deviceId, sensorType);

    console.log(`📈 ${deviceId}/${sensorType}: ${value} ${data.unit}`);
}

// Update connection status indicator
function updateConnectionStatus(status) {
    const statusEl = document.getElementById('connectionStatus');
    statusEl.className = `connection-status ${status}`;

    const statusText = {
        'connected': '🟢 Connected to MQTT',
        'disconnected': '🔴 Disconnected',
        'connecting': '🟡 Connecting...'
    };

    statusEl.textContent = statusText[status] || status;
}

// Render dashboard
function renderDashboard() {
    const container = document.getElementById('devices-container');

    const html = MQTT_CONFIG.DEVICES.map(deviceId => {
        const device = devicesData[deviceId];
        const isOnline = device.status === 'online';
        const indicatorClass = isOnline ? '' : 'offline';

        const sensorCards = MQTT_CONFIG.SENSOR_TYPES.map(sensorType => {
            const sensor = device.sensors[sensorType];
            const icon = getSensorIcon(sensorType);
            const value = sensor.latest ? sensor.latest.value.toFixed(0) : '--';
            const unit = sensor.latest ? sensor.latest.unit : '';
            const minValue = sensor.min !== Infinity ? sensor.min.toFixed(0) : '--';
            const maxValue = sensor.max !== -Infinity ? sensor.max.toFixed(0) : '--';
            const deviceNum = deviceId.replace('LR', 'D0');

            return `
                <div class="sensor-card">
                    <div class="sensor-header">
                        <div class="sensor-icon">${icon}</div>
                        <div class="sensor-title">
                            <h3>${sensorType}</h3>
                        </div>
                    </div>
                    <div class="sensor-subtitle">Current month so far</div>
                    <div class="sensor-id">${deviceNum}</div>
                    
                    <div class="sensor-value-container">
                        <span class="sensor-value" id="value-${deviceId}-${sensorType}">${value}</span>
                        <span class="sensor-unit">${unit}</span>
                        <div class="stat-right-inline">
                            <div class="stat-max">
                                <span class="stat-value-max" id="max-${deviceId}-${sensorType}">${maxValue}</span>
                                <span class="stat-label-small">MAX</span>
                            </div>
                            <div class="stat-min">
                                <span class="stat-value-min" id="min-${deviceId}-${sensorType}">${minValue}</span>
                                <span class="stat-label-small">MIN</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="sensor-chart">
                        <canvas id="chart-${deviceId}-${sensorType}"></canvas>
                    </div>
                    
                    <div class="sensor-footer" id="footer-${deviceId}-${sensorType}">
                        Last update just now
                    </div>
                </div>
            `;
        }).join('');

        return `
            <div class="device-row">
                <div class="device-card">
                    <div class="device-name">${deviceId}</div>
                    <div class="device-indicator ${indicatorClass}" id="indicator-${deviceId}"></div>
                </div>
                <div class="sensors-grid">
                    ${sensorCards}
                </div>
            </div>
        `;
    }).join('');

    container.innerHTML = html;

    // Initialize charts
    MQTT_CONFIG.DEVICES.forEach(deviceId => {
        MQTT_CONFIG.SENSOR_TYPES.forEach(sensorType => {
            initChart(deviceId, sensorType);
        });
    });
}

// Get sensor icon
function getSensorIcon(type) {
    const icons = {
        'CT1': '⚡',
        'CT2': '⚡',
        'IR': '🌡️',
        'K-Type': '🌡️'
    };
    return icons[type] || '📊';
}

// Initialize chart
function initChart(deviceId, sensorType) {
    const canvasId = `chart-${deviceId}-${sensorType}`;
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const chartKey = `${deviceId}-${sensorType}`;

    charts[chartKey] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: sensorType,
                data: [],
                borderColor: 'rgb(59, 130, 246)',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: { display: false },
                y: { beginAtZero: true }
            }
        }
    });
}

// Update sensor UI
function updateSensorUI(deviceId, sensorType) {
    const sensor = devicesData[deviceId].sensors[sensorType];

    // Update value
    const valueEl = document.getElementById(`value-${deviceId}-${sensorType}`);
    if (valueEl && sensor.latest) {
        valueEl.style.opacity = '0.5';
        setTimeout(() => {
            valueEl.textContent = sensor.latest.value.toFixed(0);
            valueEl.style.opacity = '1';
        }, 150);
    }

    // Update stats
    const minEl = document.getElementById(`min-${deviceId}-${sensorType}`);
    const maxEl = document.getElementById(`max-${deviceId}-${sensorType}`);

    if (minEl && sensor.min !== Infinity) {
        minEl.textContent = sensor.min.toFixed(0);
    }
    if (maxEl && sensor.max !== -Infinity) {
        maxEl.textContent = sensor.max.toFixed(0);
    }

    // Update chart
    const chartKey = `${deviceId}-${sensorType}`;
    const chart = charts[chartKey];
    if (chart) {
        chart.data.labels = sensor.values.map(v => v.timestamp);
        chart.data.datasets[0].data = sensor.values.map(v => v.value);
        chart.update('none');
    }

    // Update footer
    const footerEl = document.getElementById(`footer-${deviceId}-${sensorType}`);
    if (footerEl && sensor.latest) {
        footerEl.textContent = `Last update ${getRelativeTime(sensor.latest.timestamp)}`;
    }
}

// Update device status
function updateDeviceStatus(deviceId, status) {
    const indicator = document.getElementById(`indicator-${deviceId}`);
    if (indicator) {
        if (status === 'online') {
            indicator.classList.remove('offline');
        } else {
            indicator.classList.add('offline');
        }
    }
}

// Get relative time
function getRelativeTime(timestamp) {
    const now = new Date();
    const then = new Date(timestamp);
    const seconds = Math.floor((now - then) / 1000);

    if (seconds < 5) return 'just now';
    if (seconds < 60) return `${seconds} seconds ago`;

    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;

    const hours = Math.floor(minutes / 60);
    return `${hours} hour${hours > 1 ? 's' : ''} ago`;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Starting MQTT Dashboard...');
    initMQTT();
});
