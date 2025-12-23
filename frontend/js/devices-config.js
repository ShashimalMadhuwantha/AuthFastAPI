// Devices API Configuration (ES6 Module version)
// This is a module-specific version of config for devices-api.js

// Get API base URL
const getBaseUrl = () => {
    const hostname = window.location.hostname;

    // If running in Docker (served from nginx on port 3000)
    if (window.location.port === '3000') {
        return 'http://localhost:8000';
    }

    // Local development
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return 'http://127.0.0.1:8000';
    }

    // Production - use same host
    return `${window.location.protocol}//${hostname}:8000`;
};

const API_CONFIG = {
    BASE_URL: getBaseUrl()
};

// Helper function to get full API URL
function getApiUrl(endpoint, params = {}) {
    let url = API_CONFIG.BASE_URL + endpoint;

    // Replace path parameters (e.g., {id})
    Object.keys(params).forEach(key => {
        url = url.replace(`{${key}}`, params[key]);
    });

    return url;
}

export { API_CONFIG, getApiUrl };
