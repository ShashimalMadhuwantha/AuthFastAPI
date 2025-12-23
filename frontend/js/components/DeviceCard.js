// Device Card Component
export class DeviceCard {
    constructor(deviceId, deviceInfo) {
        this.deviceId = deviceId;
        this.deviceInfo = deviceInfo;
    }

    /**
     * Render device card HTML (left side with circle)
     */
    render() {
        const isOnline = this.deviceInfo?.status === 'online';
        const indicatorClass = isOnline ? '' : 'offline';

        return `
            <div class="device-card">
                <div class="device-name">${this.deviceId}</div>
                <div class="device-indicator ${indicatorClass}" id="indicator-${this.deviceId}"></div>
            </div>
        `;
    }

    /**
     * Update device status indicator
     */
    updateStatus(isOnline) {
        const indicator = document.getElementById(`indicator-${this.deviceId}`);
        if (indicator) {
            if (isOnline) {
                indicator.classList.remove('offline');
            } else {
                indicator.classList.add('offline');
            }
        }
    }
}
