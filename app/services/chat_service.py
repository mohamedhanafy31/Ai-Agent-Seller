"""
Chat Service - Business logic for Arabic conversational AI.
"""

import asyncio
import time
from typing import List, Optional, Dict, Any
from uuid import uuid4
from datetime import datetime

import aiohttp
from sqlalchemy.orm import Session
from loguru import logger

from app.schemas.chat import ChatMessage, ChatResponse, ChatSession, ProductInfo
from app.models.clothes import Clothes
from app.models.category import Category
from app.models.store import Store
from app.core.config import get_settings
from app.core.exceptions import ExternalServiceError, DatabaseError

settings = get_settings()


class ChatService:
    """Service for handling chat interactions with Arabic AI."""
    
    def __init__(self, db: Session, model_manager):
        self.db = db
        self.model_manager = model_manager
        self.settings = settings
        self.active_sessions: Dict[str, Dict] = {}
    
    async def process_message(self, message: ChatMessage) -> ChatResponse:
        """Process a chat message and generate AI response."""
        start_time = time.time()
        
        try:
            # Get or create session
            session_id = message.session_id or str(uuid4())
            
            # Extract intent and search for products if needed
            products = await self._extract_product_intent(message.message)
            
            # Generate AI response using Ollama
            ai_response = await self._generate_ai_response(message.message, products)
            
            # Update session
            await self._update_session(session_id, message.message, ai_response)
            
            processing_time = time.time() - start_time
            
            return ChatResponse(
                response=ai_response,
                session_id=session_id,
                processing_time=processing_time,
                confidence=0.85  # Mock confidence score
            )
            
        except Exception as e:
            logger.error(f"Chat processing failed: {str(e)}")
            raise ExternalServiceError("chat processing", {"error": str(e)})
    
    async def _extract_product_intent(self, message: str) -> List[ProductInfo]:
        """Extract product search intent from Arabic message."""
        try:
            # Simple keyword matching (in production, use NLP)
            search_keywords = {
                'قميص': 'shirt',
                'بنطلون': 'pants', 
                'حذاء': 'shoes',
                'جاكيت': 'jacket',
                'أزرق': 'blue',
                'أحمر': 'red',
                'أبيض': 'white',
                'أسود': 'black'
            }
            
            detected_items = []
            detected_colors = []
            
            for arabic_word, english_word in search_keywords.items():
                if arabic_word in message:
                    if english_word in ['blue', 'red', 'white', 'black']:
                        detected_colors.append(english_word)
                    else:
                        detected_items.append(english_word)
            
            # Query database for matching products
            if detected_items:
                products = await self._search_products(detected_items, detected_colors)
                return products
            
            return []
            
        except Exception as e:
            logger.warning(f"Product intent extraction failed: {str(e)}")
            return []
    
    async def _search_products(self, items: List[str], colors: List[str]) -> List[ProductInfo]:
        """Search for products in the database."""
        try:
            query = self.db.query(Clothes).join(Category).join(Store)
            
            # Filter by item type
            for item in items:
                if item == 'shirt':
                    query = query.filter(Category.name.ilike('%shirt%'))
                elif item == 'pants':
                    query = query.filter(Category.name.ilike('%pants%'))
                elif item == 'shoes':
                    query = query.filter(Category.name.ilike('%shoes%'))
                elif item == 'jacket':
                    query = query.filter(Category.name.ilike('%jacket%'))
            
            # Filter by color if specified
            for color in colors:
                query = query.filter(Clothes.name.ilike(f'%{color}%'))
            
            # Filter available items
            query = query.filter(Clothes.stock > 0)
            
            results = query.limit(5).all()
            
            products = []
            for item in results:
                products.append(ProductInfo(
                    id=item.id,
                    name=item.name,
                    price=float(item.price),
                    stock=item.stock,
                    category=item.category.name,
                    store=item.store.name
                ))
            
            return products
            
        except Exception as e:
            logger.error(f"Product search failed: {str(e)}")
            raise DatabaseError("product search", {"error": str(e)})
    
    async def _generate_ai_response(self, message: str, products: List[ProductInfo]) -> str:
        """Generate AI response using Ollama."""
        try:
            # Build context with products
            context = ""
            if products:
                context = "\n\nمنتجات متوفرة:\n"
                for product in products:
                    context += f"- {product.name}: {product.price} جنيه، متوفر {product.stock} قطعة\n"
            
            # Create prompt
            prompt = f"""أنت مساعد ذكي في متجر ملابس. أجب على استفسار العميل باللغة العربية بطريقة مفيدة ومهذبة.

استفسار العميل: {message}
{context}

الرد:"""
            
            # Call Ollama API
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9
                    }
                }
                
                async with session.post(settings.OLLAMA_ENDPOINT, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("response", "عذراً، لم أتمكن من فهم طلبك.")
                    else:
                        logger.error(f"Ollama API error: {response.status}")
                        return "عذراً، هناك مشكلة تقنية. حاول مرة أخرى."
        
        except Exception as e:
            logger.error(f"AI response generation failed: {str(e)}")
            return "عذراً، لا أستطيع الرد حالياً. حاول مرة أخرى لاحقاً."
    
    async def _update_session(self, session_id: str, message: str, response: str):
        """Update chat session with new interaction."""
        try:
            if session_id not in self.active_sessions:
                self.active_sessions[session_id] = {
                    "session_id": session_id,
                    "created_at": datetime.utcnow(),
                    "message_count": 0,
                    "messages": []
                }
            
            session = self.active_sessions[session_id]
            session["last_activity"] = datetime.utcnow()
            session["message_count"] += 1
            session["messages"].append({
                "user_message": message,
                "ai_response": response,
                "timestamp": datetime.utcnow()
            })
            
            # Keep only last 10 messages per session
            if len(session["messages"]) > 10:
                session["messages"] = session["messages"][-10:]
                
        except Exception as e:
            logger.warning(f"Session update failed: {str(e)}")
    
    async def get_active_sessions(self) -> List[ChatSession]:
        """Get list of active chat sessions."""
        sessions = []
        for session_id, session_data in self.active_sessions.items():
            sessions.append(ChatSession(
                session_id=session_id,
                created_at=session_data["created_at"],
                last_activity=session_data["last_activity"],
                message_count=session_data["message_count"],
                is_active=True
            ))
        return sessions
    
    async def create_session(self) -> ChatSession:
        """Create a new chat session."""
        session_id = str(uuid4())
        now = datetime.utcnow()
        
        session_data = {
            "session_id": session_id,
            "created_at": now,
            "last_activity": now,
            "message_count": 0,
            "messages": []
        }
        
        self.active_sessions[session_id] = session_data
        
        return ChatSession(
            session_id=session_id,
            created_at=now,
            last_activity=now,
            message_count=0,
            is_active=True
        )
    
    async def get_available_products(self, limit: int = 10, category: Optional[str] = None) -> List[ProductInfo]:
        """Get available products for recommendations."""
        try:
            query = self.db.query(Clothes).join(Category).join(Store)
            query = query.filter(Clothes.stock > 0)
            
            if category:
                query = query.filter(Category.name.ilike(f'%{category}%'))
            
            results = query.limit(limit).all()
            
            products = []
            for item in results:
                products.append(ProductInfo(
                    id=item.id,
                    name=item.name,
                    price=float(item.price),
                    stock=item.stock,
                    category=item.category.name,
                    store=item.store.name
                ))
            
            return products
            
        except Exception as e:
            logger.error(f"Get available products failed: {str(e)}")
            raise DatabaseError("get available products", {"error": str(e)}) 