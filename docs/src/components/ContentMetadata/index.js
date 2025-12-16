import React from 'react';
import './styles.css';

const ContentMetadata = ({
  title,
  content_type = "text",
  difficulty_level = "intermediate",
  prerequisites = [],
  learning_objectives = [],
  tags = [],
  word_count,
  reading_time,
  related_content = [],
  cross_references = []
}) => {
  return (
    <div className="content-metadata">
      <div className="metadata-section">
        <h4>Content Information</h4>
        <div className="metadata-grid">
          <div className="metadata-item">
            <span className="metadata-label">Type:</span>
            <span className="metadata-value">{content_type}</span>
          </div>
          <div className="metadata-item">
            <span className="metadata-label">Difficulty:</span>
            <span className={`metadata-value difficulty-${difficulty_level}`}>
              {difficulty_level.charAt(0).toUpperCase() + difficulty_level.slice(1)}
            </span>
          </div>
          {word_count && (
            <div className="metadata-item">
              <span className="metadata-label">Words:</span>
              <span className="metadata-value">{word_count}</span>
            </div>
          )}
          {reading_time && (
            <div className="metadata-item">
              <span className="metadata-label">Reading Time:</span>
              <span className="metadata-value">{reading_time} min</span>
            </div>
          )}
        </div>
      </div>

      {prerequisites.length > 0 && (
        <div className="metadata-section">
          <h4>Prerequisites</h4>
          <ul className="metadata-list">
            {prerequisites.map((prereq, index) => (
              <li key={index} className="metadata-list-item">
                {prereq}
              </li>
            ))}
          </ul>
        </div>
      )}

      {learning_objectives.length > 0 && (
        <div className="metadata-section">
          <h4>Learning Objectives</h4>
          <ul className="metadata-list">
            {learning_objectives.map((objective, index) => (
              <li key={index} className="metadata-list-item">
                {objective}
              </li>
            ))}
          </ul>
        </div>
      )}

      {tags.length > 0 && (
        <div className="metadata-section">
          <h4>Tags</h4>
          <div className="tag-container">
            {tags.map((tag, index) => (
              <span key={index} className="tag">
                {tag}
              </span>
            ))}
          </div>
        </div>
      )}

      {related_content.length > 0 && (
        <div className="metadata-section">
          <h4>Related Content</h4>
          <ul className="metadata-list">
            {related_content.map((content, index) => (
              <li key={index} className="metadata-list-item">
                <a href={content.url}>{content.title}</a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ContentMetadata;