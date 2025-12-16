import React from 'react';
import OriginalLayout from '@theme-original/Layout';
import FloatingAIButton from '@site/src/components/FloatingAIButton/FloatingAIButton';

export default function Layout(props) {
  return (
    <>
      <OriginalLayout {...props} />
      <FloatingAIButton />
    </>
  );
}