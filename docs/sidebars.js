// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Physical AI Fundamentals',
      items: ['physical-ai/overview', 'physical-ai/embodied-intelligence', 'physical-ai/simulation'],
    },
    {
      type: 'category',
      label: 'Humanoid Robotics',
      items: ['humanoid-robotics/overview', 'humanoid-robotics/kinematics', 'humanoid-robotics/control'],
    },
    {
      type: 'category',
      label: 'Vision-Language-Action Systems',
      items: ['vla-systems/overview', 'vla-systems/perception', 'vla-systems/integration'],
    },
    {
      type: 'category',
      label: 'Conversational Robotics',
      items: ['conversational-robotics/overview', 'conversational-robotics/nlp', 'conversational-robotics/integration'],
    },
    {
      type: 'category',
      label: 'ROS 2 Integration',
      items: ['ros2/overview', 'ros2/basics', 'ros2/advanced'],
    },
  ],
};

export default sidebars;