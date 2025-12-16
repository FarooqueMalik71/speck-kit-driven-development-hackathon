import React from 'react';
import './styles.css';

const ContentVersion = ({
  version = '1.0.0',
  lastModified,
  authors = [],
  changelog = [],
  status = 'draft' // draft, review, published, deprecated
}) => {
  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'draft':
        return 'status-draft';
      case 'review':
        return 'status-review';
      case 'published':
        return 'status-published';
      case 'deprecated':
        return 'status-deprecated';
      default:
        return 'status-unknown';
    }
  };

  return (
    <div className="content-version">
      <div className="version-header">
        <div className="version-info">
          <span className="version-label">Version:</span>
          <span className="version-number">{version}</span>
        </div>
        <div className={`status-badge ${getStatusColor(status)}`}>
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </div>
      </div>

      <div className="version-details">
        <div className="detail-item">
          <span className="detail-label">Last Modified:</span>
          <span className="detail-value">{formatDate(lastModified)}</span>
        </div>

        {authors.length > 0 && (
          <div className="detail-item">
            <span className="detail-label">Authors:</span>
            <span className="detail-value">
              {authors.map((author, index) => (
                <span key={index} className="author">
                  {author.name}
                  {author.email && <span className="author-email"> ({author.email})</span>}
                  {index < authors.length - 1 && ', '}
                </span>
              ))}
            </span>
          </div>
        )}
      </div>

      {changelog.length > 0 && (
        <div className="changelog-section">
          <h4>Change Log</h4>
          <ul className="changelog-list">
            {changelog.map((change, index) => (
              <li key={index} className="changelog-item">
                <div className="change-date">{formatDate(change.date)}</div>
                <div className="change-description">{change.description}</div>
                <div className="change-author">by {change.author}</div>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="version-actions">
        <button className="version-action-btn">Suggest Edit</button>
        <button className="version-action-btn">Report Issue</button>
        <button className="version-action-btn">Compare Versions</button>
      </div>
    </div>
  );
};

export default ContentVersion;