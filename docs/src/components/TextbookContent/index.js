import React from 'react';
import AIChat from '@site/src/components/AIChat';
import './styles.css';

const TextbookContent = ({ children, type = "default" }) => {
  return (
    <div className={`textbook-content textbook-content-${type}`}>
      {children}
      <div className="content-actions">
        <AIChat />
      </div>
    </div>
  );
};

export default TextbookContent;