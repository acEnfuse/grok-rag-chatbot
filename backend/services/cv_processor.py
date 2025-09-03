import os
import tempfile
from typing import List, Dict, Any, Optional
from tika import parser
import logging
import re
import PyPDF2
import io

logger = logging.getLogger(__name__)

class CVProcessor:
    def __init__(self):
        self.supported_formats = ['.pdf', '.txt', '.doc', '.docx']
        self.max_file_size = 10 * 1024 * 1024  # 10MB limit
    
    async def process_cv(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Process a CV file and extract structured information"""
        try:
            # Validate file
            if not self._validate_file(file_path, filename):
                raise ValueError(f"Unsupported file format or file too large: {filename}")
            
            # Extract text content
            text_content = await self._extract_text(file_path, filename)
            
            # Parse CV information
            cv_data = self._parse_cv_content(text_content)
            
            # Add metadata
            cv_data.update({
                "filename": filename,
                "raw_text": text_content,
                "file_size": os.path.getsize(file_path)
            })
            
            logger.info(f"Processed CV {filename} successfully")
            return cv_data
            
        except Exception as e:
            logger.error(f"Error processing CV {filename}: {e}")
            raise
    
    def _validate_file(self, file_path: str, filename: str) -> bool:
        """Validate file format and size"""
        try:
            # Check file extension
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext not in self.supported_formats:
                return False
            
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating file {filename}: {e}")
            return False
    
    async def _extract_text(self, file_path: str, filename: str) -> str:
        """Extract text from CV file"""
        try:
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext == '.pdf':
                return await self._extract_pdf_text(file_path)
            elif file_ext == '.txt':
                return await self._extract_txt_text(file_path)
            else:
                # Use Tika for other formats (doc, docx, etc.)
                return await self._extract_tika_text(file_path)
                
        except Exception as e:
            logger.error(f"Error extracting text from {filename}: {e}")
            raise
    
    async def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF using PyPDF2"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
                
                return self._clean_text(text)
                
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            # Fallback to Tika
            return await self._extract_tika_text(file_path)
    
    async def _extract_txt_text(self, file_path: str) -> str:
        """Extract text from plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                return self._clean_text(text)
                
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    text = file.read()
                    return self._clean_text(text)
            except Exception as e:
                logger.error(f"Error reading text file: {e}")
                raise
    
    async def _extract_tika_text(self, file_path: str) -> str:
        """Extract text using Tika (for doc, docx, etc.)"""
        try:
            parsed = parser.from_file(file_path)
            text = parsed.get("content", "")
            
            if not text:
                raise ValueError("No text content extracted from document")
            
            return self._clean_text(text)
            
        except Exception as e:
            logger.error(f"Error extracting text with Tika: {e}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\@]', ' ', text)
        
        # Remove extra spaces
        text = ' '.join(text.split())
        
        return text.strip()
    
    def _parse_cv_content(self, text: str) -> Dict[str, Any]:
        """Parse CV content to extract structured information"""
        try:
            # Convert to lowercase for pattern matching
            text_lower = text.lower()
            
            # Extract personal information
            personal_info = self._extract_personal_info(text)
            
            # Extract skills
            skills = self._extract_skills(text)
            
            # Extract experience
            experience = self._extract_experience(text)
            
            # Extract education
            education = self._extract_education(text)
            
            # Extract contact information
            contact = self._extract_contact_info(text)
            
            return {
                "personal_info": personal_info,
                "skills": skills,
                "experience": experience,
                "education": education,
                "contact": contact,
                "summary": self._generate_summary(text)
            }
            
        except Exception as e:
            logger.error(f"Error parsing CV content: {e}")
            return {
                "personal_info": {},
                "skills": [],
                "experience": [],
                "education": [],
                "contact": {},
                "summary": text[:500] + "..." if len(text) > 500 else text
            }
    
    def _extract_personal_info(self, text: str) -> Dict[str, str]:
        """Extract personal information from CV"""
        personal_info = {}
        
        # Extract name (usually at the beginning)
        lines = text.split('\n')[:5]  # Check first 5 lines
        for line in lines:
            line = line.strip()
            if len(line) > 2 and len(line) < 50 and not any(char.isdigit() for char in line):
                if not personal_info.get('name'):
                    personal_info['name'] = line
                    break
        
        return personal_info
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from CV"""
        skills = []
        
        # Common skill keywords
        skill_keywords = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js',
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'linux', 'git',
            'machine learning', 'ai', 'data science', 'analytics', 'tableau',
            'power bi', 'excel', 'project management', 'agile', 'scrum',
            'communication', 'leadership', 'teamwork', 'problem solving',
            'analytical', 'creative', 'detail-oriented', 'time management'
        ]
        
        text_lower = text.lower()
        for skill in skill_keywords:
            if skill in text_lower:
                skills.append(skill.title())
        
        # Remove duplicates and return
        return list(set(skills))
    
    def _extract_experience(self, text: str) -> List[Dict[str, str]]:
        """Extract work experience from CV"""
        experience = []
        
        # Look for experience patterns
        experience_patterns = [
            r'(\d{4})\s*[-–]\s*(\d{4}|\bpresent\b|\bcurrent\b)',
            r'(\d{4})\s*[-–]\s*(\d{4})',
            r'(\d{4})\s*to\s*(\d{4}|\bpresent\b|\bcurrent\b)'
        ]
        
        lines = text.split('\n')
        for i, line in enumerate(lines):
            for pattern in experience_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Try to extract job title and company from surrounding lines
                    job_info = self._extract_job_info(lines, i)
                    if job_info:
                        experience.append(job_info)
                    break
        
        return experience
    
    def _extract_job_info(self, lines: List[str], index: int) -> Optional[Dict[str, str]]:
        """Extract job information from surrounding lines"""
        try:
            # Look at current line and nearby lines
            context_lines = lines[max(0, index-2):index+3]
            
            job_info = {}
            for line in context_lines:
                line = line.strip()
                if len(line) > 5 and len(line) < 100:
                    # This could be a job title or company
                    if not job_info.get('title'):
                        job_info['title'] = line
                    elif not job_info.get('company'):
                        job_info['company'] = line
                        break
            
            return job_info if job_info else None
            
        except Exception:
            return None
    
    def _extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education information from CV"""
        education = []
        
        # Education keywords
        education_keywords = [
            'bachelor', 'master', 'phd', 'doctorate', 'degree', 'diploma',
            'certificate', 'university', 'college', 'institute', 'school'
        ]
        
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in education_keywords):
                education.append({
                    'institution': line.strip(),
                    'degree': self._extract_degree_type(line_lower)
                })
        
        return education
    
    def _extract_degree_type(self, text: str) -> str:
        """Extract degree type from education text"""
        if 'phd' in text or 'doctorate' in text:
            return 'PhD'
        elif 'master' in text:
            return 'Master'
        elif 'bachelor' in text:
            return 'Bachelor'
        elif 'diploma' in text:
            return 'Diploma'
        elif 'certificate' in text:
            return 'Certificate'
        else:
            return 'Other'
    
    def _extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information from CV"""
        contact = {}
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact['email'] = email_match.group()
        
        # Phone pattern
        phone_pattern = r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact['phone'] = phone_match.group()
        
        return contact
    
    def _generate_summary(self, text: str) -> str:
        """Generate a summary of the CV"""
        # Take first 200 characters as summary
        summary = text[:200].strip()
        if len(text) > 200:
            summary += "..."
        return summary
    
    async def process_cv_from_text(self, text: str) -> Dict[str, Any]:
        """Process CV from text content directly"""
        try:
            # Clean the text
            cleaned_text = self._clean_text(text)
            
            # Parse CV information
            cv_data = self._parse_cv_content(cleaned_text)
            
            # Add metadata
            cv_data.update({
                "filename": "text_input",
                "raw_text": cleaned_text,
                "file_size": len(cleaned_text)
            })
            
            logger.info("Processed CV from text successfully")
            return cv_data
            
        except Exception as e:
            logger.error(f"Error processing CV from text: {e}")
            raise
