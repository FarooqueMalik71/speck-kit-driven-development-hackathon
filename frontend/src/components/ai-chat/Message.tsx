import React from 'react';

interface MessageProps {
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
}

export const Message: React.FC<MessageProps> = ({ content, role, timestamp }) => {
  const isUser = role === 'user';

  // Format timestamp
  const formattedTime = timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  // Process content to add textbook-style formatting
  const processedContent = processTextbookContent(content);

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: isUser ? 'flex-end' : 'flex-start',
      marginBottom: '1rem',
      width: '100%'
    }}>
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        maxWidth: '80%',
        backgroundColor: isUser ? '#e0e7ff' : '#f9fafb', // Light indigo for user, light gray for assistant
        borderRadius: '0.75rem',
        padding: '1rem',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
      }}>
        <div style={{
          fontWeight: '500',
          marginBottom: '0.25rem',
          color: isUser ? '#4f46e5' : '#1f2937', // Indigo for user, dark gray for assistant
          fontSize: '0.875rem'
        }}>
          {isUser ? 'You' : 'AI Textbook Assistant'}
        </div>

        <div
          style={{
            lineHeight: '1.6',
            color: '#1f2937'
          }}
          dangerouslySetInnerHTML={{ __html: processedContent }}
        />
      </div>

      <div style={{
        fontSize: '0.75rem',
        color: '#6b7280',
        marginTop: '0.25rem',
        alignSelf: isUser ? 'flex-end' : 'flex-start'
      }}>
        {formattedTime}
      </div>
    </div>
  );
};

// Helper function to process content with textbook formatting
const processTextbookContent = (content: string): string => {
  let processed = content;

  // Convert markdown-style headings to HTML
  processed = processed.replace(/^# (.*$)/gm, '<h1>$1</h1>');
  processed = processed.replace(/^## (.*$)/gm, '<h2>$1</h2>');
  processed = processed.replace(/^### (.*$)/gm, '<h3>$1</h3>');

  // Convert bold text
  processed = processed.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

  // Convert italic text
  processed = processed.replace(/\*(.*?)\*/g, '<em>$1</em>');

  // Convert bullet points
  processed = processed.replace(/^\- (.*$)/gm, '<li>$1</li>');
  processed = processed.replace(/(<li>.*<\/li>)+/g, '<ul>$&</ul>');

  // Add special formatting for "Further Reading" sections
  processed = processed.replace(
    /(📘\s?\*\*Further Reading \/ Reference\*\*)/g,
    '<div style="background-color: #dbeafe; border-left: 4px solid #3b82f6; padding: 0.5rem; margin: 0.5rem 0; border-radius: 0 0.25rem 0.25rem 0;"><strong>$1</strong>'
  );

  // Close the div tag if we opened one
  if ((processed.match(/background-color: #dbeafe/g) || []).length > (processed.match(/<\/div>/g) || []).length) {
    processed += '</div>';
  }

  return processed;
};