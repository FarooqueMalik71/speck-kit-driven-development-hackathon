import React from 'react';
import './styles.css';

const ContentTags = ({ tags = [], category = "general" }) => {
  // Define tag categories and their styling
  const tagCategories = {
    'ros2': {
      color: 'blue',
      label: 'ROS 2',
      description: 'Robot Operating System 2 concepts'
    },
    'embodied-ai': {
      color: 'green',
      label: 'Embodied AI',
      description: 'AI systems with physical embodiment'
    },
    'humanoid-robotics': {
      color: 'purple',
      label: 'Humanoid Robotics',
      description: 'Human-like robot systems and control'
    },
    'physical-ai': {
      color: 'yellow',
      label: 'Physical AI',
      description: 'AI systems interacting with physical world'
    },
    'vla': {
      color: 'red',
      label: 'VLA',
      description: 'Vision-Language-Action systems'
    },
    'conversational-robotics': {
      color: 'indigo',
      label: 'Conversational Robotics',
      description: 'Natural language interaction with robots'
    },
    'simulation': {
      color: 'teal',
      label: 'Simulation',
      description: 'Robot simulation and modeling'
    },
    'control': {
      color: 'orange',
      label: 'Control',
      description: 'Robot control systems and algorithms'
    },
    'kinematics': {
      color: 'pink',
      label: 'Kinematics',
      description: 'Robot motion and geometry'
    },
    'perception': {
      color: 'cyan',
      label: 'Perception',
      description: 'Robot sensing and understanding'
    }
  };

  // Function to get tag styling based on category
  const getTagStyle = (tag) => {
    const categoryInfo = tagCategories[tag] || { color: 'gray', label: tag, description: 'General concept' };
    return categoryInfo;
  };

  return (
    <div className="content-tags">
      <h4>Concept Tags</h4>
      <div className="tags-container">
        {tags.map((tag, index) => {
          const tagInfo = getTagStyle(tag);
          return (
            <span
              key={index}
              className={`tag tag-${tagInfo.color}`}
              title={tagInfo.description}
            >
              {tagInfo.label}
            </span>
          );
        })}
      </div>
    </div>
  );
};

export default ContentTags;