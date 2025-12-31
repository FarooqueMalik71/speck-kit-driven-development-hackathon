// Configuration for the AI Chatbot
const config = {
  // Backend API URL - try multiple methods to get the backend URL
  BACKEND_URL: (() => {
    // First try to get from window.ENV (set by docusaurus config)
    if (typeof window !== 'undefined' && (window as any).ENV && (window as any).ENV.REACT_APP_BACKEND_URL) {
      return (window as any).ENV.REACT_APP_BACKEND_URL;
    }
    // Then try process.env (for build time)
    if (typeof process !== 'undefined' && process.env && process.env.REACT_APP_BACKEND_URL) {
      return process.env.REACT_APP_BACKEND_URL;
    }
    // Finally fallback to localhost
    return 'http://localhost:8000';
  })(),

  // Default settings
  DEFAULT_MODEL: 'mistralai/devstral-2512:free',
  TIMEOUT_MS: 30000, // 30 seconds timeout
};

export default config;