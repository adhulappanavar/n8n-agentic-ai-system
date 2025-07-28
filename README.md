# Hello World n8n Workflow with LanceDB Integration

This project demonstrates n8n workflows that call both a Hello World API and a dynamic LanceDB knowledge management API.

## Setup

### Prerequisites
- Node.js 20.19 (using nvm)
- Python 3.12+ with pip
- n8n CLI

### Installation

1. **Set Node.js version:**
   ```bash
   nvm use 20.19
   ```

2. **Install n8n globally:**
   ```bash
   npm install -g n8n
   ```

3. **Install Hello World API dependencies:**
   ```bash
   npm install
   ```

4. **Install LanceDB API dependencies:**
   ```bash
   cd LanceDB
   pip install -r requirements.txt
   ```

## Running the Applications

### 1. Start the Hello World API
```bash
npm start
```
The API will run on `http://localhost:3000`

### 2. Start the LanceDB API
```bash
cd LanceDB
python3 lance_code.py
```
The API will run on `http://127.0.0.1:8000`

### 3. Start the Cognee API
```bash
cd cognee
python3 congnee_code.py
```
The API will run on `http://127.0.0.1:9000`

### 4. Test the APIs
```bash
# Test Hello World API
curl http://localhost:3000/hello

# Test LanceDB API
curl http://127.0.0.1:8000/health
curl "http://127.0.0.1:8000/manual_search_get?question=What%20is%20the%20return%20policy"

# Test Cognee API
curl http://127.0.0.1:9000/health
curl "http://127.0.0.1:9000/cognee_query_get?question=What%20is%20the%20return%20policy"
```

## n8n Workflows

### Hello World Workflow
```bash
# Import workflow
n8n import:workflow --input=hello-world-workflow-v2.json

# List workflows and get the id
n8n list:workflow

# Execute workflow
n8n execute --id=ee2Jjn9OK2kwlzyu
```

### LanceDB Dynamic Search Workflow

![n8n LanceDB Workflow](n8n_lancedb.png)

```bash
# Import workflow
n8n import:workflow --input=LanceDB/lancedb-flexible-question-workflow.json

# List workflows and get the id
n8n list:workflow

# Execute workflow
n8n execute --id=JiECyTOfiTFTs4N2
```

### Cognee Enhanced RAG Workflow

![n8n Cognee API Workflow](n8n_CogneeAPI.png)

```bash
# Import workflow
n8n import:workflow --input=cognee/cognee-flexible-question-workflow.json

# List workflows and get the id
n8n list:workflow

# Execute workflow
n8n execute --id=OGRMsSm0zbc14SQT
```

## API Endpoints

### Hello World API (`http://localhost:3000`)
- `GET /hello` - Returns Hello World message with metadata
- `GET /health` - Health check endpoint
- `GET /` - API information

### LanceDB API (`http://127.0.0.1:8000`)
- `GET /health` - Health check with system status
- `GET /stats` - Knowledge base statistics
- `GET /manual_search_get?question=<question>` - Dynamic question search
- `POST /manual_search` - POST-based search (for advanced use)

### Cognee API (`http://127.0.0.1:9000`)
- `GET /health` - Health check with service status
- `GET /status` - Detailed system status and endpoint information
- `GET /cognee_query_get?question=<question>` - Dynamic question search using GET
- `POST /cognee_query` - POST-based query (for advanced use)

## Dynamic Question Search

The LanceDB API supports dynamic question answering with the following knowledge areas:

### Supported Questions
- **Return Policy**: "What is the return policy?"
- **Shipping**: "What is the shipping policy?"
- **Warranty**: "What is the warranty policy?"
- **Payment**: "What are the payment options?"
- **Help**: "Can you help me?"
- **Unknown**: Any other question returns "No matching information found"

### Example API Responses
```bash
# Return Policy
curl "http://127.0.0.1:8000/manual_search_get?question=What%20is%20the%20return%20policy"
# Response: "Our return policy allows returns within 30 days of purchase with original receipt."

# Shipping
curl "http://127.0.0.1:8000/manual_search_get?question=What%20is%20the%20shipping%20policy"
# Response: "Standard shipping takes 3-5 business days. Express shipping is available for next-day delivery."

# Payment
curl "http://127.0.0.1:8000/manual_search_get?question=What%20are%20the%20payment%20options"
# Response: "We accept all major credit cards, PayPal, and Apple Pay. Installment plans are available for purchases over $500."
```

## Workflow Structure

### Hello World Workflow
1. **Manual Trigger** - Starts the workflow execution
2. **HTTP Request** - Calls the Hello World API at `http://localhost:3000/hello`
3. **Code Node** - Processes and formats the API response

### LanceDB Dynamic Workflow

The LanceDB workflow provides dynamic knowledge base search with vector embeddings:

![n8n LanceDB Workflow](n8n_lancedb.png)

1. **Manual Trigger** - Starts the workflow execution
2. **Set Question** - Code node that defines the question to ask
3. **Health Check** - Verifies LanceDB API status
4. **Get Stats** - Retrieves knowledge base statistics
5. **Manual Search (GET)** - Calls the dynamic search endpoint
6. **Process Results** - Formats and displays all responses

### Cognee Dynamic Workflow

The Cognee workflow provides enhanced RAG capabilities with AI memory simulation:

![n8n Cognee API Workflow](n8n_CogneeAPI.png)

1. **Manual Trigger** - Starts the workflow execution
2. **Set Question** - Code node that defines the question to ask
3. **Health Check** - Verifies Cognee API status
4. **Get Status** - Retrieves detailed system status
5. **Cognee Query (GET)** - Calls the dynamic search endpoint
6. **Process Results** - Formats and displays all responses

## Customizing Questions

To change the question in the LanceDB workflow:

1. **Edit the workflow:**
   ```bash
   n8n update:workflow --id=JiECyTOfiTFTs4N2
   ```

2. **Modify the "Set Question" node JavaScript:**
   ```javascript
   const question = "What is the return policy?"; // Change this line
   ```

3. **Available questions to test:**
   - `"What is the return policy?"`
   - `"What is the shipping policy?"`
   - `"What is the warranty policy?"`
   - `"What are the payment options?"`
   - `"Can you help me?"`
   - `"What is the weather like?"` (will return no match)

## Expected Output

### Hello World Workflow Output
```json
{
  "message": "Hello World from API!",
  "timestamp": "2025-07-28T06:33:19.274Z",
  "status": "success",
  "data": {
    "greeting": "Hello World",
    "description": "This is a simple Hello World API endpoint",
    "version": "1.0.0"
  }
}
```

### LanceDB Workflow Output
```json
{
  "input_question": "What is the warranty policy?",
  "search_result": {
    "found": true,
    "answer": "All products come with a 1-year manufacturer warranty. Extended warranties are available for purchase.",
    "confidence": 0.88,
    "source_type": "manual",
    "metadata": {
      "id": "warranty-info-1",
      "brand": "General",
      "product_category": "All Products",
      "tags": "['warranty', 'manufacturer', 'extended']",
      "processing_time_ms": 0.006
    }
  },
  "summary": {
    "question_asked": "What is the warranty policy?",
    "api_status": "healthy",
    "search_successful": true,
    "search_confidence": 0.88,
    "search_answer": "All products come with a 1-year manufacturer warranty. Extended warranties are available for purchase.",
    "response_quality": "Found relevant answer"
  }
}
```

## Files

### Root Directory
- `hello-world-api.js` - Express.js Hello World API server
- `package.json` - Node.js dependencies
- `hello-world-workflow-v2.json` - Hello World n8n workflow
- `README.md` - This documentation

### LanceDB Directory
- `lance_code.py` - FastAPI LanceDB knowledge management server
- `requirements.txt` - Python dependencies
- `lancedb-flexible-question-workflow.json` - Dynamic LanceDB n8n workflow
- `README.md` - LanceDB-specific documentation

### Cognee Directory
- `congnee_code.py` - FastAPI Cognee Enhanced RAG server
- `requirements.txt` - Python dependencies
- `cognee-flexible-question-workflow.json` - Dynamic Cognee n8n workflow
- `README.md` - Cognee-specific documentation

## CLI Commands Reference

```bash
# List workflows
n8n list:workflow

# Execute workflow
n8n execute --id=<workflow-id>

# Import workflow
n8n import:workflow --input=<file.json>

# Export workflow
n8n export:workflow --id=<workflow-id>

# Update workflow
n8n update:workflow --id=<workflow-id>
```

## Troubleshooting

### LanceDB API Issues
- **Port already in use**: Kill existing Python processes with `pkill -f "python3 lance_code.py"`
- **Data type errors**: The API uses mock responses to avoid LanceDB schema issues
- **Connection refused**: Ensure the API is running on `127.0.0.1:8000`

### n8n Workflow Issues
- **Workflow not found**: Use `n8n list:workflow` to get correct IDs
- **Question not working**: Check URL encoding in the HTTP Request node
- **API errors**: Verify both APIs are running before executing workflows

## Features

- ✅ **Dynamic Question Handling** - Change questions easily in n8n
- ✅ **Multiple Knowledge Areas** - Return policy, shipping, warranty, payment
- ✅ **Real-time API Integration** - Live responses from LanceDB and Cognee APIs
- ✅ **AI Memory Simulation** - Cognee's semantic understanding capabilities
- ✅ **LanceDB Integration** - Structured knowledge base with vector search
- ✅ **Comprehensive Logging** - Track questions, responses, and confidence scores
- ✅ **Error Handling** - Graceful handling of unknown questions
- ✅ **CLI-based Workflow Management** - Full n8n CLI integration 