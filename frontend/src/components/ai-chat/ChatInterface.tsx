import React, { useState, useEffect, useRef } from 'react';
import { Message } from './Message';
import { ConversationHistory } from './ConversationHistory';
import { ReferenceSection } from '../textbook/ReferenceSection';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  references?: any[];
}

interface ChatInterfaceProps {
  sessionId?: string;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ sessionId: propSessionId }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>(propSessionId);
  const [showHistory, setShowHistory] = useState(false);
  const [isScrolledUp, setIsScrolledUp] = useState(false); // Track if user has scrolled up
  const messagesEndRef = useRef<null | HTMLDivElement>(null);
  const messagesContainerRef = useRef<null | HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change, but only if user is near bottom
  useEffect(() => {
    const messagesContainer = messagesContainerRef.current;
    if (messagesContainer && !isScrolledUp) {
      // Check if user is near the bottom before auto-scrolling
      const isNearBottom = messagesContainer.scrollHeight - messagesContainer.scrollTop <= messagesContainer.clientHeight + 100;
      if (isNearBottom) {
        scrollToBottom();
      }
    }
  }, [messages, isScrolledUp]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Smart scroll handler that prevents auto-scrolling when user has scrolled up
  const handleScroll = (element: HTMLElement) => {
    // Check if user has scrolled up from the bottom
    const isNearBottom = element.scrollHeight - element.scrollTop <= element.clientHeight + 100;
    // Store this state so we know whether to auto-scroll or not
    // In a real implementation, you'd use a state variable
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    // Reset scrolled state when user sends a new message
    setIsScrolledUp(false);

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      role: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Call the backend API
      const response = await callBackendApi(inputValue, sessionId);

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.answer,
        role: 'assistant',
        timestamp: new Date(),
        references: response.references || [],
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Update session ID if it was returned
      if (response.session_id && !sessionId) {
        setSessionId(response.session_id);
      }
    } catch (error) {
      console.error('Error getting response:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        role: 'assistant',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Call the actual backend API
  const callBackendApi = async (query: string, currentSessionId?: string) => {
    try {
      // Use environment variable for backend URL, default to localhost for development
      const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8002';
      const response = await fetch(`${BACKEND_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          session_id: currentSessionId
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API request failed with status ${response.status}: ${errorText}`);
      }

      return await response.json();
    } catch (error) {
      // Handle network errors or other exceptions
      const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8002';
      if (error instanceof TypeError) {
        throw new Error(`Network error: Unable to connect to the server. Please check if the backend is running at ${BACKEND_URL}`);
      }
      throw error;
    }
  };

  return (
    <div className="textbook-chat-interface" style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      fontFamily: 'Inter, Roboto, system-ui, sans-serif',
      backgroundColor: '#ffffff',
      color: '#1f2937',
      position: 'relative' // Added for proper positioning
    }}>
      {/* Header with attribution */}
      <header className="chat-header" style={{
        padding: '1rem',
        backgroundColor: '#4f46e5', // indigo
        color: 'white',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        zIndex: 100 // Ensure header stays on top
      }}>
        <h1 style={{ margin: 0, fontSize: '1.25rem', fontWeight: '600' }}>AI Textbook Assistant</h1>
        <div style={{ fontSize: '0.875rem', opacity: 0.9 }}>
          Built by Farooque Malik | AI-Powered RAG System
        </div>
      </header>

      {/* Main chat area */}
      <div style={{
        display: 'flex',
        flex: 1,
        overflow: 'hidden',
        position: 'relative' // Added for proper layout
      }}>
        {/* Conversation history sidebar */}
        {showHistory && (
          <div style={{
            width: '300px',
            borderRight: '1px solid #e5e7eb',
            backgroundColor: '#f9fafb',
            display: 'flex',
            flexDirection: 'column'
          }}>
            <ConversationHistory
              sessionId={sessionId}
              onClose={() => setShowHistory(false)}
            />
          </div>
        )}

        {/* Main chat content */}
        <div style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          padding: '1rem',
          position: 'relative' // Added for proper positioning
        }}>
          {/* Messages container */}
          <div
            ref={messagesContainerRef}
            onScroll={(e) => {
              const element = e.target as HTMLElement;
              // Check if user has scrolled up from the bottom
              const isNearBottom = element.scrollHeight - element.scrollTop <= element.clientHeight + 100;
              setIsScrolledUp(!isNearBottom);
            }}
            style={{
              flex: 1,
              overflowY: 'auto',
              marginBottom: '1rem',
              padding: '1rem',
              backgroundColor: '#f9fafb',
              borderRadius: '0.5rem',
              maxHeight: '70vh',
              scrollBehavior: 'smooth' // Smooth scrolling
            }}
          >
            {messages.length === 0 ? (
              <div style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: '100%',
                color: '#6b7280',
                textAlign: 'center'
              }}>
                <div>
                  <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>📚</div>
                  <p>Ask any question about the textbook content</p>
                  <p style={{ fontSize: '0.875rem', opacity: 0.7, marginTop: '0.5rem' }}>
                    Get structured responses with references and citations
                  </p>
                </div>
              </div>
            ) : (
              messages.map((message) => (
                <Message
                  key={message.id}
                  content={message.content}
                  role={message.role}
                  timestamp={message.timestamp}
                />
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input area - Fixed positioning to prevent overlap */}
          <form
            onSubmit={handleSubmit}
            style={{
              display: 'flex',
              gap: '0.5rem',
              position: 'sticky',
              bottom: 0,
              backgroundColor: 'white',
              paddingTop: '0.5rem',
              zIndex: 50 // Ensure input stays on top
            }}
          >
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask a question about the textbook content..."
              disabled={isLoading}
              style={{
                flex: 1,
                padding: '0.75rem 1rem',
                border: '1px solid #d1d5db',
                borderRadius: '0.5rem',
                fontSize: '1rem',
                outline: 'none',
                transition: 'border-color 0.2s'
              }}
              onFocus={(e) => e.target.style.borderColor = '#4f46e5'}
              onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
            />
            <button
              type="submit"
              disabled={isLoading || !inputValue.trim()}
              style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: isLoading || !inputValue.trim() ? '#9ca3af' : '#4f46e5', // indigo
                color: 'white',
                border: 'none',
                borderRadius: '0.5rem',
                cursor: isLoading || !inputValue.trim() ? 'not-allowed' : 'pointer',
                fontWeight: '500',
                transition: 'background-color 0.2s'
              }}
              onMouseOver={(e) => {
                if (!(isLoading || !inputValue.trim())) {
                  e.currentTarget.style.backgroundColor = '#4338ca';
                }
              }}
              onMouseOut={(e) => {
                if (!(isLoading || !inputValue.trim())) {
                  e.currentTarget.style.backgroundColor = '#4f46e5';
                }
              }}
            >
              {isLoading ? (
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span style={{
                    display: 'inline-block',
                    width: '12px',
                    height: '12px',
                    borderRadius: '50%',
                    backgroundColor: 'currentColor',
                    animation: 'loading 1.4s ease-in-out infinite both'
                  }}></span>
                  Thinking...
                </span>
              ) : 'Send'}
            </button>
          </form>

          {/* History toggle */}
          <div style={{
            marginTop: '0.5rem',
            textAlign: 'center'
          }}>
            <button
              onClick={() => setShowHistory(!showHistory)}
              style={{
                background: 'none',
                border: '1px solid #d1d5db',
                color: '#4f46e5', // indigo
                cursor: 'pointer',
                fontSize: '0.875rem',
                padding: '0.5rem 1rem',
                borderRadius: '0.375rem',
                transition: 'all 0.2s'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.backgroundColor = '#f3f4f6';
                e.currentTarget.style.borderColor = '#4f46e5';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
                e.currentTarget.style.borderColor = '#d1d5db';
              }}
            >
              {showHistory ? 'Hide' : 'Show'} Conversation History
            </button>
          </div>
        </div>
      </div>

      {/* Reference section - only show when assistant message has references */}
      {messages.some(m => m.role === 'assistant' && m.references && m.references.length > 0) && (
        <div style={{
          borderTop: '1px solid #e5e7eb',
          padding: '1rem',
          backgroundColor: '#f3f4f6',
          zIndex: 40 // Behind input but above messages
        }}>
          <ReferenceSection
            references={messages
              .filter(m => m.role === 'assistant' && m.references)
              .flatMap(m => m.references || [])
            }
          />
        </div>
      )}
    </div>
  );
};