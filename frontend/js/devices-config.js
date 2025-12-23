// Devices API Configuration (ES6 Module version)
// This exists because devices-api.js uses ES6 imports
// config.js can't be imported as a module due to backward compatibility

// Get API base URL
const getBaseUrl = () => {
    const hostname = window.location.hostname;

    // Local development - always use localhost:8000
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return 'http://localhost:8000';
    }

    // Production/Remote - use same hostname
    return `http://${hostname}:8000`;
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
