import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

from google import genai
from google.genai import types
from pydantic import BaseModel

from vector_store.chroma_store import ChromaStore
from utils.language_detector import LanguageDetector

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryCategory(BaseModel):
    category: str
    confidence: float

class ChatbotAgent:
    def __init__(self):
        # Initialize Gemini client
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        
        # Initialize components
        self.vector_store = ChromaStore()
        self.language_detector = LanguageDetector()
        
        # Category classification prompts
        self.category_prompt = {
            'en': """
            Classify the following customer support query into one of these categories:
            - Product FAQ: Questions about product features, specifications, usage
            - Tech issue: Technical problems, bugs, troubleshooting
            - Transactional: Orders, payments, refunds, account issues
            
            Respond with JSON in this format: {"category": "category_name", "confidence": float_between_0_and_1}
            
            Query: {query}
            """,
            'ar': """
            صنف استفسار دعم العملاء التالي إلى إحدى هذه الفئات:
            - Product FAQ: أسئلة حول ميزات المنتج والمواصفات والاستخدام
            - Tech issue: مشاكل تقنية وأخطاء واستكشاف الأخطاء وإصلاحها
            - Transactional: طلبات ومدفوعات واسترداد ومشاكل الحساب
            
            أجب بصيغة JSON: {"category": "category_name", "confidence": float_between_0_and_1}
            
            الاستفسار: {query}
            """
        }

    async def process_chat(self, message: str, language: str, user_id: Optional[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Main chat processing pipeline using LangGraph-like approach"""
        try:
            # Step 1: Categorize query
            category_result = await self._categorize_query(message, language)
            
            # Step 2: Retrieve relevant context
            context_chunks = await self._retrieve_context(message, language)
            
            # Step 3: Generate response using Gemini
            response_result = await self._generate_response(
                message, context_chunks, language, category_result['category']
            )
            
            # Step 4: Calculate confidence score
            confidence = min(category_result['confidence'], response_result['confidence'])
            
            return {
                'response': response_result['response'],
                'confidence': confidence,
                'category': category_result['category'],
                'language': language
            }
            
        except Exception as e:
            logger.error(f"Chat processing failed: {e}")
            return {
                'response': self._get_fallback_response(language),
                'confidence': 0.1,
                'category': 'unknown',
                'language': language
            }

    async def _categorize_query(self, query: str, language: str) -> Dict[str, Any]:
        """Categorize the user query"""
        try:
            prompt = self.category_prompt.get(language, self.category_prompt['en']).format(query=query)
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            if response.text:
                # Try to extract JSON from response
                try:
                    # Sometimes the response includes extra text, try to find JSON
                    response_text = response.text.strip()
                    if '{' in response_text and '}' in response_text:
                        start = response_text.find('{')
                        end = response_text.rfind('}') + 1
                        json_text = response_text[start:end]
                        result = json.loads(json_text)
                        return {
                            'category': result.get('category', 'unknown'),
                            'confidence': float(result.get('confidence', 0.5))
                        }
                except json.JSONDecodeError as je:
                    logger.error(f"JSON parsing failed: {je}, response: {response.text}")
                
                # Fallback: simple keyword matching
                query_lower = query.lower()
                if any(word in query_lower for word in ['password', 'login', 'account', 'payment', 'refund', 'order']):
                    return {'category': 'Transactional', 'confidence': 0.7}
                elif any(word in query_lower for word in ['crash', 'error', 'bug', 'not working', 'slow', 'problem']):
                    return {'category': 'Tech issue', 'confidence': 0.7}
                else:
                    return {'category': 'Product FAQ', 'confidence': 0.6}
            else:
                return {'category': 'unknown', 'confidence': 0.3}
                
        except Exception as e:
            logger.error(f"Query categorization failed: {e}")
            return {'category': 'unknown', 'confidence': 0.2}

    async def _retrieve_context(self, query: str, language: str, top_k: int = 5) -> List[str]:
        """Retrieve relevant context from vector store"""
        try:
            # Search for relevant documents
            results = await self.vector_store.similarity_search(query, top_k=top_k)
            
            # Extract text chunks
            context_chunks = []
            for result in results:
                if 'text' in result:
                    context_chunks.append(result['text'])
            
            return context_chunks
            
        except Exception as e:
            logger.error(f"Context retrieval failed: {e}")
            return []

    async def _generate_response(self, query: str, context_chunks: List[str], language: str, category: str) -> Dict[str, Any]:
        """Generate response using Gemini with retrieved context"""
        try:
            # Prepare context
            context_text = "\n\n".join(context_chunks) if context_chunks else "No relevant context found."
            
            # Language-specific prompts
            if language == 'ar':
                system_prompt = f"""
                أنت مساعد دعم عملاء ذكي. استخدم المعلومات المقدمة فقط للإجابة على استفسار العميل.
                فئة الاستفسار: {category}
                
                قواعد مهمة:
                1. استخدم فقط المعلومات المقدمة في السياق
                2. إذا لم تجد إجابة في السياق، قل "أعتذر، لا أستطيع العثور على معلومات محددة حول هذا الموضوع"
                3. كن مفيداً ومهذباً
                4. قدم إجابات واضحة ومفصلة
                
                السياق المتاح:
                {context_text}
                """
                
                user_prompt = f"استفسار العميل: {query}"
            else:
                system_prompt = f"""
                You are an intelligent customer support assistant. Use ONLY the provided information to answer the customer's query.
                Query category: {category}
                
                Important rules:
                1. Use only the information provided in the context
                2. If you cannot find an answer in the context, say "I apologize, but I cannot find specific information about this topic"
                3. Be helpful and polite
                4. Provide clear and detailed answers
                
                Available context:
                {context_text}
                """
                
                user_prompt = f"Customer query: {query}"
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Content(role="user", parts=[types.Part(text=user_prompt)])
                ],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.1,  # Lower temperature for more consistent responses
                ),
            )
            
            if response.text:
                # Calculate confidence based on context availability and response quality
                confidence = 0.8 if context_chunks else 0.3
                
                # Lower confidence if response indicates uncertainty
                uncertainty_phrases = {
                    'en': ['cannot find', 'not sure', 'unclear', 'apologize'],
                    'ar': ['لا أستطيع', 'غير متأكد', 'أعتذر', 'غير واضح']
                }
                
                response_lower = response.text.lower()
                for phrase in uncertainty_phrases.get(language, uncertainty_phrases['en']):
                    if phrase in response_lower:
                        confidence = min(confidence, 0.4)
                        break
                
                return {
                    'response': response.text,
                    'confidence': confidence
                }
            else:
                return {
                    'response': self._get_fallback_response(language),
                    'confidence': 0.2
                }
                
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return {
                'response': self._get_fallback_response(language),
                'confidence': 0.1
            }

    def _get_fallback_response(self, language: str) -> str:
        """Get fallback response when processing fails"""
        fallback_responses = {
            'en': "I apologize, but I'm having trouble processing your request right now. Please try again or contact our human support team for assistance.",
            'ar': "أعتذر، لكنني أواجه صعوبة في معالجة طلبك الآن. يرجى المحاولة مرة أخرى أو الاتصال بفريق الدعم البشري للحصول على المساعدة."
        }
        
        return fallback_responses.get(language, fallback_responses['en'])
