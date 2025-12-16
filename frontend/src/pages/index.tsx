import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <div className="row">
          <div className="col col--6">
            <Heading as="h1" className="hero__title">
              Master AI Robotics
            </Heading>
            <p className="hero__subtitle">
              An AI-Native Textbook for Embodied Intelligence.
              Learn Physical AI, Humanoid Robotics, and Vision-Language-Action systems
              with interactive AI assistance.
            </p>
            <div className={styles.buttons}>
              <Link
                className="button button--secondary button--lg"
                to="/docs/intro">
                Start Learning →
              </Link>
              <Link
                className="button button--primary button--lg margin-left--md"
                to="/ai-chat">
                Try AI Assistant
              </Link>
            </div>
          </div>
          <div className="col col--6">
            <div className={styles.illustration}>
              <img
                src="/img/undraw_docusaurus_react.png"
                alt="AI Robotics Illustration"
                className={styles.heroIllustration}
              />
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

const FeatureList = [
  {
    title: 'Physical AI Fundamentals',
    description: (
      <>
        Master the integration of perception, reasoning, and action in physical environments.
        Understand how AI systems interact with the real world through sensors and actuators.
      </>
    ),
  },
  {
    title: 'Humanoid Robotics',
    description: (
      <>
        Learn about humanoid robot design, control systems, and applications in human-centered environments.
        Explore the challenges of bipedal locomotion and human-robot interaction.
      </>
    ),
  },
  {
    title: 'AI-Powered Learning',
    description: (
      <>
        Interactive AI assistant with full-book and selected-text Q&A modes.
        Personalized learning paths and real-time translation capabilities.
      </>
    ),
  },
  {
    title: 'ROS 2 Integration',
    description: (
      <>
        Practical implementation of robotics concepts using ROS 2 frameworks.
        Learn to build and deploy real robotic systems with industry-standard tools.
      </>
    ),
  },
  {
    title: 'Vision-Language-Action Systems',
    description: (
      <>
        Understand modern approaches to embodied intelligence that combine
        visual perception, natural language understanding, and physical action.
      </>
    ),
  },
  {
    title: 'Industry Applications',
    description: (
      <>
        Explore real-world applications of AI robotics in manufacturing,
        healthcare, service industries, and research environments.
      </>
    ),
  },
];

function Feature({ title, description }) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center padding-horiz--md">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Master AI Robotics`}
      description="AI-Native Textbook for Physical AI & Humanoid Robotics">
      <HomepageHeader />
      <main>
        <section className={styles.features}>
          <div className="container padding-vert--lg">
            <div className="text--center padding-bottom--lg">
              <Heading as="h2" className={styles.sectionTitle}>
                What You'll Learn
              </Heading>
              <p className={styles.sectionSubtitle}>
                Comprehensive coverage of cutting-edge AI robotics concepts
              </p>
            </div>
            <div className="row">
              {FeatureList.map((props, idx) => (
                <Feature key={idx} {...props} />
              ))}
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}
