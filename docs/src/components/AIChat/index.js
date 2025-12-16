import React, { useState } from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import './styles.css';

const AIChat = ({ initialQuery = "" }) => {
  const { siteConfig } = useDocusaurusContext();
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: 'Hello! I\'m your AI assistant for the Physical AI & Humanoid Robotics textbook. How can I help you today?',
      sender: 'ai',
      timestamp: new Date(),
    }
  ]);
  const [inputValue, setInputValue] = useState(initialQuery);

  const handleSend = () => {
    if (inputValue.trim() === '') return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');

    // Simulate AI response after a delay
    setTimeout(() => {
      const aiMessage = {
        id: Date.now() + 1,
        text: `I received your question: "${inputValue}". This is a simulated response from the AI assistant. In the full implementation, this would connect to the RAG system to provide contextually relevant answers from the textbook content.`,
        sender: 'ai',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, aiMessage]);
    }, 1000);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="ai-chat-container">
      <h3>AI Assistant</h3>
      <div className="ai-chat-messages">
        {messages.map((message) => (
          <div key={message.id} className={`ai-message ${message.sender}`}>
            <div className="ai-message-text">{message.text}</div>
            <div className="ai-message-time">
              {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </div>
          </div>
        ))}
      </div>
      <div className="ai-chat-input">
        <textarea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask a question about this content..."
          rows="3"
        />
        <button onClick={handleSend} disabled={!inputValue.trim()}>
          Send
        </button>
      </div>
    </div>
  );
};

export default AIChat;