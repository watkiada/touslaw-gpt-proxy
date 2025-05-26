const http = require('http');
const https = require('https');
const fs = require('fs');

// Load environment variables from .env if present
function loadEnv() {
  try {
    const envData = fs.readFileSync('.env', 'utf8');
    envData.split(/\r?\n/).forEach(line => {
      const match = line.match(/^\s*([^#=]+)\s*=\s*(.*)\s*$/);
      if (match) {
        const key = match[1];
        const value = match[2];
        if (!process.env[key]) {
          process.env[key] = value;
        }
      }
    });
  } catch (err) {
    // .env is optional
  }
}
loadEnv();

const PORT = process.env.PORT || 3000;

function setCors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

const server = http.createServer((req, res) => {
  if (req.method === 'OPTIONS') {
    setCors(res);
    res.statusCode = 204;
    res.end();
    return;
  }

  if (req.url === '/chat' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => (body += chunk));
    req.on('end', () => {
      try {
        const requestData = JSON.parse(body);
        const openaiReq = https.request(
          'https://api.openai.com/v1/chat/completions',
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
            },
          },
          openaiRes => {
            let result = '';
            openaiRes.on('data', d => (result += d));
            openaiRes.on('end', () => {
              setCors(res);
              try {
                const data = JSON.parse(result);
                const reply =
                  data.choices &&
                  data.choices[0] &&
                  data.choices[0].message &&
                  data.choices[0].message.content;
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ reply }));
              } catch (e) {
                console.error('Failed to parse OpenAI response:', e.message);
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(
                  JSON.stringify({ error: 'Invalid response from OpenAI' })
                );
              }
            });
          }
        );

        openaiReq.on('error', err => {
          console.error('GPT Proxy Error:', err.message);
          setCors(res);
          res.writeHead(500, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Proxy failed to reach OpenAI' }));
        });

        openaiReq.write(JSON.stringify(requestData));
        openaiReq.end();
      } catch (err) {
        console.error('Request parsing error:', err.message);
        setCors(res);
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Invalid request body' }));
      }
    });
  } else {
    setCors(res);
    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Not found' }));
  }
});

server.listen(PORT, () => {
  console.log(`\uD83D\uDD25 GPT Proxy is live on port ${PORT}`);
});
