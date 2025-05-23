require('dotenv').config();
const express = require('express');
const cors = require('cors');
const axios = require('axios');
const multer = require('multer');
const { spawn } = require('child_process');
const fs = require('fs');
const { PineconeClient } = require('@pinecone-database/pinecone');

const app = express();
app.use(cors());
app.use(express.json());

const upload = multer({ dest: 'uploads/' });

// Initialize Pinecone client
const pinecone = new PineconeClient();
(async () => {
  try {
    await pinecone.init({
      apiKey: process.env.PINECONE_API_KEY || '',
      environment: process.env.PINECONE_ENV || 'us-east1-gcp'
    });
  } catch (e) {
    console.error('Failed to init Pinecone:', e.message);
  }
})();

let pineconeIndex;
(async () => {
  if (pinecone && process.env.PINECONE_INDEX) {
    pineconeIndex = pinecone.Index(process.env.PINECONE_INDEX);
  }
})();

app.post('/chat', async (req, res) => {
  try {
    const response = await axios.post(
      'https://api.openai.com/v1/chat/completions',
      req.body,
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
        },
      }
    );
    res.json({ reply: response.data.choices[0].message.content });
  } catch (error) {
    console.error('GPT Proxy Error:', error.message);
    res.status(500).json({ error: 'Proxy failed to reach OpenAI' });
  }
});

// Handle PDF uploads
app.post('/upload', upload.single('file'), async (req, res) => {
  try {
    const filePath = req.file.path;
    const python = spawn('python3', ['ocr.py', filePath]);
    let data = '';
    python.stdout.on('data', chunk => data += chunk.toString());
    python.stderr.on('data', chunk => console.error('OCR error:', chunk.toString()));
    python.on('close', async () => {
      const text = data.trim();
      if (!pineconeIndex) {
        return res.status(500).json({ error: 'Pinecone index not initialized' });
      }
      const embedRes = await axios.post(
        'https://api.openai.com/v1/embeddings',
        { input: text, model: 'text-embedding-ada-002' },
        { headers: { 'Authorization': `Bearer ${process.env.OPENAI_API_KEY}` } }
      );
      const vector = embedRes.data.data[0].embedding;
      await pineconeIndex.upsert([{ id: req.file.filename, values: vector, metadata: { text } }]);
      fs.unlinkSync(filePath);
      res.json({ success: true });
    });
  } catch (err) {
    console.error('Upload error:', err.message);
    res.status(500).json({ error: 'Failed to process PDF' });
  }
});

// Query Pinecone for similar text
app.post('/query', async (req, res) => {
  try {
    const question = req.body.question;
    if (!pineconeIndex) {
      return res.status(500).json({ error: 'Pinecone index not initialized' });
    }
    const embedRes = await axios.post(
      'https://api.openai.com/v1/embeddings',
      { input: question, model: 'text-embedding-ada-002' },
      { headers: { 'Authorization': `Bearer ${process.env.OPENAI_API_KEY}` } }
    );
    const vector = embedRes.data.data[0].embedding;
    const queryRes = await pineconeIndex.query({ vector, topK: 5, includeMetadata: true });
    res.json({ matches: queryRes.matches });
  } catch (err) {
    console.error('Query error:', err.message);
    res.status(500).json({ error: 'Failed to query Pinecone' });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🔥 GPT Proxy is live on port ${PORT}`);
});
