import React, { useState, useRef, useEffect } from "react";

function Chat() {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "Hello! Ask me anything about careers or skills." }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text) return;

    setMessages((m) => [...m, { sender: "user", text }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });

      const data = await res.json();
      const botReply = data.answer || data.response || "No response received.";

      setMessages((m) => [...m, { sender: "bot", text: botReply }]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        { sender: "bot", text: "Error connecting to the server." },
      ]);
    }

    setLoading(false);
  };

  const handleSend = (e) => {
    e.preventDefault();
    sendMessage();
  };

  return (
    <div className="chat-box">
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`bubble ${msg.sender}`}>
            {msg.text}
          </div>
        ))}

        {loading && <div className="bubble bot">Typing...</div>}

        <div ref={chatEndRef} />
      </div>

      <form className="input-area" onSubmit={handleSend}>
        <input
          type="text"
          placeholder="Ask a career question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}

export default Chat;
