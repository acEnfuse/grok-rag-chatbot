import os
from typing import List, Dict, Any
from groq import AsyncGroq
import logging

logger = logging.getLogger(__name__)

class GroqService:
    def __init__(self):
        self.client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"  # Updated to latest production model
    
    async def generate_job_matching_response(
        self, 
        cv_data: Dict[str, Any], 
        matched_jobs: List[Dict[str, Any]], 
        chat_history: List[Dict[str, str]] = None
    ) -> str:
        """Generate a job matching response using Groq with CV and job data"""
        try:
            # Prepare CV summary
            cv_summary = self._prepare_cv_summary(cv_data)
            
            # Prepare job matches
            jobs_context = self._prepare_jobs_context(matched_jobs)
            
            # Prepare chat history
            messages = []
            
            # System prompt for job matching
            system_prompt = """You are an AI career advisor for the Human Resources and Social Development (HRSD) ministry of Saudi Arabia. Your role is to help job seekers find suitable employment opportunities based on their CV and the available job positions.

Guidelines:
- Analyze the candidate's CV and match it with available job opportunities
- Provide detailed explanations for why each job is a good match
- Include match percentages and specific reasons for the match
- Be encouraging and professional in your tone
- Focus on skills alignment, experience level, and career growth potential
- Provide actionable advice for improving job prospects
- Always maintain a supportive and helpful tone"""
            
            messages.append({"role": "system", "content": system_prompt})
            
            # Add recent chat history for context
            if chat_history:
                for msg in chat_history[-4:]:  # Last 4 messages for context
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Add current analysis request
            user_message = f"""Please analyze this candidate's CV and provide job matching recommendations:

CANDIDATE CV SUMMARY:
{cv_summary}

AVAILABLE JOB OPPORTUNITIES:
{jobs_context}

Please provide:
1. A brief summary of the candidate's profile
2. Top 3-5 job matches with detailed explanations
3. Match percentages and specific reasons for each match
4. Suggestions for improving job prospects
5. Any additional career advice

Format your response in a clear, professional manner suitable for a government career counseling service."""
            
            messages.append({"role": "user", "content": user_message})
            
            # Generate response
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=2048,
                temperature=0.3,
                top_p=0.9
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating job matching response with Groq: {e}")
            raise
    
    def _prepare_cv_summary(self, cv_data: Dict[str, Any]) -> str:
        """Prepare a summary of CV data for the AI"""
        summary_parts = []
        
        # Personal info
        if cv_data.get('personal_info', {}).get('name'):
            summary_parts.append(f"Name: {cv_data['personal_info']['name']}")
        
        # Skills
        if cv_data.get('skills'):
            skills_str = ", ".join(cv_data['skills'][:10])  # Top 10 skills
            summary_parts.append(f"Skills: {skills_str}")
        
        # Experience
        if cv_data.get('experience'):
            exp_summary = []
            for exp in cv_data['experience'][:3]:  # Top 3 experiences
                if exp.get('title'):
                    exp_summary.append(exp['title'])
            if exp_summary:
                summary_parts.append(f"Recent Experience: {', '.join(exp_summary)}")
        
        # Education
        if cv_data.get('education'):
            edu_summary = []
            for edu in cv_data['education'][:2]:  # Top 2 education entries
                if edu.get('institution'):
                    edu_summary.append(edu['institution'])
            if edu_summary:
                summary_parts.append(f"Education: {', '.join(edu_summary)}")
        
        # Contact
        if cv_data.get('contact', {}).get('email'):
            summary_parts.append(f"Email: {cv_data['contact']['email']}")
        
        # Raw text summary
        if cv_data.get('summary'):
            summary_parts.append(f"CV Summary: {cv_data['summary']}")
        
        return "\n".join(summary_parts) if summary_parts else "CV data not available"
    
    def _prepare_jobs_context(self, matched_jobs: List[Dict[str, Any]]) -> str:
        """Prepare job matches context for the AI"""
        if not matched_jobs:
            return "No job matches found."
        
        jobs_context = []
        for i, job in enumerate(matched_jobs[:5], 1):  # Top 5 jobs
            job_info = f"""
Job {i}:
- Title: {job.get('job_title', 'N/A')}
- Company: {job.get('company', 'N/A')}
- Match Score: {job.get('match_score', 0)}%
- Description: {job.get('description', 'N/A')[:200]}...
- Required Skills: {job.get('required_skills', 'N/A')}
- Experience Level: {job.get('experience_level', 'N/A')}
- Location: {job.get('location', 'N/A')}
- Salary: {job.get('salary_range', 'N/A')}
"""
            jobs_context.append(job_info)
        
        return "\n".join(jobs_context)
    
    async def generate_response(
        self, 
        query: str, 
        context_docs: List[Dict[str, Any]], 
        chat_history: List[Dict[str, str]] = None
    ) -> str:
        """Generate a response using Groq with RAG context (legacy method)"""
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
            # Return a fallback response when Groq is unavailable
            return f"I apologize, but I'm currently unable to process your request due to a technical issue with the AI service. However, I can still help you with job matching through our CV upload feature. Please upload your CV to get personalized job recommendations based on the available opportunities in Saudi Arabia."
    
    async def generate_simple_chat_response(self, query: str, chat_history: List[Dict[str, str]] = None) -> str:
        """Generate a simple chat response without RAG context"""
        try:
            # Prepare messages
            messages = []
            
            # Add system message
            system_message = """You are an AI career advisor for the Human Resources and Social Development (HRSD) ministry in Saudi Arabia. 
            You help job seekers with career advice, CV analysis, and job matching guidance. 
            Be helpful, professional, and provide actionable advice about careers in Saudi Arabia."""
            
            messages.append({"role": "system", "content": system_message})
            
            # Add chat history
            if chat_history:
                messages.extend(chat_history)
            
            # Add current query
            messages.append({"role": "user", "content": query})
            
            # Generate response
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_completion_tokens=4000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating chat response with Groq: {e}")
            # Return a fallback response when Groq is unavailable
            return f"I apologize, but I'm currently unable to process your request due to a technical issue with the AI service. However, I can still help you with job matching through our CV upload feature. Please upload your CV to get personalized job recommendations based on the available opportunities in Saudi Arabia."

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