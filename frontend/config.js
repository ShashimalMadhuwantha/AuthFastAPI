// API Configuration
// ===================
// This is the SINGLE source of truth for API configuration
// Used by both traditional scripts (<script src="config.js">) and ES6 modules
// 
// Files using this config:
// - index.html (traditional script)
// - devices-dashboard.html (traditional script)
// - devices-api.js (ES6 module - uses global API_CONFIG and getApiUrl)
// - devices-app.js (ES6 module - imports from devices-api.js)
//
// Automatically detects environment and sets appropriate API URL

const API_CONFIG = {
    // Detect environment and set base URL
    // In Docker: backend service is accessible at 'backend:8000'
    // In local dev: use localhost
    BASE_URL: (() => {
        const hostname = window.location.hostname;
        const port = window.location.port;

        // Docker environment: frontend on port 3000, backend on port 8000
        // Local dev: frontend on port 8080, backend on port 8000

        // Always use the current hostname with backend port 8000
        // This works for:
        // - Docker: http://localhost:3000 -> http://localhost:8000
        // - Local: http://localhost:8080 -> http://localhost:8000
        // - Production: http://example.com:3000 -> http://example.com:8000

        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return 'http://localhost:8000';
        }

        // Production - use same host
        return `http://${hostname}:8000`;
    })(),

    // API endpoints
    ENDPOINTS: {
        // Auth endpoints
        SIGNIN: '/api/v1/auth/signin',
        SIGNUP: '/api/v1/auth/signup',
        USERS_ME: '/api/v1/auth/users/me',

        // User management endpoints
        USERS_LIST: '/api/v1/users/',
        USERS_CREATE: '/api/v1/users/',
        USERS_GET: '/api/v1/users/{id}',
        USERS_UPDATE: '/api/v1/users/{id}',
        USERS_DELETE: '/api/v1/users/{id}',

        // Device endpoints (used by devices-api.js)
        DEVICES_LIST: '/api/v1/devices/',
        DEVICES_GET: '/api/v1/devices/{device_id}',
        SENSOR_LATEST: '/api/v1/devices/{device_id}/sensors/{sensor_type}/latest',
        SENSOR_STATS: '/api/v1/devices/{device_id}/sensors/{sensor_type}/stats',
        SENSOR_TIMESERIES: '/api/v1/devices/{device_id}/sensors/{sensor_type}/timeseries',
    }
};

// Helper function to get full API URL
// Supports both path parameters ({id}) and query parameters (?hours=6)
function getApiUrl(endpoint, params = {}) {
    let url = API_CONFIG.BASE_URL + endpoint;

    // Separate path params from query params
    const pathParams = {};
    const queryParams = {};

    Object.keys(params).forEach(key => {
        if (url.includes(`{${key}}`)) {
            pathParams[key] = params[key];
        } else {
            queryParams[key] = params[key];
        }
    });

    // Replace path parameters (e.g., {id} -> 123)
    Object.keys(pathParams).forEach(key => {
        url = url.replace(`{${key}}`, pathParams[key]);
    });

    // Add query parameters (e.g., ?hours=6&type=CT1)
    const queryString = Object.keys(queryParams)
        .map(key => `${key}=${encodeURIComponent(queryParams[key])}`)
        .join('&');

    if (queryString) {
        url += `?${queryString}`;
    }

    return url;
}
