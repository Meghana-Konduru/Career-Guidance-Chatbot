import React, { useState, useEffect } from 'react';
import LogoAnimation from './components/LogoAnimation';
import ChatInterface from './components/ChatInterface';
import './App.css';

// Add API configuration at the top
const API_URL = 'http://localhost:5000';

function App() {
  const [showChat, setShowChat] = useState(false);
  const [backendStatus, setBackendStatus] = useState('checking');

  // Add backend health check
  useEffect(() => {
    checkBackendHealth();
  }, []);

  const checkBackendHealth = async () => {
    try {
      const response = await fetch(`${API_URL}/health`);
      if (response.ok) {
        setBackendStatus('connected');
      } else {
        setBackendStatus('error');
      }
    } catch (error) {
      console.error('Backend connection failed:', error);
      setBackendStatus('error');
    }
  };

  const handleLogoComplete = () => {
    setShowChat(true);
  };

  // Add status display component
  const StatusIndicator = () => (
    <div className={`backend-status ${backendStatus}`}>
      {backendStatus === 'checking' && '🔍 Checking backend connection...'}
      {backendStatus === 'connected' && '✅ Backend connected'}
      {backendStatus === 'error' && '❌ Backend unavailable - make sure Python server is running on port 8000'}
    </div>
  );

  return (
    <div className="App">
      {!showChat && <LogoAnimation onAnimationComplete={handleLogoComplete} />}
      {showChat && (
        <>
          <StatusIndicator />
          <ChatInterface apiUrl={API_URL} backendStatus={backendStatus} />
        </>
      )}
    </div>
  );
}

export default App;