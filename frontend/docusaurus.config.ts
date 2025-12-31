import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'An AI-Native Textbook for Embodied Intelligence',
  favicon: 'img/favicon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://speck-kit-driven-development-hackathon.vercel.app',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'https://github.com/FarooqueMalik71', // Replace with your GitHub username/organization
  projectName: 'speck-kit-driven-development-hackathon', // Replace with your actual repository name

  onBrokenLinks: 'warn',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/FarooqueMalik71/speck-kit-driven-development-hackathon/edit/main/',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    // Replace with your project's social card
    image: 'img/docusaurus-social-card.jpg',
    // Pass environment variables to client
    customFields: {
      BACKEND_URL: process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000',
    },
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'Physical AI & Humanoid Robotics',
      logo: {
        alt: 'Physical AI & Humanoid Robotics Logo',
        src: 'img/logo.png',
        href: '/', // Optional: link to your website
        target: '_self', // Open in same tab
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'textbookSidebar',
          position: 'left',
          label: 'Textbook',
        },
        {to: '/ai-chat', label: 'AI Assistant', position: 'left'},
        {
          href: 'https://github.com/your-github-username/your-repo-name',
          label: 'GitHub',
          position: 'right',
        },
        {
          href: 'https://www.ros.org/',
          label: 'ROS 2',
          position: 'right',
        },
        {
          type: 'dropdown',
          label: 'More',
          position: 'right',
          items: [
            {to: '/docs/ai-assistant/using-full-book-qa', label: 'AI Guide'},
          ],
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Textbook',
          items: [
            {
              label: 'Introduction',
              to: '/docs/intro',
            },
            {
              label: 'Overview',
              to: '/docs/overview',
            },
            {
              label: 'Physical AI',
              to: '/docs/physical-ai/introduction',
            },
            {
              label: 'Humanoid Robotics',
              to: '/docs/humanoid-robotics/introduction',
            },
          ],
        },
        {
          title: 'Resources',
          items: [
            {
              label: 'AI Assistant',
              to: '/ai-chat',
            },
            {
              label: 'ROS 2 Guide',
              to: '/docs/ros2/introduction',
            },
            {
              label: 'Vision-Language-Action',
              to: '/docs/vla-systems/introduction',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/FarooqueMalik71',
            },
            {
              label: 'Twitter',
              href: 'https://x.com/FarooqueMalik71',
            },
            {
              label: 'Linkedin',
              href: 'https://www.linkedin.com/in/farooque-malik871/',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Physical AI & Humanoid Robotics Textbook.  Farooque | All Rights Reserved 2025`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
