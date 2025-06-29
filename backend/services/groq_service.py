import os
from typing import List, Dict, Any
from groq import AsyncGroq
import logging

logger = logging.getLogger(__name__)

class GroqService:
    def __init__(self):
        self.client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"  # Updated to latest production model
    
    async def generate_response(
        self, 
        query: str, 
        context_docs: List[Dict[str, Any]], 
        chat_history: List[Dict[str, str]] = None
    ) -> str:
        """Generate a response using Groq with RAG context"""
        try:
            # Prepare context from retrieved documents
            context = ""
            if context_docs:
                context = "\n\n".join([
                    f"Document: {doc['filename']}\nContent: {doc['text']}"
                    for doc in context_docs[:5]  # Limit to top 5 documents
                ])
            
            # Prepare chat history
            messages = []
            
            # System prompt
            system_prompt = """You are a helpful AI assistant that answers questions based on the provided context documents. 
            
Guidelines:
- Use the context documents to answer questions accurately
- If the answer is not in the context, say so politely
- Cite the relevant documents when possible
- Be concise but comprehensive
- If no context is provided, explain that you need documents to be uploaded first"""
            
            messages.append({"role": "system", "content": system_prompt})
            
            # Add recent chat history for context
            if chat_history:
                for msg in chat_history[-6:]:  # Last 6 messages for context
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Add current query with context
            user_message = f"""Question: {query}

Context Documents:
{context if context else "No relevant documents found. Please upload documents first."}

Please answer the question based on the provided context."""
            
            messages.append({"role": "user", "content": user_message})
            
            # Generate response
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1024,
                temperature=0.1,
                top_p=0.9
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating response with Groq: {e}")
            raise
    
    async def generate_summary(self, text: str, max_length: int = 200) -> str:
        """Generate a summary of the given text"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": f"Summarize the following text in no more than {max_length} characters. Be concise and capture the key points."
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=100,
                temperature=0.1
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return text[:max_length] + "..." if len(text) > max_length else text 