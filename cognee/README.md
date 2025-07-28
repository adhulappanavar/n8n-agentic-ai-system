# Cognee Enhanced RAG API

This directory contains the Cognee Enhanced RAG (Retrieval-Augmented Generation) API that integrates with LanceDB for knowledge management and provides intelligent question answering capabilities.

## Setup

### Prerequisites
- Python 3.12+ with pip
- LanceDB API running on `http://127.0.0.1:8000`

### Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set OpenAI API key (optional):**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   ```

## Running the Cognee API

### Start the API
```bash
python3 congnee_code.py
```
The API will run on `http://127.0.0.1:9000`

### Test the API
```bash
# Health check
curl http://127.0.0.1:9000/health

# Status check
curl http://127.0.0.1:9000/status

# Query with GET endpoint
curl "http://127.0.0.1:9000/cognee_query_get?question=What%20is%20the%20return%20policy"
```

## API Endpoints

### Core Endpoints
- `GET /health` - Health check with service status
- `GET /status` - Detailed system status and endpoint information
- `GET /cognee_query_get?question=<question>` - **Dynamic question search using GET**
- `POST /cognee_query` - POST-based query (for advanced use)
- `POST /query` - Legacy query endpoint

### Enhanced Features
- **AI Memory Simulation** - Simulates Cognee's semantic understanding
- **Manual Knowledge Integration** - Connects to LanceDB for context retrieval
- **OpenAI Integration** - Uses GPT-3.5-turbo for intelligent responses (when configured)
- **Fallback Responses** - Provides intelligent responses even without OpenAI

## Dynamic Question Search

The Cognee API supports dynamic question answering with integration to LanceDB knowledge base:

### Supported Questions
- **Return Policy**: "What is the return policy?"
- **Shipping**: "What is the shipping policy?"
- **Warranty**: "What is the warranty policy?"
- **Payment**: "What are the payment options?"
- **General AI Questions**: "What is artificial intelligence?"
- **Machine Learning**: "How does machine learning work?"

### Example API Responses
```bash
# Return Policy (with context)
curl "http://127.0.0.1:9000/cognee_query_get?question=What%20is%20the%20return%20policy"
# Response: "Based on our knowledge base: Our return policy allows returns within 30 days..."

# Shipping (with context)
curl "http://127.0.0.1:9000/cognee_query_get?question=What%20is%20the%20shipping%20policy"
# Response: "Based on our knowledge base: Standard shipping takes 3-5 business days..."

# AI Question (without context)
curl "http://127.0.0.1:9000/cognee_query_get?question=What%20is%20artificial%20intelligence"
# Response: "Based on AI memory analysis: I understand you're asking about..."
```

## n8n Workflow Integration

### Import Cognee Workflow
```bash
n8n import:workflow --input=cognee/cognee-flexible-question-workflow.json
```

### Execute Workflow
```bash
n8n execute --id=OGRMsSm0zbc14SQT
```

### Workflow Structure
1. **Manual Trigger** - Starts the workflow execution
2. **Set Question** - Code node that defines the question to ask
3. **Health Check** - Verifies Cognee API status
4. **Get Status** - Retrieves detailed system status
5. **Cognee Query (GET)** - Calls the dynamic search endpoint
6. **Process Results** - Formats and displays all responses

## Customizing Questions

To change the question in the Cognee workflow:

1. **Edit the workflow:**
   ```bash
   n8n update:workflow --id=OGRMsSm0zbc14SQT
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
   - `"What is artificial intelligence?"`
   - `"How does machine learning work?"`

## Expected Output

### Cognee Workflow Output
```json
{
  "input_question": "What is the return policy?",
  "cognee_result": {
    "answer": "Based on our knowledge base: Our return policy allows returns within 30 days of purchase with original receipt.",
    "cognee_answer": "Based on our knowledge base: Our return policy allows returns within 30 days of purchase with original receipt.",
    "cognee_confidence": 0.7,
    "used_context": true,
    "ai_memory_used": true,
    "source": "cognee_ai_memory",
    "metadata": {
      "manual_context_found": true,
      "ai_memory_active": true,
      "openai_used": false,
      "timestamp": "2025-07-28T13:10:20.176403"
    }
  },
  "summary": {
    "question_asked": "What is the return policy?",
    "cognee_service_status": "healthy",
    "openai_configured": false,
    "manual_kb_connected": true,
    "cognee_confidence": 0.7,
    "ai_memory_used": true,
    "context_used": true,
    "cognee_answer": "Based on our knowledge base: Our return policy allows returns within 30 days of purchase with original receipt.",
    "response_quality": "Medium confidence"
  }
}
```

## Files

- `congnee_code.py` - FastAPI Cognee Enhanced RAG server
- `requirements.txt` - Python dependencies
- `cognee-flexible-question-workflow.json` - Dynamic Cognee n8n workflow
- `README.md` - This documentation

## Features

- ✅ **Dynamic Question Handling** - Change questions easily in n8n
- ✅ **LanceDB Integration** - Connects to manual knowledge base
- ✅ **AI Memory Simulation** - Simulates semantic understanding
- ✅ **OpenAI Integration** - Uses GPT-3.5-turbo when configured
- ✅ **Fallback Responses** - Intelligent responses without OpenAI
- ✅ **Context Retrieval** - Finds relevant information from knowledge base
- ✅ **Confidence Scoring** - Provides confidence levels for responses
- ✅ **Comprehensive Logging** - Tracks queries, responses, and metadata
- ✅ **CLI-based Workflow Management** - Full n8n CLI integration

## Troubleshooting

### Cognee API Issues
- **Port already in use**: Kill existing Python processes with `pkill -f "python3 congnee_code.py"`
- **LanceDB connection failed**: Ensure LanceDB API is running on `127.0.0.1:8000`
- **OpenAI not configured**: API works with fallback responses even without OpenAI key

### n8n Workflow Issues
- **Workflow not found**: Use `n8n list:workflow` to get correct IDs
- **Question not working**: Check URL encoding in the HTTP Request node
- **API errors**: Verify both Cognee and LanceDB APIs are running

## Architecture

The Cognee API implements a multi-layered approach:

1. **Question Processing** - Receives and processes user questions
2. **Context Retrieval** - Queries LanceDB for relevant knowledge
3. **AI Memory Simulation** - Simulates semantic understanding
4. **Response Generation** - Uses OpenAI or fallback for intelligent responses
5. **Result Formatting** - Returns structured responses with metadata

This creates a robust RAG system that combines structured knowledge (LanceDB) with intelligent processing (Cognee AI memory simulation). 