// Configuration for the AI Chatbot
const config = {
  // Backend API URL - can be overridden by environment variable or set for production
  BACKEND_URL: process.env.REACT_APP_BACKEND_URL || typeof window !== 'undefined'
    ? `${window.location.protocol}//${window.location.hostname}:${window.location.port || '8002'}`
    : 'http://localhost:8002',

  // Default settings
  DEFAULT_MODEL: 'mistralai/devstral-2512:free',
  TIMEOUT_MS: 30000, // 30 seconds timeout
};

export default config;