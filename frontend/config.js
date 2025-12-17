// API Configuration
// This file contains the API endpoint configuration
// Change this URL based on your environment

const API_CONFIG = {
    // For local development
    BASE_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://127.0.0.1:8000'
        : 'http://localhost:8000',
    
    // API endpoints
    ENDPOINTS: {
        SIGNIN: '/api/v1/auth/signin',
        SIGNUP: '/api/v1/auth/signup',
        // Add more endpoints as needed
    }
};

// Helper function to get full API URL
function getApiUrl(endpoint) {
    return API_CONFIG.BASE_URL + endpoint;
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = API_CONFIG;
}
