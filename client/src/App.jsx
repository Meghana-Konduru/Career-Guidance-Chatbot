import React, { useState } from 'react';
import LogoAnimation from './components/LogoAnimation';
import ChatInterface from './components/ChatInterface'; // Your chat component

function App() {
  const [showChat, setShowChat] = useState(false);

  const handleAnimationComplete = () => {
    setShowChat(true);
  };

  return (
    <div className="App">
      <LogoAnimation onAnimationComplete={handleAnimationComplete} />
      {showChat && <ChatInterface />}
    </div>
  );
}

export default App;