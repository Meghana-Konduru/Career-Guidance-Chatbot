import React, { useEffect, useState } from 'react';
import './LogoAnimation.css';

const LogoAnimation = ({ onAnimationComplete }) => {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false);
      setTimeout(() => {
        onAnimationComplete();
      }, 1000); // Wait for fade out animation to complete
    }, 3000); // Show logo for 3 seconds

    return () => clearTimeout(timer);
  }, [onAnimationComplete]);

  if (!isVisible) return null;

  return (
    <div className="logo-animation">
      <div className="logo-content">
        <div className="logo-text">CareerGuide</div>
        <div className="logo-subtitle">Your AI Career Assistant</div>
      </div>
    </div>
  );
};

export default LogoAnimation;