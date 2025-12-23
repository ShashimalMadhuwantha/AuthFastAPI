// Sensor Card Component
export class SensorCard {
    constructor(deviceId, sensorType, latest, stats) {
        this.deviceId = deviceId;
        this.sensorType = sensorType;
        this.latest = latest;
        this.stats = stats;
    }

    /**
     * Get sensor icon
     */
    getSensorIcon(type) {
        const icons = {
            'CT1': '⚡',
            'CT2': '⚡',
            'IR': '🌡️',
            'K-Type': '🌡️'
        };
        return icons[type] || '📊';
    }

    /**
     * Get device number (LR1 -> D01, LR2 -> D02)
     */
    getDeviceNumber() {
        const num = this.deviceId.replace('LR', '');
        return `D0${num}`;
    }

    /**
     * Get relative time string
     */
    getRelativeTime(timestamp) {
        if (!timestamp) return 'just now';

        // Add 'Z' if missing for UTC parsing
        let isoTimestamp = timestamp;
        if (!timestamp.endsWith('Z') && !timestamp.includes('+')) {
            isoTimestamp = timestamp + 'Z';
        }

        const now = new Date();
        const then = new Date(isoTimestamp);
        const seconds = Math.floor((now - then) / 1000);

        if (seconds < 5) return 'just now';
        if (seconds < 60) return `${seconds} seconds ago`;

        const minutes = Math.floor(seconds / 60);
        if (minutes < 60) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;

        const hours = Math.floor(minutes / 60);
        if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;

        const days = Math.floor(hours / 24);
        return `${days} day${days > 1 ? 's' : ''} ago`;
    }

    /**
     * Render sensor card HTML - Matching MQTT Design
     */
    render() {
        const icon = this.getSensorIcon(this.sensorType);
        const value = this.latest?.value?.toFixed(0) || '0';
        const unit = this.latest?.unit || '';
        const minValue = this.stats?.min_value?.toFixed(0) || '0';
        const maxValue = this.stats?.max_value?.toFixed(0) || '100';
        const deviceNum = this.getDeviceNumber();
        const relativeTime = this.getRelativeTime(this.latest?.timestamp);

        return `
            <div class="sensor-card">
                <div class="sensor-header">
                    <div class="sensor-icon">${icon}</div>
                    <div class="sensor-title">
                        <h3>${this.sensorType}</h3>
                    </div>
                </div>
                <div class="sensor-subtitle">Current month so far</div>
                <div class="sensor-id">${deviceNum}</div>
                
                <div class="sensor-value-container">
                    <span class="sensor-value" id="value-${this.deviceId}-${this.sensorType}">${value}</span>
                    <span class="sensor-unit">${unit}</span>
                    <div class="stat-right-inline">
                        <div class="stat-max">
                            <span class="stat-value-max" id="max-${this.deviceId}-${this.sensorType}">${maxValue}</span>
                            <span class="stat-label-small">MAX</span>
                        </div>
                        <div class="stat-min">
                            <span class="stat-value-min" id="min-${this.deviceId}-${this.sensorType}">${minValue}</span>
                            <span class="stat-label-small">MIN</span>
                        </div>
                    </div>
                </div>
                
                <div class="sensor-chart">
                    <canvas id="chart-${this.deviceId}-${this.sensorType}"></canvas>
                </div>
                
                <div class="sensor-footer" id="footer-${this.deviceId}-${this.sensorType}" data-timestamp="${this.latest?.timestamp || ''}">
                    Last update ${relativeTime}
                </div>
            </div>
        `;
    }

    /**
     * Update sensor values without re-rendering
     */
    update(latest, stats) {
        const valueEl = document.getElementById(`value-${this.deviceId}-${this.sensorType}`);
        const minEl = document.getElementById(`min-${this.deviceId}-${this.sensorType}`);
        const maxEl = document.getElementById(`max-${this.deviceId}-${this.sensorType}`);
        const footerEl = document.getElementById(`footer-${this.deviceId}-${this.sensorType}`);

        if (valueEl && latest?.value !== undefined) {
            valueEl.style.opacity = '0.5';
            setTimeout(() => {
                valueEl.textContent = latest.value.toFixed(0);
                valueEl.style.opacity = '1';
            }, 150);
        }
        if (minEl && stats?.min_value !== undefined) {
            minEl.textContent = stats.min_value.toFixed(0);
        }
        if (maxEl && stats?.max_value !== undefined) {
            maxEl.textContent = stats.max_value.toFixed(0);
        }
        if (footerEl && latest?.timestamp) {
            footerEl.setAttribute('data-timestamp', latest.timestamp);
            footerEl.textContent = `Last update ${this.getRelativeTime(latest.timestamp)}`;
        }
    }
}
