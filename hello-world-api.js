const express = require('express');
const cors = require('cors');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Hello World endpoint
app.get('/hello', (req, res) => {
  const timestamp = new Date().toISOString();
  const response = {
    message: 'Hello World from API!',
    timestamp: timestamp,
    status: 'success',
    data: {
      greeting: 'Hello World',
      description: 'This is a simple Hello World API endpoint',
      version: '1.0.0'
    }
  };
  
  res.json(response);
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Root endpoint
app.get('/', (req, res) => {
  res.json({ 
    message: 'Hello World API is running!',
    endpoints: {
      hello: '/hello',
      health: '/health'
    }
  });
});

app.listen(PORT, () => {
  console.log(`Hello World API server running on http://localhost:${PORT}`);
  console.log(`Available endpoints:`);
  console.log(`  GET /hello - Hello World response`);
  console.log(`  GET /health - Health check`);
  console.log(`  GET / - API info`);
}); 