// Main Dashboard Controller
import { DevicesAPI } from './devices-api.js';
import { DeviceCard } from './components/DeviceCard.js';
import { SensorCard } from './components/SensorCard.js';

// Configuration
const CONFIG = {
    SENSOR_TYPES: ['CT1', 'CT2', 'IR', 'K-Type'],
    UPDATE_INTERVAL: 5000, // 5 seconds
    TIMESTAMP_INTERVAL: 1000 // 1 second
};

class DevicesDashboard {
    constructor() {
        this.updateInterval = null;
        this.timestampInterval = null;
        this.charts = {};
        this.timePeriodHours = parseFloat(localStorage.getItem('timePeriod')) || 24; // Load from localStorage or default 24 hours
        this.refreshIntervalSeconds = parseInt(localStorage.getItem('refreshInterval')) || 5; // Load from localStorage or default 5 seconds
        this.customDateRange = null; // Will store {startDate, endDate} if custom range is set
    }

    /**
     * Initialize the dashboard
     */
    async init() {
        console.log('🚀 Initializing Devices Dashboard...');
        this.setupTimePeriodSelector();
        this.setupEventListeners(); // Listen for modal events
        await this.loadAllDevices();
        this.startAutoUpdate();
        this.startTimestampRefresh();
        console.log('✅ Dashboard initialized');
        console.log(`⏱️ Refresh interval: ${this.refreshIntervalSeconds} seconds`);
        console.log(`📅 Time period: ${this.timePeriodHours} hours`);
    }

    /**
     * Setup event listeners for modal settings
     */
    setupEventListeners() {
        // Listen for refresh interval changes from modal
        window.addEventListener('refreshIntervalChanged', (e) => {
            const newInterval = e.detail.interval;
            console.log(`🔄 Refresh interval changed to ${newInterval} seconds`);
            this.refreshIntervalSeconds = newInterval;
            this.restartAutoUpdate();
        });

        // Listen for time period changes from modal (deprecated, keeping for backward compatibility)
        window.addEventListener('timePeriodChanged', async (e) => {
            const newPeriod = e.detail.hours;
            console.log(`📅 Time period changed to ${newPeriod} hours`);
            this.timePeriodHours = newPeriod;
            this.customDateRange = null; // Clear custom range
            await this.refreshAllData();
        });

        // Listen for custom date range changes from modal
        window.addEventListener('dateRangeChanged', async (e) => {
            const { startDate, endDate } = e.detail;
            console.log(`📅 Custom date range set: ${startDate} to ${endDate}`);
            this.customDateRange = { startDate, endDate };
            await this.refreshAllData();
        });
    }

    /**
     * Setup time period selector
     */
    setupTimePeriodSelector() {
        const selector = document.getElementById('timePeriodSelector');
        if (selector) {
            // Set initial value from localStorage
            selector.value = this.timePeriodHours;

            selector.addEventListener('change', async (e) => {
                this.timePeriodHours = parseFloat(e.target.value);
                console.log(`⏱️ Time period changed to ${this.timePeriodHours} hours`);
                await this.refreshAllData();
            });
        }
    }

    /**
     * Refresh all data with new time period
     */
    async refreshAllData() {
        console.log('🔄 Refreshing all data...');
        await this.loadAllDevices();
    }

    /**
     * Load all devices and sensors
     */
    async loadAllDevices() {
        const container = document.getElementById('devices-container');
        container.innerHTML = '<div class="text-center py-8"><div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div><p class="mt-2 text-gray-600 dark:text-gray-400">Loading devices...</p></div>';

        try {
            // Fetch all devices
            const devices = await DevicesAPI.getAllDevices();

            if (!devices || devices.length === 0) {
                container.innerHTML = '<div class="text-center py-8 text-gray-600 dark:text-gray-400">No devices found</div>';
                return;
            }

            // Determine time range parameter
            const timeParam = this.customDateRange || this.timePeriodHours;

            // Fetch data for each device
            const devicesData = await Promise.all(
                devices.map(device =>
                    DevicesAPI.getDeviceData(device.device_id, CONFIG.SENSOR_TYPES, timeParam)
                )
            );

            // Render all devices
            const validDevices = devicesData.filter(data => data !== null && data.sensors.length > 0);

            if (validDevices.length === 0) {
                container.innerHTML = `
                    <div class="text-center py-12">
                        <div class="text-6xl mb-4">📊</div>
                        <h3 class="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-2">No Data Available</h3>
                        <p class="text-gray-600 dark:text-gray-400">
                            No sensor data found for the selected date range.<br>
                            Try selecting a different time period or check if sensors are publishing data.
                        </p>
                    </div>
                `;
                return;
            }

            container.innerHTML = validDevices
                .map(deviceData => this.renderDevice(deviceData))
                .join('');

            // Initialize all charts
            validDevices.forEach(deviceData => {
                deviceData.sensors.forEach(({ type, timeseries }) => {
                    this.initChart(deviceData.deviceId, type, timeseries);
                });
            });

            console.log('✅ All devices loaded successfully');
        } catch (error) {
            console.error('❌ Error loading devices:', error);
            container.innerHTML = '<div class="text-center py-8 text-red-600 dark:text-red-400">Error loading devices. Please check console for details.</div>';
        }
    }

    /**
     * Render a single device section
     */
    renderDevice(deviceData) {
        const { deviceId, deviceInfo, sensors } = deviceData;

        const deviceCard = new DeviceCard(deviceId, deviceInfo);
        const deviceCardHtml = deviceCard.render();

        const sensorCards = sensors
            .map(({ type, latest, stats }) => {
                const sensorCard = new SensorCard(deviceId, type, latest, stats);
                return sensorCard.render();
            })
            .join('');

        return `
            <div class="device-row">
                ${deviceCardHtml}
                <div class="sensors-grid">
                    ${sensorCards}
                </div>
            </div>
        `;
    }

    /**
     * Initialize a chart for a sensor
     */
    initChart(deviceId, sensorType, timeseries) {
        const canvasId = `chart-${deviceId}-${sensorType}`;
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const chartKey = `${deviceId}-${sensorType}`;

        // Destroy existing chart if any
        if (this.charts[chartKey]) {
            this.charts[chartKey].destroy();
        }

        // Prepare data
        const data = timeseries?.data || [];
        const labels = data.map(point => new Date(point.timestamp));
        const values = data.map(point => point.value);

        // Create chart
        this.charts[chartKey] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: sensorType,
                    data: values,
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
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'minute',
                            displayFormats: {
                                minute: 'HH:mm',
                                hour: 'HH:mm'
                            }
                        },
                        adapters: {
                            date: {
                                zone: 'UTC'
                            }
                        },
                        ticks: {
                            source: 'auto'
                        },
                        display: false
                    },
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    /**
     * Update all values without page refresh (optimized - only fetches latest values)
     */
    async updateValues() {
        console.log('🔄 Updating values...');

        try {
            const devices = await DevicesAPI.getAllDevices();

            for (const device of devices) {
                const deviceId = device.device_id;

                // Update device status
                try {
                    const deviceInfo = await DevicesAPI.getDevice(deviceId);
                    const deviceCard = new DeviceCard(deviceId, deviceInfo);
                    deviceCard.updateStatus(deviceInfo?.status === 'online');
                } catch (err) {
                    console.error(`Error updating device status for ${deviceId}:`, err);
                }

                // Update sensor values (OPTIMIZED: only fetch latest)
                for (const type of CONFIG.SENSOR_TYPES) {
                    try {
                        // Only fetch latest value (not stats or timeseries)
                        const latest = await DevicesAPI.getLatestReading(deviceId, type);

                        // Update the displayed value
                        const valueEl = document.getElementById(`value-${deviceId}-${type}`);
                        if (valueEl && latest) {
                            valueEl.textContent = latest.value.toFixed(0);
                        }

                        // Update timestamp
                        const footerEl = document.getElementById(`footer-${deviceId}-${type}`);
                        if (footerEl && latest) {
                            footerEl.setAttribute('data-timestamp', latest.timestamp);
                            const sensorCard = new SensorCard('', '', { timestamp: latest.timestamp }, {});
                            footerEl.textContent = `Last update ${sensorCard.getRelativeTime(latest.timestamp)}`;
                        }

                        // Add new point to chart (in memory)
                        if (latest) {
                            this.addPointToChart(deviceId, type, latest.value, latest.timestamp);
                        }

                        // Recalculate and update stats from chart data (in memory)
                        this.updateStatsFromChart(deviceId, type);

                    } catch (err) {
                        console.error(`Error updating ${deviceId}/${type}:`, err);
                    }
                }
            }

            console.log('✅ Values updated');
        } catch (error) {
            console.error('❌ Error updating values:', error);
        }
    }

    /**
     * Add a new data point to an existing chart (in memory)
     */
    addPointToChart(deviceId, sensorType, value, timestamp) {
        const chartKey = `${deviceId}-${sensorType}`;
        const chart = this.charts[chartKey];

        if (!chart) return;

        const newTimestamp = new Date(timestamp);

        // Add new data point
        chart.data.labels.push(newTimestamp);
        chart.data.datasets[0].data.push(value);

        // Keep only last 100 points for performance
        if (chart.data.labels.length > 100) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
        }

        // Update chart (no animation for smooth updates)
        chart.update('none');
    }

    /**
     * Recalculate min/max stats from chart data (in memory)
     */
    updateStatsFromChart(deviceId, sensorType) {
        const chartKey = `${deviceId}-${sensorType}`;
        const chart = this.charts[chartKey];

        if (!chart || chart.data.datasets[0].data.length === 0) return;

        const values = chart.data.datasets[0].data;
        const minValue = Math.min(...values);
        const maxValue = Math.max(...values);

        // Update MIN display
        const minEl = document.getElementById(`min-${deviceId}-${sensorType}`);
        if (minEl) minEl.textContent = minValue.toFixed(0);

        // Update MAX display
        const maxEl = document.getElementById(`max-${deviceId}-${sensorType}`);
        if (maxEl) maxEl.textContent = maxValue.toFixed(0);
    }

    /**
     * Update chart data
     */
    updateChart(deviceId, sensorType, timeseries) {
        const chartKey = `${deviceId}-${sensorType}`;
        const chart = this.charts[chartKey];
        if (!chart || !timeseries) return;

        const data = timeseries.data || [];
        chart.data.labels = data.map(point => new Date(point.timestamp));
        chart.data.datasets[0].data = data.map(point => point.value);
        chart.update('none'); // Update without animation
    }

    /**
     * Start automatic updates
     */
    startAutoUpdate() {
        const intervalMs = this.refreshIntervalSeconds * 1000;
        console.log(`⏰ Auto-update started (every ${this.refreshIntervalSeconds} seconds)`);

        this.updateInterval = setInterval(() => {
            this.updateValues();
        }, intervalMs);
    }

    /**
     * Restart automatic updates with new interval
     */
    restartAutoUpdate() {
        // Clear existing interval
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        // Trigger immediate update
        this.updateValues();
        // Start with new interval
        this.startAutoUpdate();
    }

    /**
     * Refresh all timestamps
     */
    refreshTimestamps() {
        const footers = document.querySelectorAll('[id^="footer-"]');
        footers.forEach(footer => {
            const timestamp = footer.getAttribute('data-timestamp');
            if (timestamp) {
                const sensorCard = new SensorCard('', '', { timestamp }, {});
                const relativeTime = sensorCard.getRelativeTime(timestamp);
                footer.textContent = `Last update ${relativeTime}`;
            }
        });
    }

    /**
     * Start timestamp refresh
     */
    startTimestampRefresh() {
        this.timestampInterval = setInterval(() => {
            this.refreshTimestamps();
        }, CONFIG.TIMESTAMP_INTERVAL);
    }

    /**
     * Stop automatic updates
     */
    stopAutoUpdate() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
        if (this.timestampInterval) {
            clearInterval(this.timestampInterval);
            this.timestampInterval = null;
        }
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const dashboard = new DevicesDashboard();
    dashboard.init();
});

export default DevicesDashboard;
