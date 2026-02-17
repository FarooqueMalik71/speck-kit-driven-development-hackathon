import React, { useState, useEffect } from 'react';
import Layout from '@theme/Layout';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  citations?: string[];
}

const AIChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Hello! I\'m your AI assistant for the Physical AI & Humanoid Robotics textbook. How can I help you today?',
      sender: 'ai',
      timestamp: new Date(),
      citations: []
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [queryMode, setQueryMode] = useState<'full_book' | 'selected_text'>('full_book');
  const [selectedText, setSelectedText] = useState('');

  const { siteConfig } = useDocusaurusContext();

  const handleSend = async () => {
    if (inputValue.trim() === '' || isLoading) return;

    // Add user message
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
      // Prepare the query payload
      const queryPayload = {
        query: inputValue,
        mode: queryMode,
        context_ids: queryMode === 'selected_text' && selectedText ? [selectedText] : []
      };

      // Call the backend API to get AI response
      const response = await getAIResponse(queryPayload);

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.answer,
        sender: 'ai',
        timestamp: new Date(),
        citations: response.citations || []
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

  // Real API call to backend
  const getAIResponse = async (queryPayload: any): Promise<any> => {
    try {
      // Get the backend URL from site config custom fields
      const customFields = (siteConfig.customFields as any) || {};
      const backendUrl = customFields.backendUrl || 'https://farooquemalik50871-AI-Book-Backend.hf.space';

      const response = await fetch(`${backendUrl}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
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

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && !isLoading) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleTextSelection = () => {
    const selection = window.getSelection();
    if (selection && selection.toString().trim() !== '') {
      setSelectedText(selection.toString().substring(0, 100) + '...'); // Limit the display
      setQueryMode('selected_text');
    }
  };

  // Add event listener for text selection
  useEffect(() => {
    const handleMouseUp = () => {
      handleTextSelection();
    };

    document.addEventListener('mouseup', handleMouseUp);
    return () => {
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, []);

  return (
    <Layout
      title={`AI Assistant - ${siteConfig.title}`}
      description="AI-powered assistant for the Physical AI & Humanoid Robotics textbook">
      <div className="container margin-vert--lg">
        <div className="row">
          <div className="col col--12">
            <h1>AI Assistant for Physical AI & Humanoid Robotics</h1>

            <div className="margin-bottom--lg">
              <label htmlFor="query-mode" className="form-label">
                Query Mode:
              </label>
              <div className="button-group button-group--block">
                <button
                  className={`button ${queryMode === 'full_book' ? 'button--primary' : 'button--secondary'}`}
                  onClick={() => setQueryMode('full_book')}>
                  Full Book Q&A
                </button>
                <button
                  className={`button ${queryMode === 'selected_text' ? 'button--primary' : 'button--secondary'}`}
                  onClick={() => setQueryMode('selected_text')}>
                  Selected Text Q&A
                </button>
              </div>

              {queryMode === 'selected_text' && selectedText && (
                <div className="alert alert--info margin-top--md">
                  <p><strong>Selected Text:</strong> {selectedText}</p>
                  <p className="margin-bottom--none"><em>AI responses will be limited to information related to this text.</em></p>
                </div>
              )}
            </div>

            <div className="card">
              <div className="card__body">
                <div className="margin-bottom--lg" style={{ maxHeight: '500px', overflowY: 'auto' }}>
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`margin-bottom--sm ${message.sender === 'user' ? 'text--right' : ''}`}
                    >
                      <div
                        className={`padding--sm radius--sm ${
                          message.sender === 'user'
                            ? 'background--primary text--light'
                            : 'background--success text--light'
                        }`}
                        style={{
                          display: 'inline-block',
                          maxWidth: '80%',
                          wordWrap: 'break-word'
                        }}
                      >
                        <div className="margin-bottom--xs">
                          <strong>{message.sender === 'user' ? 'You' : 'AI Assistant'}:</strong>
                        </div>
                        <div>{message.text}</div>
                        {message.citations && message.citations.length > 0 && (
                          <div className="margin-top--sm">
                            <small>
                              <strong>Citations:</strong> {message.citations.join(', ')}
                            </small>
                          </div>
                        )}
                        <div className="margin-top--xs">
                          <small className="text--light">
                            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </small>
                        </div>
                      </div>
                    </div>
                  ))}

                  {isLoading && (
                    <div className="margin-bottom--sm">
                      <div
                        className="padding--sm radius--sm background--success text--light"
                        style={{ display: 'inline-block', maxWidth: '80%' }}
                      >
                        <div className="margin-bottom--xs">
                          <strong>AI Assistant:</strong>
                        </div>
                        <div>Thinking...</div>
                      </div>
                    </div>
                  )}
                </div>

                <div className="input-group">
                  <textarea
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask a question about the textbook content..."
                    className="text--normal padding--md form-control"
                    rows={3}
                    disabled={isLoading}
                    style={{ resize: 'vertical' }}
                  />
                  <div className="margin-top--sm">
                    <button
                      onClick={handleSend}
                      disabled={inputValue.trim() === '' || isLoading}
                      className="button button--primary"
                    >
                      {isLoading ? 'Sending...' : 'Send'}
                    </button>
                  </div>
                </div>

                <div className="margin-top--md">
                  <div className="alert alert--info">
                    <p className="margin-bottom--sm"><strong>How to use:</strong></p>
                    <ul className="margin-bottom--none">
                      <li>Use <strong>Full Book Q&A</strong> to ask questions about the entire textbook content</li>
                      <li>Use <strong>Selected Text Q&A</strong> to ask targeted questions about specific content you've selected</li>
                      <li>Simply select text anywhere on the textbook pages to enable Selected Text mode</li>
                      <li>All AI responses are grounded in textbook content with citations provided</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default AIChatPage;