const express = require("express");
const axios = require("axios");
const cors = require("cors");
require("dotenv").config();

const app = express();
app.use(express.json());
app.use(cors());

app.get("/health", (req, res) => {
  res.json({ status: "ok" });
});

app.post("/api/chat", async (req, res) => {
  try {
    const r = await axios.post("http://localhost:8000/chat", {
      message: req.body.message
    });

    res.json({ answer: r.data.response });
  } catch (err) {
    console.log("Flask error:", err.message);
    res.status(500).json({ answer: "AI engine unreachable. Make sure Python server is running on port 8000." });
  }
});

app.listen(5000, () => console.log("🚀 Express running on 5000"));
