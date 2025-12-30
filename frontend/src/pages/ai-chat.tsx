import React from 'react';
import Layout from '@theme/Layout';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import { ChatInterface } from '../components/ai-chat/ChatInterface';

const AIChatPage: React.FC = () => {
  const { siteConfig } = useDocusaurusContext();

  return (
    <Layout
      title={`AI Textbook Assistant - ${siteConfig.title}`}
      description="AI-powered textbook assistant with structured responses and citations">
      <div style={{
        height: '100vh',
        display: 'flex',
        flexDirection: 'column'
      }}>
        <ChatInterface />
      </div>
    </Layout>
  );
};

export default AIChatPage;