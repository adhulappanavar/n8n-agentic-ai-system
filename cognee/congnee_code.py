from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
import openai
import uvicorn
import asyncio
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load OpenAI Key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY", "sk-test-key-placeholder")

app = FastAPI(title="Cognee Enhanced RAG API", version="1.0.0")

# Configuration
LANCE_DB_API = "http://127.0.0.1:8000/manual_search"  # Updated LanceDB service URL

class QueryRequest(BaseModel):
    question: str
    context: Optional[Dict[str, Any]] = {}

class CogneeResponse(BaseModel):
    answer: str
    cognee_answer: str
    cognee_confidence: float
    used_context: bool
    ai_memory_used: bool
    source: str

async def enhanced_cognee_query(question: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Enhanced Cognee integration that mimics the real system behavior
    """
    try:
        logger.info(f"🧠 Processing Cognee query: '{question}'")
        
        # Step 1: Try to get context from manual knowledge first
        context_answer = ""
        try:
            # Use GET endpoint instead of POST
            encoded_question = requests.utils.quote(question)
            context_resp = requests.get(
                f"http://127.0.0.1:8000/manual_search_get?question={encoded_question}", 
                timeout=5
            ).json()
            
            if context_resp.get("found", False) and context_resp.get("confidence", 0) > 0.5:
                context_answer = context_resp.get("answer", "")
                logger.info("✅ Found context from manual knowledge")
            else:
                logger.info("⚠️ No high-confidence manual knowledge found")
                
        except Exception as e:
            logger.warning(f"⚠️ Manual knowledge lookup failed: {e}")
        
        # Step 2: Prepare AI memory simulation (since real Cognee may have API issues)
        ai_memory_context = ""
        ai_memory_used = False
        
        try:
            # Simulate Cognee's semantic understanding
            # In a real implementation, this would call: await cognee.search(question)
            ai_memory_context = f"AI Memory Context: Based on knowledge graphs and semantic understanding of '{question}'"
            ai_memory_used = True
            logger.info("🧠 Simulated AI memory processing")
            
        except Exception as e:
            logger.warning(f"⚠️ AI memory simulation failed: {e}")
        
        # Step 3: Generate intelligent response using OpenAI (with fallback)
        try:
            if openai.api_key and openai.api_key != "sk-test-key-placeholder":
                # Use real OpenAI API
                system_prompt = (
                    "You are an intelligent RAG agent powered by Cognee AI memory and LanceDB knowledge. "
                    "Provide helpful, accurate answers based on the context provided. "
                    "If context is available, prioritize it. If not, use your knowledge but mention limitations."
                )
                
                user_prompt = f"""
Context from Manual Knowledge: {context_answer}

AI Memory Context: {ai_memory_context}

User Question: {question}

Please provide a comprehensive answer:
"""
                
                # Use updated OpenAI API
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                
                answer = response.choices[0].message.content.strip()
                confidence = 0.8 if context_answer else 0.6
                
                logger.info("✅ Generated response using OpenAI")
                
            else:
                # Fallback response when OpenAI is not available
                if context_answer:
                    answer = f"Based on our knowledge base: {context_answer}"
                    confidence = 0.7
                elif ai_memory_used:
                    answer = f"Based on AI memory analysis: I understand you're asking about '{question}'. While I don't have specific information in our knowledge base, I can help you with general guidance on this topic."
                    confidence = 0.4
                else:
                    answer = "I apologize, but I don't have enough information to provide a comprehensive answer to your question. Please try rephrasing or contact support for assistance."
                    confidence = 0.2
                
                logger.info("✅ Generated fallback response (OpenAI not available)")
        
        except Exception as e:
            logger.error(f"❌ Error generating response: {e}")
            # Final fallback
            if context_answer:
                answer = f"Based on our knowledge: {context_answer}"
                confidence = 0.6
            else:
                answer = "I encountered an error processing your request. Please try again or contact support."
                confidence = 0.1
        
        return {
            "answer": answer,
            "cognee_answer": answer,  # For n8n workflow compatibility
            "cognee_confidence": confidence,
            "used_context": bool(context_answer),
            "ai_memory_used": ai_memory_used,
            "source": "cognee_ai_memory" if ai_memory_used else "fallback",
            "metadata": {
                "manual_context_found": bool(context_answer),
                "ai_memory_active": ai_memory_used,
                "openai_used": openai.api_key != "sk-test-key-placeholder",
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Critical error in Cognee query: {e}")
        return {
            "answer": "System error occurred. Please contact support.",
            "cognee_answer": "System error occurred. Please contact support.",
            "cognee_confidence": 0.1,
            "used_context": False,
            "ai_memory_used": False,
            "source": "error",
            "error": str(e)
        }

@app.post("/cognee_query", response_model=CogneeResponse)
async def cognee_query_endpoint(req: QueryRequest):
    """Enhanced Cognee query endpoint"""
    try:
        result = await enhanced_cognee_query(req.question, req.context)
        
        return CogneeResponse(
            answer=result["answer"],
            cognee_answer=result["cognee_answer"],
            cognee_confidence=result["cognee_confidence"],
            used_context=result["used_context"],
            ai_memory_used=result["ai_memory_used"],
            source=result["source"]
        )
        
    except Exception as e:
        logger.error(f"❌ Error in cognee query endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Cognee query error: {str(e)}")

@app.post("/query")  # Legacy endpoint for compatibility
async def legacy_query_endpoint(req: QueryRequest):
    """Legacy query endpoint for backward compatibility"""
    try:
        result = await enhanced_cognee_query(req.question, req.context)
        return {"answer": result["answer"], "used_context": result["used_context"]}
        
    except Exception as e:
        logger.error(f"❌ Error in legacy query: {e}")
        raise HTTPException(status_code=500, detail=f"Query error: {str(e)}")

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "cognee_enhanced_rag",
        "openai_configured": openai.api_key != "sk-test-key-placeholder",
        "manual_knowledge_endpoint": LANCE_DB_API,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/status")
def get_status():
    """Get detailed system status"""
    try:
        # Test manual knowledge connection
        manual_kb_status = "unknown"
        try:
            resp = requests.get("http://127.0.0.1:8000/health", timeout=3)
            manual_kb_status = "connected" if resp.status_code == 200 else "error"
        except:
            manual_kb_status = "disconnected"
        
        return {
            "cognee_service": "active",
            "openai_api": "configured" if openai.api_key != "sk-test-key-placeholder" else "placeholder",
            "manual_knowledge_service": manual_kb_status,
            "ai_memory_simulation": "active",
            "endpoints": {
                "cognee_query": "/cognee_query",
                "legacy_query": "/query",
                "health": "/health",
                "status": "/status",
                "cognee_query_get": "/cognee_query_get"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check error: {str(e)}")

@app.get("/cognee_query_get")
async def cognee_query_get(question: str):
    """Cognee query endpoint using GET request with query parameter"""
    try:
        logger.info(f"🧠 Processing Cognee GET query: '{question}'")
        
        # Use the same enhanced query function
        result = await enhanced_cognee_query(question, {})
        
        return {
            "answer": result["answer"],
            "cognee_answer": result["cognee_answer"],
            "cognee_confidence": result["cognee_confidence"],
            "used_context": result["used_context"],
            "ai_memory_used": result["ai_memory_used"],
            "source": result["source"],
            "metadata": result.get("metadata", {})
        }
        
    except Exception as e:
        logger.error(f"❌ Error in cognee GET query: {e}")
        raise HTTPException(status_code=500, detail=f"Cognee GET query error: {str(e)}")

if __name__ == "__main__":
    logger.info("🚀 Starting Cognee Enhanced RAG Service")
    logger.info(f"🔑 OpenAI API configured: {openai.api_key != 'sk-test-key-placeholder'}")
    logger.info(f"🔗 Manual Knowledge endpoint: {LANCE_DB_API}")
    uvicorn.run(app, host="0.0.0.0", port=9000)
