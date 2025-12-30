import React from 'react';

interface Reference {
  type: string;
  title: string;
  url: string;
  description: string;
  relevance: number;
}

interface ReferenceSectionProps {
  references: Reference[];
}

export const ReferenceSection: React.FC<ReferenceSectionProps> = ({ references }) => {
  if (!references || references.length === 0) {
    return null;
  }

  return (
    <div style={{
      backgroundColor: '#f0f9ff', // Light blue background
      borderLeft: '4px solid #3b82f6', // Blue left border
      padding: '1rem',
      borderRadius: '0 0.5rem 0.5rem 0',
      marginTop: '1rem'
    }}>
      <h4 style={{
        margin: '0 0 0.75rem 0',
        color: '#1d4ed8', // Dark blue
        fontSize: '1rem',
        fontWeight: '600',
        display: 'flex',
        alignItems: 'center'
      }}>
        <span role="img" aria-label="book">📘</span> <span style={{ marginLeft: '0.5rem' }}>Further Reading / Reference</span>
      </h4>

      <ul style={{
        listStyle: 'none',
        padding: 0,
        margin: 0
      }}>
        {references.map((ref, index) => (
          <li
            key={`${ref.url}-${index}`}
            style={{
              marginBottom: '0.5rem',
              padding: '0.5rem',
              backgroundColor: 'white',
              borderRadius: '0.375rem',
              border: '1px solid #dbeafe'
            }}
          >
            <div style={{
              fontWeight: '500',
              color: '#1e40af',
              marginBottom: '0.25rem'
            }}>
              {ref.type === 'internal' ? (
                <a
                  href={ref.url}
                  style={{
                    textDecoration: 'underline',
                    color: '#1e40af'
                  }}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {ref.title}
                </a>
              ) : (
                <a
                  href={ref.url}
                  style={{
                    textDecoration: 'underline',
                    color: '#1e40af'
                  }}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {ref.title}
                </a>
              )}
            </div>
            <div style={{
              fontSize: '0.875rem',
              color: '#4b5563',
              marginBottom: '0.25rem'
            }}>
              {ref.description}
            </div>
            {ref.relevance !== undefined && (
              <div style={{
                fontSize: '0.75rem',
                color: '#6b7280',
                fontStyle: 'italic'
              }}>
                Relevance: {(ref.relevance * 100).toFixed(0)}%
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
};