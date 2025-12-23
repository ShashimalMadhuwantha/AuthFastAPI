// API Configuration
// This file contains the API endpoint configuration
// Automatically detects environment and sets appropriate API URL

const API_CONFIG = {
    // Detect environment and set base URL
    // In Docker: backend service is accessible at 'backend:8000'
    // In local dev: use localhost
    BASE_URL: (() => {
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
    }
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
