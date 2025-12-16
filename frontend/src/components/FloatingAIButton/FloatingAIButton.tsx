import React, { useState, useEffect } from 'react';
import Link from '@docusaurus/Link';

const FloatingAIButton = () => {
  const [isVisible, setIsVisible] = useState(true);

  // Show button when page is scrolled down
  useEffect(() => {
    const toggleVisibility = () => {
      if (window.pageYOffset > 300) {
        setIsVisible(true);
      } else {
        setIsVisible(false);
      }
    };

    window.addEventListener('scroll', toggleVisibility);

    return () => window.removeEventListener('scroll', toggleVisibility);
  }, []);

  return (
    <Link
      to="/ai-chat"
      className={`floating-ai-button ${isVisible ? 'show' : 'hide'}`}
      aria-label="AI Assistant"
    >
      <span role="img" aria-label="robot">🤖</span>
    </Link>
  );
};

export default FloatingAIButton;