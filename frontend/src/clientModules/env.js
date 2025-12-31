
// Client-side environment variables for Docusaurus
// This file is loaded by the clientModules in docusaurus.config.ts

// Define environment variables that should be available in the browser
window.ENV = window.ENV || {};

// Add any environment variables you need here
window.ENV.REACT_APP_BACKEND_URL = process.env.REACT_APP_BACKEND_URL;