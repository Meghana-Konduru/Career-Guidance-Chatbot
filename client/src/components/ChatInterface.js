import React, { useState, useRef, useEffect } from 'react';
import './ChatInterface.css';

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    { text: "Hello! I'm your career guidance assistant. I can help you with career planning, skills development, and professional growth. What would you like to know today?", isUser: false }
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    const message = inputText.trim();
    if (!message || isLoading) return;

    // Add user message to chat
    const userMessage = { text: message, isUser: true };
    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      // Send message to backend
      const response = await fetch('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message
        })
      });

      const data = await response.json();
      
      // Add bot response to chat
      const botMessage = { text: data.answer, isUser: false };
      setMessages(prev => [...prev, botMessage]);
      
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = { 
        text: "Sorry, I'm having trouble connecting to the server. Please try again later.", 
        isUser: false 
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h1>Career Guidance Assistant</h1>
        <p>Ask me anything about careers and opportunities</p>
      </div>
      
      <div className="chat-messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.isUser ? 'user' : 'bot'}`}>
            <div className="message-bubble">
              {msg.text}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="message bot">
            <div className="message-bubble typing-indicator">
              <div className="typing-dots">
                <div className="dot"></div>
                <div className="dot"></div>
                <div className="dot"></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input">
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask about careers, skills, jobs..."
          disabled={isLoading}
        />
        <button 
          onClick={handleSend} 
          disabled={isLoading || !inputText.trim()}
        >
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </div>
    </div>
  );
};

export default ChatInterface;