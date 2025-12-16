import React from 'react';
import ContentMetadata from '@site/src/components/ContentMetadata';
import ContentTags from '@site/src/components/ContentTags';
import AIChat from '@site/src/components/AIChat';
import './styles.css';

// Text Content Template
export const TextTemplate = ({
  title,
  content,
  tags = [],
  metadata = {},
  showAIChat = true,
  children
}) => {
  return (
    <div className="content-template text-template">
      <h1>{title}</h1>
      <ContentMetadata {...metadata} />
      <ContentTags tags={tags} />
      <div className="content-body">
        {content ? <div dangerouslySetInnerHTML={{ __html: content }} /> : children}
      </div>
      {showAIChat && <AIChat />}
    </div>
  );
};

// Code Example Template
export const CodeTemplate = ({
  title,
  code,
  language = 'python',
  description,
  tags = [],
  metadata = {},
  showAIChat = true,
  children
}) => {
  return (
    <div className="content-template code-template">
      <h1>{title}</h1>
      <ContentMetadata {...metadata} />
      <ContentTags tags={tags} />
      <div className="content-description">
        {description && <p>{description}</p>}
      </div>
      <div className="code-block">
        <pre>
          <code className={`language-${language}`}>
            {code}
          </code>
        </pre>
      </div>
      <div className="code-explanation">
        {children}
      </div>
      {showAIChat && <AIChat />}
    </div>
  );
};

// Figure/Visualization Template
export const FigureTemplate = ({
  title,
  src,
  alt,
  caption,
  tags = [],
  metadata = {},
  showAIChat = true,
  children
}) => {
  return (
    <div className="content-template figure-template">
      <h1>{title}</h1>
      <ContentMetadata {...metadata} />
      <ContentTags tags={tags} />
      <div className="figure-container">
        <img src={src} alt={alt} className="figure-image" />
        {caption && <div className="figure-caption">{caption}</div>}
      </div>
      <div className="figure-explanation">
        {children}
      </div>
      {showAIChat && <AIChat />}
    </div>
  );
};

// Simulation Viewer Template
export const SimulationTemplate = ({
  title,
  embedUrl,
  description,
  tags = [],
  metadata = {},
  showAIChat = true,
  children
}) => {
  return (
    <div className="content-template simulation-template">
      <h1>{title}</h1>
      <ContentMetadata {...metadata} />
      <ContentTags tags={tags} />
      <div className="content-description">
        {description && <p>{description}</p>}
      </div>
      <div className="simulation-container">
        <iframe
          src={embedUrl}
          className="simulation-frame"
          title={title}
          allowFullScreen
        ></iframe>
      </div>
      <div className="simulation-explanation">
        {children}
      </div>
      {showAIChat && <AIChat />}
    </div>
  );
};

// Interactive Element Template
export const InteractiveTemplate = ({
  title,
  component,
  description,
  tags = [],
  metadata = {},
  showAIChat = true,
  children
}) => {
  return (
    <div className="content-template interactive-template">
      <h1>{title}</h1>
      <ContentMetadata {...metadata} />
      <ContentTags tags={tags} />
      <div className="content-description">
        {description && <p>{description}</p>}
      </div>
      <div className="interactive-container">
        {component}
      </div>
      <div className="interactive-explanation">
        {children}
      </div>
      {showAIChat && <AIChat />}
    </div>
  );
};

export default {
  TextTemplate,
  CodeTemplate,
  FigureTemplate,
  SimulationTemplate,
  InteractiveTemplate
};