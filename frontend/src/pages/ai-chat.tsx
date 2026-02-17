import React, { useState, useEffect, useRef } from 'react';
import Layout from '@theme/Layout';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  citations?: string[];
  sources?: string[];
}

const AIChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Hello! I\'m your AI assistant for the Physical AI & Humanoid Robotics textbook. Ask me anything about the textbook content.',
      sender: 'ai',
      timestamp: new Date(),
      citations: []
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [queryMode, setQueryMode] = useState<'full_book' | 'selected_text'>('full_book');
  const [selectedText, setSelectedText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { siteConfig } = useDocusaurusContext();

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (inputValue.trim() === '' || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const queryPayload = {
        query: inputValue,
        mode: queryMode,
        context_ids: queryMode === 'selected_text' && selectedText ? [selectedText] : []
      };

      const response = await getAIResponse(queryPayload);

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.answer,
        sender: 'ai',
        timestamp: new Date(),
        citations: response.citations || [],
        sources: response.sources || []
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I encountered an error processing your request. Please try again.',
        sender: 'ai',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const getAIResponse = async (queryPayload: any): Promise<any> => {
    try {
      const customFields = (siteConfig.customFields as any) || {};
      const backendUrl = customFields.backendUrl || 'http://localhost:8000';

      const response = await fetch(`${backendUrl}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(queryPayload),
      });

      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching AI response:', error);
      throw error;
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && !isLoading) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleTextSelection = () => {
    const selection = window.getSelection();
    if (selection && selection.toString().trim() !== '') {
      setSelectedText(selection.toString().substring(0, 100) + '...');
      setQueryMode('selected_text');
    }
  };

  useEffect(() => {
    document.addEventListener('mouseup', handleTextSelection);
    return () => document.removeEventListener('mouseup', handleTextSelection);
  }, []);

  return (
    <Layout
      title={`AI Assistant - ${siteConfig.title}`}
      description="AI-powered assistant for the Physical AI & Humanoid Robotics textbook">
      <div className="chat-page">
        <div className="chat-container">
          {/* Header */}
          <div className="chat-header">
            <div className="chat-header__info">
              <div className="chat-header__avatar">AI</div>
              <div>
                <div className="chat-header__title">Textbook AI Assistant</div>
                <div className="chat-header__subtitle">Physical AI & Humanoid Robotics</div>
              </div>
            </div>
            <div className="chat-header__mode">
              <button
                className={`chat-mode-btn ${queryMode === 'full_book' ? 'chat-mode-btn--active' : ''}`}
                onClick={() => setQueryMode('full_book')}>
                Full Book
              </button>
              <button
                className={`chat-mode-btn ${queryMode === 'selected_text' ? 'chat-mode-btn--active' : ''}`}
                onClick={() => setQueryMode('selected_text')}>
                Selected Text
              </button>
            </div>
          </div>

          {/* Selected text banner */}
          {queryMode === 'selected_text' && selectedText && (
            <div className="chat-selected-banner">
              <span className="chat-selected-banner__label">Context:</span>
              <span className="chat-selected-banner__text">{selectedText}</span>
              <button
                className="chat-selected-banner__clear"
                onClick={() => { setSelectedText(''); setQueryMode('full_book'); }}>
                Clear
              </button>
            </div>
          )}

          {/* Messages */}
          <div className="chat-messages">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`chat-msg ${message.sender === 'user' ? 'chat-msg--user' : 'chat-msg--ai'}`}>
                {message.sender === 'ai' && (
                  <div className="chat-msg__avatar chat-msg__avatar--ai">AI</div>
                )}
                <div className="chat-msg__content">
                  <div className={`chat-bubble ${message.sender === 'user' ? 'chat-bubble--user' : 'chat-bubble--ai'}`}>
                    <div className="chat-bubble__text">{message.text}</div>
                    {message.citations && message.citations.length > 0 && (
                      <div className="chat-bubble__citations">
                        <span className="chat-bubble__citations-label">Sources:</span>
                        {message.citations.map((c, i) => (
                          <span key={i} className="chat-bubble__citation-tag">{c}</span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className={`chat-msg__time ${message.sender === 'user' ? 'chat-msg__time--right' : ''}`}>
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
                {message.sender === 'user' && (
                  <div className="chat-msg__avatar chat-msg__avatar--user">You</div>
                )}
              </div>
            ))}

            {isLoading && (
              <div className="chat-msg chat-msg--ai">
                <div className="chat-msg__avatar chat-msg__avatar--ai">AI</div>
                <div className="chat-msg__content">
                  <div className="chat-bubble chat-bubble--ai">
                    <div className="chat-typing">
                      <span className="chat-typing__dot"></span>
                      <span className="chat-typing__dot"></span>
                      <span className="chat-typing__dot"></span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="chat-input">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question about the textbook..."
              rows={1}
              disabled={isLoading}
              className="chat-input__field"
            />
            <button
              onClick={handleSend}
              disabled={inputValue.trim() === '' || isLoading}
              className="chat-input__send">
              {isLoading ? (
                <span className="chat-input__spinner" />
              ) : (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="22" y1="2" x2="11" y2="13" />
                  <polygon points="22 2 15 22 11 13 2 9 22 2" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default AIChatPage;
