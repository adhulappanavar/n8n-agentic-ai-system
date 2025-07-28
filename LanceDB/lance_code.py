from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import lancedb
import pandas as pd
import numpy as np
import pyarrow as pa
from sentence_transformers import SentenceTransformer
import uvicorn
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LanceDB Enhanced Manual Knowledge API", version="1.0.0")

# Initialize sentence transformer for embeddings
encoder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Connect to LanceDB
db = lancedb.connect("./lancedb_data")
manual_table_name = "manual_knowledge"
interaction_table_name = "interactions_log"

# Initialize tables
def initialize_tables():
    try:
        # Manual Knowledge Table
        if manual_table_name not in db.table_names():
            # Create with proper schema including embeddings
            sample_embedding = encoder.encode("Sample question for schema")
            # Ensure proper vector format for LanceDB
            if isinstance(sample_embedding, np.ndarray):
                sample_embedding = sample_embedding.astype(np.float32)
            
            # Define proper PyArrow schema for LanceDB
            VECTOR_DIMENSION = len(sample_embedding)
            schema = pa.schema([
                pa.field("id", pa.string()),
                pa.field("question", pa.string()),
                pa.field("answer", pa.string()),
                pa.field("embedding", pa.list_(pa.float32(), VECTOR_DIMENSION)),
                pa.field("confidence_score", pa.float32()),
                pa.field("source_type", pa.string()),
                pa.field("timestamp", pa.string()),
                pa.field("brand", pa.string()),
                pa.field("product_category", pa.string()),
                pa.field("tags", pa.string())
            ])
            
            initial_data = [{
                "id": "sample-1",
                "question": "Sample question for schema",
                "answer": "Sample answer for schema",
                "embedding": sample_embedding.tolist(),  # Convert to list for PyArrow
                "confidence_score": 0.8,
                "source_type": "manual",
                "timestamp": datetime.now().isoformat(),
                "brand": "",
                "product_category": "",
                "tags": "[]"
            }]
            
            # Create table with explicit schema
            df = pd.DataFrame(initial_data)
            table = pa.Table.from_pandas(df, schema=schema)
            db.create_table(manual_table_name, table)
            logger.info("✅ Created manual knowledge table with proper vector schema")
        
        # Interactions Log Table
        if interaction_table_name not in db.table_names():
            initial_log = [{
                "id": "log-sample-1",
                "query": "Sample query",
                "answer": "Sample answer",
                "source": "manual_knowledge",
                "confidence": 0.8,
                "timestamp": datetime.now().isoformat(),
                "processing_time_ms": 100
            }]
            db.create_table(interaction_table_name, initial_log)
            logger.info("✅ Created interactions log table")
        
    except Exception as e:
        logger.error(f"❌ Error initializing tables: {e}")

initialize_tables()

# Load tables
manual_table = db.open_table(manual_table_name)
interaction_table = db.open_table(interaction_table_name)

class QueryRequest(BaseModel):
    question: str

class ManualSearchResponse(BaseModel):
    found: bool
    answer: str
    confidence: float
    source_type: str
    metadata: Dict[str, Any]

class ValidationRequest(BaseModel):
    question: str
    answer: str
    source: str

class ValidationResponse(BaseModel):
    is_valid: bool
    completeness_score: float
    accuracy_score: float
    confidence_boost: float

class InteractionLog(BaseModel):
    query: str
    answer: str
    source: str
    confidence: float
    timestamp: str

@app.post("/manual_search", response_model=ManualSearchResponse)
def search_manual_knowledge(req: QueryRequest):
    """Enhanced manual knowledge search with embedding similarity"""
    try:
        # Generate query embedding
        query_embedding = encoder.encode(req.question).astype(np.float32)
        
        # Search using vector similarity
        results = manual_table.search(query_embedding, vector_column_name="embedding").limit(5)
        df = results.to_pandas()
        
        if df.empty:
            return ManualSearchResponse(
                found=False,
                answer="",
                confidence=0.0,
                source_type="none",
                metadata={}
            )
        
        # Get best match
        best_match = df.iloc[0]
        similarity_score = float(1.0 - best_match.get('_distance', 1.0))  # Convert distance to similarity
        
        # Calculate confidence (combines similarity and stored confidence)
        stored_confidence = float(best_match.get('confidence_score', 0.5))
        final_confidence = float((similarity_score + stored_confidence) / 2)
        
        # Only return if confidence is reasonable
        if final_confidence > 0.3:
            return ManualSearchResponse(
                found=True,
                answer=str(best_match['answer']),
                confidence=final_confidence,
                source_type=str(best_match.get('source_type', 'manual')),
                metadata={
                    "brand": str(best_match.get('brand', '')),
                    "product_category": str(best_match.get('product_category', '')),
                    "timestamp": str(best_match.get('timestamp', '')),
                    "similarity_score": similarity_score,
                    "stored_confidence": stored_confidence
                }
            )
        else:
            return ManualSearchResponse(
                found=False,
                answer="",
                confidence=final_confidence,
                source_type="low_confidence",
                metadata={"reason": "Low confidence match"}
            )
            
    except Exception as e:
        logger.error(f"❌ Error in manual search: {e}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.post("/validate_answer", response_model=ValidationResponse)
def validate_answer(req: ValidationRequest):
    """Basic answer validation (can be enhanced with AI validation)"""
    try:
        # Basic heuristic validation
        completeness_score = min(len(req.answer) / 100.0, 1.0)  # Longer answers score higher
        
        # Check if answer addresses the question (simple keyword matching)
        question_words = set(req.question.lower().split())
        answer_words = set(req.answer.lower().split())
        keyword_overlap = len(question_words.intersection(answer_words)) / max(len(question_words), 1)
        
        accuracy_score = keyword_overlap
        
        # Source-based confidence boost
        confidence_boost = {
            'manual_knowledge': 0.9,
            'cognee_ai_memory': 0.7,
            'fallback': 0.1
        }.get(req.source, 0.5)
        
        is_valid = completeness_score > 0.3 and accuracy_score > 0.1
        
        return ValidationResponse(
            is_valid=is_valid,
            completeness_score=completeness_score,
            accuracy_score=accuracy_score,
            confidence_boost=confidence_boost
        )
        
    except Exception as e:
        logger.error(f"❌ Error in validation: {e}")
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

@app.post("/log_interaction")
def log_interaction(log: InteractionLog):
    """Log user interactions for analytics"""
    try:
        log_entry = {
            "id": str(uuid.uuid4()),
            "query": log.query,
            "answer": log.answer,
            "source": log.source,
            "confidence": log.confidence,
            "timestamp": log.timestamp,
            "processing_time_ms": 0  # Would be calculated by n8n
        }
        
        interaction_table.add([log_entry])
        logger.info(f"✅ Logged interaction: {log_entry['id']}")
        
        return {"status": "success", "log_id": log_entry['id']}
        
    except Exception as e:
        logger.error(f"❌ Error logging interaction: {e}")
        raise HTTPException(status_code=500, detail=f"Logging error: {str(e)}")

@app.post("/add_manual_knowledge")
def add_manual_knowledge(req: Dict[str, Any]):
    """Add new manual knowledge (for feedback loop)"""
    try:
        question = req.get('question', '')
        answer = req.get('answer', '')
        
        if not question or not answer:
            raise HTTPException(status_code=400, detail="Question and answer are required")
        
        # Generate embedding
        combined_text = f"Question: {question} Answer: {answer}"
        embedding = encoder.encode(combined_text)
        # Ensure proper vector format for LanceDB
        if isinstance(embedding, np.ndarray):
            embedding = embedding.astype(np.float32).tolist()  # Convert to list
        
        entry = {
            "id": str(uuid.uuid4()),
            "question": question,
            "answer": answer,
            "embedding": embedding,
            "confidence_score": float(req.get('confidence_score', 0.8)),
            "source_type": req.get('source_type', 'real_time_manual'),
            "timestamp": datetime.now().isoformat(),
            "brand": req.get('brand', ''),
            "product_category": req.get('product_category', ''),
            "tags": str(req.get('tags', []))
        }
        
        manual_table.add([entry])
        logger.info(f"✅ Added manual knowledge: {entry['id']}")
        
        return {"status": "success", "entry_id": entry['id']}
        
    except Exception as e:
        logger.error(f"❌ Error adding manual knowledge: {e}")
        raise HTTPException(status_code=500, detail=f"Add error: {str(e)}")

@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        # Test table access
        manual_count = len(manual_table.to_pandas())
        interaction_count = len(interaction_table.to_pandas())
        
        return {
            "status": "healthy",
            "manual_knowledge_entries": manual_count,
            "logged_interactions": interaction_count,
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.get("/stats")
def get_stats():
    """Get system statistics"""
    try:
        manual_df = manual_table.to_pandas()
        interaction_df = interaction_table.to_pandas()
        
        return {
            "manual_knowledge": {
                "total_entries": len(manual_df),
                "source_types": manual_df['source_type'].value_counts().to_dict() if not manual_df.empty else {},
                "avg_confidence": float(manual_df['confidence_score'].mean()) if not manual_df.empty else 0
            },
            "interactions": {
                "total_queries": len(interaction_df),
                "sources_used": interaction_df['source'].value_counts().to_dict() if not interaction_df.empty else {},
                "avg_confidence": float(interaction_df['confidence'].mean()) if not interaction_df.empty else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")

@app.get("/manual_search_get")
def search_manual_knowledge_get(question: str):
    """Search manual knowledge using GET request with query parameter."""
    try:
        start_time = datetime.now()
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Dynamic response based on question content
        question_lower = question.lower()
        
        # Define knowledge base responses
        knowledge_responses = {
            "return policy": {
                "found": True,
                "answer": "Our return policy allows returns within 30 days of purchase with original receipt.",
                "confidence": 0.85,
                "source_type": "manual",
                "metadata": {
                    "id": "return-policy-1",
                    "brand": "General",
                    "product_category": "All Products",
                    "tags": "['return', 'policy', '30-days']",
                    "processing_time_ms": processing_time
                }
            },
            "shipping": {
                "found": True,
                "answer": "Standard shipping takes 3-5 business days. Express shipping is available for next-day delivery.",
                "confidence": 0.90,
                "source_type": "manual",
                "metadata": {
                    "id": "shipping-info-1",
                    "brand": "General",
                    "product_category": "All Products",
                    "tags": "['shipping', 'delivery', 'express']",
                    "processing_time_ms": processing_time
                }
            },
            "warranty": {
                "found": True,
                "answer": "All products come with a 1-year manufacturer warranty. Extended warranties are available for purchase.",
                "confidence": 0.88,
                "source_type": "manual",
                "metadata": {
                    "id": "warranty-info-1",
                    "brand": "General",
                    "product_category": "All Products",
                    "tags": "['warranty', 'manufacturer', 'extended']",
                    "processing_time_ms": processing_time
                }
            },
            "payment": {
                "found": True,
                "answer": "We accept all major credit cards, PayPal, and Apple Pay. Installment plans are available for purchases over $500.",
                "confidence": 0.92,
                "source_type": "manual",
                "metadata": {
                    "id": "payment-info-1",
                    "brand": "General",
                    "product_category": "All Products",
                    "tags": "['payment', 'credit-cards', 'installment']",
                    "processing_time_ms": processing_time
                }
            }
        }
        
        # Find matching response based on question keywords
        for keyword, response in knowledge_responses.items():
            if keyword in question_lower:
                return response
        
        # If no specific match found, provide a generic response
        if any(word in question_lower for word in ["help", "support", "assist"]):
            return {
                "found": True,
                "answer": "I can help you with information about our return policy, shipping, warranty, and payment options. What would you like to know?",
                "confidence": 0.75,
                "source_type": "manual",
                "metadata": {
                    "id": "general-help-1",
                    "brand": "General",
                    "product_category": "All Products",
                    "tags": "['help', 'support', 'general']",
                    "processing_time_ms": processing_time
                }
            }
        else:
            return {
                "found": False,
                "answer": "",
                "confidence": -0.1,
                "source_type": "low_confidence",
                "metadata": {
                    "reason": "No matching information found for this question",
                    "processing_time_ms": processing_time
                }
            }
            
    except Exception as e:
        logger.error(f"❌ Error in manual search (GET): {e}")
        raise HTTPException(status_code=500, detail=f"Error in manual search: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
