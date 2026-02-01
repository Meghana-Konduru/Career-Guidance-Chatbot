// server/controllers/chatController.js
const axios = require('axios');

const FLASK_URL = process.env.FLASK_URL || 'http://localhost:8000/api/chat';

async function sendToFlask(req, res) {
  try {
    const { message } = req.body;
    if (!message) return res.status(400).json({ error: "Missing 'message' field" });

    // Forward to Flask AI engine
    const resp = await axios.post(FLASK_URL, { question: message }, {
      headers: { 'Content-Type': 'application/json' },
      timeout: 120000
    });

    // If Flask returns { answer: ... } we'll forward it. Otherwise forward whole body.
    const answer = resp.data?.answer ?? resp.data;
    res.json({ answer });
  } catch (err) {
    console.error('Error forwarding to Flask:', err?.response?.data ?? err.message);
    const status = err.response?.status || 500;
    res.status(status).json({ error: 'Failed to get response from AI engine', details: err?.response?.data ?? err.message });
  }
}

module.exports = { sendToFlask };
