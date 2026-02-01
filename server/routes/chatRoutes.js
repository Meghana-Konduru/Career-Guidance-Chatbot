// server/routes/chatRoutes.js
const express = require('express');
const router = express.Router();
const { sendToFlask } = require('../controllers/chatController');

router.post('/', sendToFlask);

module.exports = router;
