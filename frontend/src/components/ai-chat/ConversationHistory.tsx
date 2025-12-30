import React, { useState, useEffect } from 'react';

interface ConversationHistoryProps {
  sessionId?: string;
  onClose: () => void;
}

interface ConversationTurn {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  references?: any[];
}

export const ConversationHistory: React.FC<ConversationHistoryProps> = ({ sessionId, onClose }) => {
  const [history, setHistory] = useState<ConversationTurn[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (sessionId) {
      fetchHistory();
    }
  }, [sessionId]);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      setError(null);

      if (!sessionId) {
        setHistory([]);
        return;
      }

      const response = await fetch(`http://localhost:8000/api/v1/chatbot/session/${sessionId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API request failed with status ${response.status}: ${errorText}`);
      }

      const data = await response.json();

      // Transform the backend response to match our frontend format
      const historyData: ConversationTurn[] = data.history.map((turn: any) => ({
        id: turn.turnId,
        role: turn.role as 'user' | 'assistant',
        content: turn.content,
        timestamp: turn.timestamp,
        references: turn.references || [],
      }));

      setHistory(historyData);
    } catch (err) {
      if (err instanceof TypeError) {
        setError('Network error: Unable to connect to the server. Please check if the backend is running at http://localhost:8000');
      } else {
        setError('Failed to load conversation history');
      }
      console.error('Error fetching history:', err);
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = async () => {
    if (window.confirm('Are you sure you want to clear the conversation history?')) {
      try {
        if (!sessionId) {
          setError('No session ID provided');
          return;
        }

        const response = await fetch(`http://localhost:8000/api/v1/chatbot/session/${sessionId}/clear`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`API request failed with status ${response.status}: ${errorText}`);
        }

        setHistory([]);
      } catch (err) {
        if (err instanceof TypeError) {
          setError('Network error: Unable to connect to the server. Please check if the backend is running at http://localhost:8000');
        } else {
          setError('Failed to clear conversation history');
        }
        console.error('Error clearing history:', err);
      }
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
    }}>
      <div style={{
        padding: '1rem',
        borderBottom: '1px solid #e5e7eb',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <h3 style={{ margin: 0, fontSize: '1rem' }}>Conversation History</h3>
        <button
          onClick={onClose}
          style={{
            background: 'none',
            border: 'none',
            color: '#6b7280',
            cursor: 'pointer',
            fontSize: '1.25rem'
          }}
        >
          ×
        </button>
      </div>

      <div style={{
        padding: '0.5rem',
        borderBottom: '1px solid #e5e7eb',
        display: 'flex',
        gap: '0.5rem'
      }}>
        <button
          onClick={fetchHistory}
          disabled={loading}
          style={{
            flex: 1,
            padding: '0.5rem',
            backgroundColor: '#f3f4f6',
            border: '1px solid #d1d5db',
            borderRadius: '0.375rem',
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          Refresh
        </button>
        <button
          onClick={clearHistory}
          disabled={loading || history.length === 0}
          style={{
            flex: 1,
            padding: '0.5rem',
            backgroundColor: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: '0.375rem',
            cursor: (loading || history.length === 0) ? 'not-allowed' : 'pointer',
            color: '#dc2626'
          }}
        >
          Clear
        </button>
      </div>

      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '1rem 0.5rem'
      }}>
        {loading ? (
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '100%',
            color: '#6b7280'
          }}>
            Loading history...
          </div>
        ) : error ? (
          <div style={{
            color: '#dc2626',
            textAlign: 'center',
            padding: '1rem'
          }}>
            {error}
          </div>
        ) : history.length === 0 ? (
          <div style={{
            color: '#6b7280',
            textAlign: 'center',
            padding: '1rem'
          }}>
            No conversation history available
          </div>
        ) : (
          <div>
            {history.map((turn) => (
              <div
                key={turn.id}
                style={{
                  marginBottom: '1rem',
                  padding: '0.75rem',
                  backgroundColor: turn.role === 'user' ? '#e0e7ff' : '#f3f4f6',
                  borderRadius: '0.5rem'
                }}
              >
                <div style={{
                  fontWeight: '500',
                  fontSize: '0.875rem',
                  color: turn.role === 'user' ? '#4f46e5' : '#1f2937',
                  marginBottom: '0.25rem'
                }}>
                  {turn.role === 'user' ? 'You' : 'AI Assistant'} •{' '}
                  {new Date(turn.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
                <div style={{
                  fontSize: '0.875rem',
                  lineHeight: '1.5'
                }}>
                  {turn.content.length > 100 ? `${turn.content.substring(0, 100)}...` : turn.content}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};