# LanceDB API with n8n Workflow

This project demonstrates a LanceDB API server with vector search capabilities and an n8n workflow that interacts with it.

## Setup

### Prerequisites
- Python 3.12+
- Node.js 20.19 (using nvm)
- n8n CLI

### Installation

1. **Set Node.js version:**
   ```bash
   nvm use 20.19
   ```

2. **Install Python dependencies:**
   ```bash
   cd LanceDB
   python3 -m pip install -r requirements.txt
   ```

3. **Install n8n globally:**
   ```bash
   npm install -g n8n
   ```

## Running the Application

### 1. Start the LanceDB API
```bash
cd LanceDB
python3 lance_code.py
```
The API will run on `http://127.0.0.1:8000`

### 2. Test the API
```bash
# Health check
curl http://127.0.0.1:8000/health

# Get stats
curl http://127.0.0.1:8000/stats

# Search knowledge
curl -X POST http://127.0.0.1:8000/manual_search \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the product return policy?"}'
```

### 3. Import the n8n Workflow
```bash
n8n import:workflow --input=LanceDB/lancedb-simple-workflow.json
```

### 4. Execute the Workflow
```bash
n8n execute --id=tMNH3hrYHzcH9Tlw
```

## API Endpoints

- `GET /health` - Health check with system status
- `GET /stats` - System statistics and metrics
- `POST /manual_search` - Vector search for knowledge
- `POST /validate_answer` - Answer validation
- `POST /log_interaction` - Log user interactions
- `POST /add_manual_knowledge` - Add new knowledge entries

## Workflow Structure

The n8n workflow consists of:

1. **Manual Trigger** - Starts the workflow execution
2. **Health Check** - Calls `/health` endpoint
3. **Get Stats** - Calls `/stats` endpoint  
4. **Process Results** - Combines and formats the responses

## Expected Output

When executed, the workflow returns:
```json
{
  "health": {
    "status": "healthy",
    "manual_entries": 1,
    "interactions": 1,
    "model": "sentence-transformers/all-MiniLM-L6-v2",
    "timestamp": "2025-07-28T12:24:42.082588"
  },
  "stats": {
    "manual_knowledge": {
      "total_entries": 1,
      "source_types": {
        "manual": 1
      },
      "avg_confidence": 0.800000011920929
    },
    "interactions": {
      "total_queries": 1,
      "sources_used": {
        "manual_knowledge": 1
      },
      "avg_confidence": 0.8
    }
  },
  "summary": {
    "api_status": "healthy",
    "total_manual_entries": 1,
    "total_interactions": 1,
    "avg_confidence": 0.800000011920929
  }
}
```

## Features

### LanceDB API
- **Vector Search**: Uses sentence transformers for semantic search
- **Knowledge Management**: Store and retrieve manual knowledge
- **Interaction Logging**: Track user queries and responses
- **Health Monitoring**: System status and statistics
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2`

### n8n Integration
- **CLI Execution**: Run workflows from command line
- **API Integration**: HTTP requests to LanceDB endpoints
- **Data Processing**: JavaScript code nodes for response formatting
- **Error Handling**: Graceful handling of API errors

## Files

- `lance_code.py` - FastAPI server with LanceDB integration
- `requirements.txt` - Python dependencies
- `lancedb-simple-workflow.json` - n8n workflow definition
- `README.md` - This documentation

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
```

## Troubleshooting

### IPv6/IPv4 Issues
If you encounter connection issues, ensure the API is bound to IPv4:
```python
uvicorn.run(app, host="127.0.0.1", port=8000)
```

### Workflow Execution
Make sure both the LanceDB API and n8n are running:
1. LanceDB API on `http://127.0.0.1:8000`
2. n8n CLI available in PATH
3. Node.js 20.19 active via nvm 