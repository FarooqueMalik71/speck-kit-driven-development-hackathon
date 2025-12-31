// Configuration for the AI Chatbot
const config = {
  // Backend API URL - set directly since process.env is not available in browser for Docusaurus
  BACKEND_URL: typeof window !== 'undefined'
    ? 'http://localhost:8000'  // Directly set to the correct backend URL
    : 'http://localhost:8000', // Fallback for server-side rendering

  // Default settings
  DEFAULT_MODEL: 'mistralai/devstral-2512:free',
  TIMEOUT_MS: 30000, // 30 seconds timeout
};

export default config;