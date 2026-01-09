// API wrapper for device endpoints
import { API_CONFIG, getApiUrl } from './devices-config.js';

// Helper to get auth headers
function getAuthHeaders() {
    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
    return {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };
}

export const DevicesAPI = {
    /**
     * Get all devices
     */
    async getAllDevices() {
        const response = await fetch(getApiUrl('/api/v1/devices/'), {
            headers: getAuthHeaders()
        });
        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = 'index.html';
                return;
            }
            throw new Error('Failed to fetch devices');
        }
        return response.json();
    },

    /**
     * Get specific device
     */
    async getDevice(deviceId) {
        const response = await fetch(getApiUrl(`/api/v1/devices/${deviceId}`), {
            headers: getAuthHeaders()
        });
        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = 'index.html';
                return;
            }
            throw new Error(`Failed to fetch device ${deviceId}`);
        }
        return response.json();
    },

    /**
     * Get latest sensor reading
     */
    async getLatestReading(deviceId, sensorType) {
        const response = await fetch(getApiUrl(`/api/v1/devices/${deviceId}/sensors/${sensorType}/latest`), {
            headers: getAuthHeaders()
        });
        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = 'index.html';
                return;
            }
            throw new Error(`Failed to fetch latest reading for ${deviceId}/${sensorType}`);
        }
        return response.json();
    },

    /**
     * Get sensor statistics
     */
    async getSensorStats(deviceId, sensorType, hoursOrDateRange = 24) {
        let url;
        if (typeof hoursOrDateRange === 'object' && hoursOrDateRange.startDate && hoursOrDateRange.endDate) {
            // Custom date range
            url = getApiUrl(`/api/v1/devices/${deviceId}/sensors/${sensorType}/stats?start_date=${hoursOrDateRange.startDate}&end_date=${hoursOrDateRange.endDate}`);
        } else {
            // Hours-based
            url = getApiUrl(`/api/v1/devices/${deviceId}/sensors/${sensorType}/stats?hours=${hoursOrDateRange}`);
        }
        const response = await fetch(url, {
            headers: getAuthHeaders()
        });
        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = 'index.html';
                return;
            }
            throw new Error(`Failed to fetch stats for ${deviceId}/${sensorType}`);
        }
        return response.json();
    },

    /**
     * Get sensor time series data
     */
    async getTimeSeries(deviceId, sensorType, hoursOrDateRange = 24, quotaLimit = null) {
        let url;
        if (typeof hoursOrDateRange === 'object' && hoursOrDateRange.startDate && hoursOrDateRange.endDate) {
            // Custom date range
            url = getApiUrl(`/api/v1/devices/${deviceId}/sensors/${sensorType}/timeseries?start_date=${hoursOrDateRange.startDate}&end_date=${hoursOrDateRange.endDate}`);
            // Add quota limit if specified
            if (quotaLimit) {
                url += `&quota_limit=${quotaLimit}`;
            }
        } else {
            // Hours-based
            url = getApiUrl(`/api/v1/devices/${deviceId}/sensors/${sensorType}/timeseries?hours=${hoursOrDateRange}`);
        }
        const response = await fetch(url, {
            headers: getAuthHeaders()
        });
        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = 'index.html';
                return;
            }
            throw new Error(`Failed to fetch timeseries for ${deviceId}/${sensorType}`);
        }
        return response.json();
    },

    /**
     * Get all data for a device (device info + all sensors)
     */
    async getDeviceData(deviceId, sensorTypes, hoursOrDateRange = 24) {
        try {
            const deviceInfo = await this.getDevice(deviceId);

            const sensorsData = await Promise.all(
                sensorTypes.map(async (type) => {
                    try {
                        const [latest, stats, timeseries] = await Promise.all([
                            this.getLatestReading(deviceId, type),
                            this.getSensorStats(deviceId, type, hoursOrDateRange),
                            this.getTimeSeries(deviceId, type, hoursOrDateRange)
                        ]);
                        return { type, latest, stats, timeseries };
                    } catch (err) {
                        console.warn(`No data for ${deviceId}/${type}`);
                        return null;
                    }
                })
            );

            return {
                deviceId,
                deviceInfo,
                sensors: sensorsData.filter(s => s !== null)
            };
        } catch (error) {
            console.error(`Error fetching data for ${deviceId}:`, error);
            return null;
        }
    }
};
