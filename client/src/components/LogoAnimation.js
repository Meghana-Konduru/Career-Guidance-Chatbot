import React, { useEffect, useState } from 'react';
import './LogoAnimation.css';

const LogoAnimation = ({ onAnimationComplete }) => {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false);
      setTimeout(() => {
        if (onAnimationComplete) {
          onAnimationComplete();
        }
      }, 1000);
    }, 3000);

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