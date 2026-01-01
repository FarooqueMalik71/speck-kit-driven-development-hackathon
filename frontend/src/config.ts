// Configuration for the AI Chatbot
const config = {
  // Backend API URL - dynamically determined based on environment
  BACKEND_URL: (() => {
    // Check if we're in a browser environment
    if (typeof window !== 'undefined') {
      // In browser environment
      // For production deployment, use the custom field from docusaurus config
      // @ts-ignore - accessing docusaurus siteConfig
      if (window && (window as any).siteConfig && (window as any).siteConfig.customFields) {
        // @ts-ignore
        return (window as any).siteConfig.customFields.BACKEND_URL;
      }
      // Fallback: check if we're on localhost
      if (window.location && window.location.hostname === 'localhost' || window.location.hostname.startsWith('127.')) {
        return 'http://localhost:8000';
      } else {
        // For production, you can set the URL to your deployed backend
        // Update this with your actual deployed backend URL
        return 'https://your-backend-project-name.vercel.app/api'; // Replace with your actual backend URL
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