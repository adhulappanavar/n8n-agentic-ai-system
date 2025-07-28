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
import re
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load OpenAI Key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY", "sk-test-key-placeholder")

app = FastAPI(title="LanceCogniee Validation API", version="1.0.0")

class ValidationRequest(BaseModel):
    question: str
    answer: str
    source: str  # "lancedb", "cognee", "combined"
    confidence: float
    context: Optional[Dict[str, Any]] = {}

class ValidationResponse(BaseModel):
    is_valid: bool
    validation_score: float
    validation_reason: str
    quality_metrics: Dict[str, Any]
    suggestions: List[str]
    final_answer: str

class QualityMetrics(BaseModel):
    relevance_score: float
    accuracy_score: float
    completeness_score: float
    clarity_score: float
    consistency_score: float
    factual_accuracy: float
    logical_coherence: float

async def validate_answer_quality(question: str, answer: str, source: str) -> QualityMetrics:
    """
    Comprehensive answer quality validation for agentic AI systems
    """
    try:
        # 1. Relevance Check - Does the answer address the question?
        relevance_score = await check_relevance(question, answer)
        
        # 2. Accuracy Check - Is the information factually correct?
        accuracy_score = await check_accuracy(question, answer)
        
        # 3. Completeness Check - Does it cover all aspects of the question?
        completeness_score = await check_completeness(question, answer)
        
        # 4. Clarity Check - Is the answer clear and well-structured?
        clarity_score = await check_clarity(answer)
        
        # 5. Consistency Check - Is the answer internally consistent?
        consistency_score = await check_consistency(answer)
        
        # 6. Factual Accuracy - Cross-reference with knowledge base
        factual_accuracy = await check_factual_accuracy(question, answer)
        
        # 7. Logical Coherence - Does the answer make logical sense?
        logical_coherence = await check_logical_coherence(answer)
        
        return QualityMetrics(
            relevance_score=relevance_score,
            accuracy_score=accuracy_score,
            completeness_score=completeness_score,
            clarity_score=clarity_score,
            consistency_score=consistency_score,
            factual_accuracy=factual_accuracy,
            logical_coherence=logical_coherence
        )
        
    except Exception as e:
        logger.error(f"❌ Error in quality validation: {e}")
        # Return default scores on error
        return QualityMetrics(
            relevance_score=0.5,
            accuracy_score=0.5,
            completeness_score=0.5,
            clarity_score=0.5,
            consistency_score=0.5,
            factual_accuracy=0.5,
            logical_coherence=0.5
        )

async def check_relevance(question: str, answer: str) -> float:
    """Check if the answer is relevant to the question"""
    try:
        # Simple keyword matching
        question_lower = question.lower()
        answer_lower = answer.lower()
        
        # Extract key terms from question
        key_terms = extract_key_terms(question_lower)
        
        # Count matching terms
        matches = sum(1 for term in key_terms if term in answer_lower)
        relevance = min(1.0, matches / max(1, len(key_terms)))
        
        logger.info(f"🔍 Relevance check: {relevance:.2f} for question: '{question}'")
        return relevance
        
    except Exception as e:
        logger.warning(f"⚠️ Relevance check failed: {e}")
        return 0.5

async def check_accuracy(question: str, answer: str) -> float:
    """Check factual accuracy of the answer"""
    try:
        # Define accuracy patterns for different question types
        accuracy_patterns = {
            "return policy": ["30 days", "receipt", "return", "policy"],
            "shipping": ["business days", "express", "delivery", "shipping"],
            "warranty": ["warranty", "manufacturer", "extended", "purchase"],
            "payment": ["credit cards", "paypal", "apple pay", "installment"]
        }
        
        question_lower = question.lower()
        answer_lower = answer.lower()
        
        # Find matching pattern
        for pattern_key, expected_terms in accuracy_patterns.items():
            if pattern_key in question_lower:
                matches = sum(1 for term in expected_terms if term in answer_lower)
                accuracy = min(1.0, matches / len(expected_terms))
                logger.info(f"✅ Accuracy check: {accuracy:.2f} for pattern: {pattern_key}")
                return accuracy
        
        # Default accuracy for unknown patterns
        return 0.7
        
    except Exception as e:
        logger.warning(f"⚠️ Accuracy check failed: {e}")
        return 0.5

async def check_completeness(question: str, answer: str) -> float:
    """Check if the answer covers all aspects of the question"""
    try:
        # Define completeness criteria for different question types
        completeness_criteria = {
            "return policy": ["timeframe", "requirements", "process"],
            "shipping": ["timeframe", "options", "cost"],
            "warranty": ["duration", "coverage", "options"],
            "payment": ["methods", "options", "terms"]
        }
        
        question_lower = question.lower()
        answer_lower = answer.lower()
        
        # Find matching criteria
        for criteria_key, required_aspects in completeness_criteria.items():
            if criteria_key in question_lower:
                covered_aspects = sum(1 for aspect in required_aspects if aspect in answer_lower)
                completeness = min(1.0, covered_aspects / len(required_aspects))
                logger.info(f"📋 Completeness check: {completeness:.2f} for criteria: {criteria_key}")
                return completeness
        
        # Default completeness for unknown criteria
        return 0.6
        
    except Exception as e:
        logger.warning(f"⚠️ Completeness check failed: {e}")
        return 0.5

async def check_clarity(answer: str) -> float:
    """Check clarity and readability of the answer"""
    try:
        # Simple clarity metrics
        sentences = len(re.split(r'[.!?]+', answer))
        words = len(answer.split())
        avg_sentence_length = words / max(1, sentences)
        
        # Clarity score based on sentence length and structure
        if avg_sentence_length <= 15 and sentences >= 1:
            clarity = 0.9
        elif avg_sentence_length <= 25 and sentences >= 1:
            clarity = 0.7
        else:
            clarity = 0.5
            
        logger.info(f"📝 Clarity check: {clarity:.2f} (avg sentence length: {avg_sentence_length:.1f})")
        return clarity
        
    except Exception as e:
        logger.warning(f"⚠️ Clarity check failed: {e}")
        return 0.5

async def check_consistency(answer: str) -> float:
    """Check internal consistency of the answer"""
    try:
        # Check for contradictions
        contradictions = [
            ("30 days", "60 days"),
            ("express", "standard"),
            ("warranty", "no warranty"),
            ("credit cards", "cash only")
        ]
        
        answer_lower = answer.lower()
        consistency_score = 1.0
        
        for term1, term2 in contradictions:
            if term1 in answer_lower and term2 in answer_lower:
                consistency_score = 0.3
                break
                
        logger.info(f"🔄 Consistency check: {consistency_score:.2f}")
        return consistency_score
        
    except Exception as e:
        logger.warning(f"⚠️ Consistency check failed: {e}")
        return 0.5

async def check_factual_accuracy(question: str, answer: str) -> float:
    """Cross-reference with knowledge base for factual accuracy"""
    try:
        # Try to get reference from LanceDB
        try:
            encoded_question = requests.utils.quote(question)
            response = requests.get(
                f"http://127.0.0.1:8000/manual_search_get?question={encoded_question}",
                timeout=3
            )
            
            if response.status_code == 200:
                reference_data = response.json()
                if reference_data.get("found", False):
                    reference_answer = reference_data.get("answer", "").lower()
                    answer_lower = answer.lower()
                    
                    # Simple similarity check
                    common_words = set(reference_answer.split()) & set(answer_lower.split())
                    similarity = len(common_words) / max(1, len(set(reference_answer.split())))
                    
                    logger.info(f"📚 Factual accuracy: {similarity:.2f} (cross-referenced)")
                    return min(1.0, similarity + 0.2)  # Boost for having reference
                    
        except Exception as e:
            logger.warning(f"⚠️ LanceDB reference failed: {e}")
        
        # Default factual accuracy
        return 0.6
        
    except Exception as e:
        logger.warning(f"⚠️ Factual accuracy check failed: {e}")
        return 0.5

async def check_logical_coherence(answer: str) -> float:
    """Check logical coherence of the answer"""
    try:
        # Check for logical indicators
        logical_indicators = ["because", "therefore", "since", "as a result", "consequently"]
        answer_lower = answer.lower()
        
        # Count logical connectors
        logical_count = sum(1 for indicator in logical_indicators if indicator in answer_lower)
        
        # Coherence score based on logical structure
        if logical_count >= 2:
            coherence = 0.9
        elif logical_count >= 1:
            coherence = 0.7
        else:
            coherence = 0.5
            
        logger.info(f"🧠 Logical coherence: {coherence:.2f} (logical connectors: {logical_count})")
        return coherence
        
    except Exception as e:
        logger.warning(f"⚠️ Logical coherence check failed: {e}")
        return 0.5

def extract_key_terms(text: str) -> List[str]:
    """Extract key terms from text"""
    # Remove common stop words
    stop_words = {"what", "is", "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
    
    # Extract words and filter
    words = re.findall(r'\b\w+\b', text.lower())
    key_terms = [word for word in words if word not in stop_words and len(word) > 2]
    
    return key_terms

async def generate_validation_suggestions(metrics: QualityMetrics, answer: str) -> List[str]:
    """Generate improvement suggestions based on quality metrics"""
    suggestions = []
    
    if metrics.relevance_score < 0.7:
        suggestions.append("Answer could be more relevant to the specific question asked")
    
    if metrics.accuracy_score < 0.7:
        suggestions.append("Verify factual accuracy of the information provided")
    
    if metrics.completeness_score < 0.7:
        suggestions.append("Answer could cover more aspects of the question")
    
    if metrics.clarity_score < 0.7:
        suggestions.append("Consider restructuring for better clarity and readability")
    
    if metrics.consistency_score < 0.7:
        suggestions.append("Check for internal contradictions in the response")
    
    if metrics.factual_accuracy < 0.7:
        suggestions.append("Cross-reference with authoritative knowledge sources")
    
    if metrics.logical_coherence < 0.7:
        suggestions.append("Add logical connectors to improve flow and coherence")
    
    return suggestions

@app.post("/validate_answer", response_model=ValidationResponse)
async def validate_answer_endpoint(req: ValidationRequest):
    """Validate answer quality for agentic AI systems"""
    try:
        logger.info(f"🔍 Validating answer for question: '{req.question}'")
        logger.info(f"📝 Source: {req.source}, Confidence: {req.confidence}")
        
        # Perform comprehensive quality validation
        quality_metrics = await validate_answer_quality(req.question, req.answer, req.source)
        
        # Calculate overall validation score
        validation_score = (
            quality_metrics.relevance_score * 0.2 +
            quality_metrics.accuracy_score * 0.25 +
            quality_metrics.completeness_score * 0.15 +
            quality_metrics.clarity_score * 0.1 +
            quality_metrics.consistency_score * 0.1 +
            quality_metrics.factual_accuracy * 0.15 +
            quality_metrics.logical_coherence * 0.05
        )
        
        # Determine if answer is valid (threshold: 0.7)
        is_valid = validation_score >= 0.7
        
        # Generate improvement suggestions
        suggestions = await generate_validation_suggestions(quality_metrics, req.answer)
        
        # Determine validation reason
        if is_valid:
            validation_reason = "Answer meets quality standards for agentic AI systems"
        else:
            validation_reason = f"Answer quality score ({validation_score:.2f}) below threshold (0.7)"
        
        # Prepare final answer (could be enhanced based on validation)
        final_answer = req.answer
        
        return ValidationResponse(
            is_valid=is_valid,
            validation_score=validation_score,
            validation_reason=validation_reason,
            quality_metrics=quality_metrics.dict(),
            suggestions=suggestions,
            final_answer=final_answer
        )
        
    except Exception as e:
        logger.error(f"❌ Error in answer validation: {e}")
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "lancecogniee_validation_api",
        "openai_configured": openai.api_key != "sk-test-key-placeholder",
        "validation_criteria": [
            "relevance", "accuracy", "completeness", 
            "clarity", "consistency", "factual_accuracy", "logical_coherence"
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/validation_metrics")
def get_validation_metrics():
    """Get detailed validation metrics information"""
    return {
        "validation_weights": {
            "relevance_score": 0.2,
            "accuracy_score": 0.25,
            "completeness_score": 0.15,
            "clarity_score": 0.1,
            "consistency_score": 0.1,
            "factual_accuracy": 0.15,
            "logical_coherence": 0.05
        },
        "thresholds": {
            "minimum_validation_score": 0.7,
            "high_quality_threshold": 0.85
        },
        "supported_sources": ["lancedb", "cognee", "combined"],
        "quality_criteria": {
            "relevance": "Answer addresses the specific question asked",
            "accuracy": "Information is factually correct",
            "completeness": "Answer covers all relevant aspects",
            "clarity": "Answer is clear and well-structured",
            "consistency": "Answer is internally consistent",
            "factual_accuracy": "Cross-referenced with knowledge base",
            "logical_coherence": "Answer flows logically"
        }
    }

if __name__ == "__main__":
    logger.info("🚀 Starting LanceCogniee Validation API")
    logger.info(f"🔑 OpenAI API configured: {openai.api_key != 'sk-test-key-placeholder'}")
    logger.info("📊 Validation criteria: relevance, accuracy, completeness, clarity, consistency, factual_accuracy, logical_coherence")
    uvicorn.run(app, host="127.0.0.1", port=9500) 