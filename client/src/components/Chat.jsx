import React, { useState } from "react";
import axios from "axios";

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const sendMessage = async () => {
    if (!input.trim()) return;

    setMessages(prev => [...prev, { sender: "user", text: input }]);

    try {
      const res = await axios.post("http://localhost:5000/api/chat", {
        question: input
      });

      setMessages(prev => [...prev, { sender: "ai", text: res.data.answer }]);
    } catch {
      setMessages(prev => [...prev, {
        sender: "ai",
        text: "Server error. Try again."
      }]);
    }

    setInput("");
  };

  return (
    <div className="chat-container">
      <div className="chat-box">
        {messages.map((m, i) => (
          <p key={i} className={m.sender}>
            <strong>{m.sender === "user" ? "You: " : "AI: "}</strong>
            {m.text}
          </p>
        ))}
      </div>

      <div className="input-row">
        <input
          value={input}
          placeholder="Ask anything about your career..."
          onChange={e => setInput(e.target.value)}
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}
