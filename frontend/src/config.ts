// Configuration for the AI Chatbot
const config = {
  // Backend API URL - Use relative path for same-project deployment
  BACKEND_URL: (() => {
    // Check if we're in a browser environment
    if (typeof window !== 'undefined') {
      // In browser environment
      // For same Vercel project deployment, use relative path to API route
      if (window.location && window.location.hostname !== 'localhost' && !window.location.hostname.startsWith('127.')) {
        // In production on same Vercel project, the API route is at /api/query
        return '/api'; // This will make the full path /api/query
      } else {
        // In development, use the localhost backend
        return 'http://localhost:8000';
      }
    }
    // For server-side rendering
    return 'http://localhost:8000';
  })(),

  // Default settings
  DEFAULT_MODEL: 'mistralai/devstral-2512:free',
  TIMEOUT_MS: 30000, // 30 seconds timeout
};

export default config;