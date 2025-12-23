// API Configuration
// This file contains the API endpoint configuration
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
