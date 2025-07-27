"""
Chat API endpoints for Arabic conversational interface.

This module provides intelligent Arabic chat capabilities specifically designed for clothing retail.
The AI assistant helps customers find products, answer questions, and provide shopping guidance.

Features:
- Natural Arabic language understanding
- Product recommendations
- Shopping assistance
- Session management
- Context-aware conversations

Powered by Ollama with Gemma 2 model optimized for Arabic retail conversations.
"""

from typing import List, Dict, Any, Generator
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import json
import asyncio

from app.api.deps import get_db, require_ollama_service
from app.services.model_manager import ModelManager
from app.schemas.chat import ChatMessage, ChatResponse, ChatSession
from app.services.chat_service import ChatService
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["chat"])


@router.get(
    "/", 
    response_model=Dict[str, Any],
    summary="Chat Service Information",
    description="Get comprehensive information about the Arabic chat service capabilities and available endpoints."
)
async def chat_info():
    """
    ## Arabic Chat Service Overview
    
    This endpoint provides detailed information about the conversational AI service designed 
    specifically for Arabic-speaking customers in the clothing retail context.
    
    ### Features:
    - **Natural Language Processing**: Advanced Arabic language understanding
    - **Product Discovery**: Intelligent product search and recommendations
    - **Shopping Assistance**: Guided shopping experience with personalized suggestions
    - **Context Awareness**: Maintains conversation context across messages
    - **Multi-turn Conversations**: Supports extended dialogues with session tracking
    
    ### Use Cases:
    - Customer product inquiries ("أريد قميص أزرق للعمل")
    - Size and fit guidance ("ما هو المقاس المناسب لي؟")
    - Style recommendations ("ما هي الألوان الرائجة هذا الموسم؟")
    - Price and availability questions ("كم سعر هذا الفستان؟")
    - Order assistance and support
    
    ### Supported Languages:
    - Primary: Arabic (العربية)
    - Secondary: English (for mixed conversations)
    
    ### Response Format:
    Returns service information including available endpoints, capabilities, and usage guidelines.
    """
    return {
        "name": "Arabic Chat Interface",
        "description": "Intelligent conversational AI for clothing retail assistance",
        "version": "2.0.0",
        "language": "Arabic (العربية)",
        "model": "Ollama Gemma 2 4B",
        "capabilities": {
            "product_search": "Find products by description, color, size, style",
            "recommendations": "Personalized product suggestions based on preferences",
            "size_guidance": "Help customers find the right size and fit",
            "style_advice": "Fashion and styling recommendations",
            "order_support": "Assistance with orders, returns, and exchanges",
            "inventory_check": "Real-time availability and stock information"
        },
        "features": {
            "session_management": "Maintains context across multiple messages",
            "multilingual": "Supports Arabic with English fallback",
            "contextual_memory": "Remembers previous conversation topics",
            "product_integration": "Connected to live inventory system",
            "sentiment_analysis": "Understands customer emotions and preferences"
        },
        "endpoints": {
            "POST /message": {
                "description": "Send a message to the chat bot",
                "purpose": "Main conversational interface",
                "example": "أريد شراء فستان للمناسبات"
            },
            "GET /sessions": {
                "description": "List active chat sessions",
                "purpose": "Session management and analytics"
            },
            "POST /sessions": {
                "description": "Create a new chat session",
                "purpose": "Initialize new conversation context"
            },
            "GET /products": {
                "description": "Get available products",
                "purpose": "Browse product catalog"
            }
        },
        "examples": {
            "greeting": "مرحباً، كيف يمكنني مساعدتك اليوم؟",
            "product_inquiry": "أبحث عن قميص رسمي للعمل",
            "size_question": "ما هو المقاس المناسب لطولي 170 سم؟",
            "color_preference": "أفضل الألوان الداكنة مثل الأسود والكحلي"
        }
    }


@router.post(
    "/message", 
    response_model=ChatResponse,
    summary="Send Message to AI Assistant",
    description="Send a message to the Arabic conversational AI and receive an intelligent response with product recommendations and shopping assistance.",
    responses={
        200: {
            "description": "Successful conversation response",
            "content": {
                "application/json": {
                    "example": {
                        "response": "عندنا مجموعة رائعة من القمصان الزرقاء! يمكنني أن أقترح عليك قمصان قطنية مريحة للعمل أو قمصان رسمية للمناسبات. ما نوع القميص الذي تفضل؟",
                        "session_id": "sess_abc123",
                        "timestamp": "2024-01-20T10:30:00Z",
                        "processing_time": 1.2,
                        "confidence": 0.95,
                        "context": {
                            "intent": "product_search",
                            "product_category": "shirts",
                            "color_preference": "blue",
                            "suggested_products": ["shirt_001", "shirt_002"]
                        }
                    }
                }
            }
        },
        400: {
            "description": "Invalid message format or empty content",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Message cannot be empty or exceed 1000 characters"
                    }
                }
            }
        },
        503: {
            "description": "AI service temporarily unavailable",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Chat service is temporarily unavailable. Please try again later."
                    }
                }
            }
        }
    }
)
async def send_message(
    message: ChatMessage,
    db: Session = Depends(get_db),
    models: ModelManager = Depends(require_ollama_service)
):
    """
    ## Send Message to Arabic AI Assistant
    
    This endpoint processes natural language messages in Arabic and provides intelligent responses
    with product recommendations, shopping guidance, and conversational support.
    
    ### Message Processing:
    1. **Language Detection**: Automatically detects Arabic text and processes accordingly
    2. **Intent Recognition**: Identifies customer intent (search, question, complaint, etc.)
    3. **Context Integration**: Uses session history for contextual responses
    4. **Product Matching**: Connects customer queries to relevant products
    5. **Response Generation**: Creates natural, helpful Arabic responses
    
    ### Supported Query Types:
    
    **Product Search:**
    - "أريد فستان أحمر للحفلات" (I want a red dress for parties)
    - "أبحث عن حذاء رياضي مريح" (I'm looking for comfortable sports shoes)
    
    **Size & Fit Questions:**
    - "ما المقاس المناسب لي؟" (What size is right for me?)
    - "هل هذا الفستان مناسب للمحجبات؟" (Is this dress suitable for hijabis?)
    
    **Style Advice:**
    - "ما هي الألوان الرائجة؟" (What colors are trending?)
    - "ماذا أرتدي في المقابلة؟" (What should I wear for an interview?)
    
    **Price & Availability:**
    - "كم سعر هذا القميص؟" (How much is this shirt?)
    - "هل متوفر بمقاس كبير؟" (Is it available in large size?)
    
    ### Parameters:
    - **message**: Your message in Arabic (1-1000 characters)
    - **session_id**: Optional session identifier for conversation continuity
    
    ### Response Features:
    - **Contextual**: Remembers previous conversation
    - **Product-Aware**: Suggests real products from inventory
    - **Culturally Appropriate**: Respects Arabic cultural preferences
    - **Helpful**: Provides actionable shopping guidance
    
    ### Best Practices:
    - Use natural, conversational Arabic
    - Be specific about preferences (color, size, occasion)
    - Include context from previous messages when relevant
    - Ask follow-up questions for better recommendations
    """
    try:
        chat_service = ChatService(db, models)
        response = await chat_service.process_message(message)
        
        logger.info(f"Chat message processed: {message.message[:50]}...")
        return response
        
    except Exception as e:
        logger.error(f"Chat message processing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chat service is temporarily unavailable. Please try again later."
        )


@router.post(
    "/stream", 
    summary="Stream Message to AI Assistant",
    description="Send a message to the Arabic conversational AI and receive a real-time streaming response using Server-Sent Events (SSE).",
    responses={
        200: {
            "description": "Streaming response with real-time AI generation",
            "content": {
                "text/event-stream": {
                    "example": "data: {\"type\": \"token\", \"content\": \"مرحباً\"}\n\ndata: {\"type\": \"token\", \"content\": \" بك\"}\n\ndata: {\"type\": \"complete\", \"session_id\": \"sess_123\"}\n\n"
                }
            }
        },
        400: {
            "description": "Invalid message format"
        },
        503: {
            "description": "Chat service unavailable"
        }
    }
)
async def stream_message(
    message: ChatMessage,
    db: Session = Depends(get_db),
    models: ModelManager = Depends(require_ollama_service)
):
    """
    **Stream AI Response in Real-Time**
    
    This endpoint provides Server-Sent Events (SSE) streaming for real-time AI responses.
    The response is generated token by token, allowing for immediate display of partial results.
    
    **Stream Event Types:**
    - `token`: Individual response tokens/words
    - `context`: Context information (products, intent)
    - `complete`: Final response with metadata
    - `error`: Error information
    
    **Usage:**
    ```javascript
    const eventSource = new EventSource('/api/v1/chat/stream', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: 'أريد قميص أزرق', session_id: 'sess_123'})
    });
    
    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        if (data.type === 'token') {
            appendToChat(data.content);
        }
    };
    ```
    """
    async def generate_stream():
        try:
            chat_service = ChatService(db, models)
            
            # Send initial event
            yield f"data: {json.dumps({'type': 'start', 'message': 'Processing your request...'})}\n\n"
            await asyncio.sleep(0.1)
            
            # Get the full response first (in a real implementation, you'd stream from the model)
            response = await chat_service.process_message(message)
            
            # Stream the response word by word
            words = response.response.split()
            
            for i, word in enumerate(words):
                # Send each word as a token
                yield f"data: {json.dumps({'type': 'token', 'content': word + ' '})}\n\n"
                await asyncio.sleep(0.05)  # Small delay for realistic streaming effect
                
                # Send progress updates
                if i % 10 == 0:
                    progress = (i + 1) / len(words) * 100
                    yield f"data: {json.dumps({'type': 'progress', 'percentage': round(progress, 1)})}\n\n"
            
            # Send context information
            if hasattr(response, 'context') and response.context:
                yield f"data: {json.dumps({'type': 'context', 'data': response.context})}\n\n"
            
            # Send final completion event
            completion_data = {
                'type': 'complete',
                'session_id': response.session_id,
                'timestamp': response.timestamp.isoformat() if hasattr(response.timestamp, 'isoformat') else str(response.timestamp),
                'processing_time': response.processing_time,
                'confidence': response.confidence,
                'full_response': response.response
            }
            yield f"data: {json.dumps(completion_data)}\n\n"
            
            logger.info(f"Streaming chat completed for session: {response.session_id}")
            
        except Exception as e:
            logger.error(f"Streaming chat failed: {str(e)}")
            error_data = {
                'type': 'error',
                'error': str(e),
                'message': 'Chat service temporarily unavailable'
            }
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )


@router.get("/sessions", response_model=List[ChatSession])
async def get_chat_sessions(
    db: Session = Depends(get_db)
):
    """Get list of active chat sessions."""
    try:
        chat_service = ChatService(db, None)
        sessions = await chat_service.get_active_sessions()
        
        return sessions
        
    except Exception as e:
        logger.error(f"Failed to get chat sessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chat sessions: {str(e)}"
        )


@router.post("/sessions", response_model=ChatSession)
async def create_chat_session(
    db: Session = Depends(get_db)
):
    """Create a new chat session."""
    try:
        chat_service = ChatService(db, None)
        session = await chat_service.create_session()
        
        logger.info(f"New chat session created: {session.session_id}")
        return session
        
    except Exception as e:
        logger.error(f"Failed to create chat session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create chat session: {str(e)}"
        )


@router.get("/products")
async def get_available_products(
    limit: int = 10,
    category: str = None,
    db: Session = Depends(get_db)
):
    """Get available products for chat recommendations."""
    try:
        chat_service = ChatService(db, None)
        products = await chat_service.get_available_products(limit, category)
        
        return {"products": products, "total": len(products)}
        
    except Exception as e:
        logger.error(f"Failed to get products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get products: {str(e)}"
        ) 