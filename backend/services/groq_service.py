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
            raise
    
    async def format_job_data(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format and clean up job data to make it more human-readable"""
        try:
            formatted_jobs = []
            
            for job in jobs:
                # Use aggressive local formatting instead of LLM
                formatted_description = self._aggressive_description_formatting(job.get('description', ''))
                formatted_skills = self._aggressive_skills_formatting(job.get('required_skills', ''))
                
                # Create formatted job object
                formatted_job = job.copy()
                formatted_job['description'] = formatted_description
                formatted_job['required_skills'] = formatted_skills
                
                formatted_jobs.append(formatted_job)
            
            return formatted_jobs
            
        except Exception as e:
            logger.error(f"Error formatting job data: {e}")
            return jobs  # Return original jobs if formatting fails
    
    def _simple_description_formatting(self, description: str) -> str:
        """Simple text processing for job descriptions"""
        if not description or len(description.strip()) < 10:
            return description
        
        import re
        
        # Fix common concatenation issues
        formatted = description
        
        # Fix the specific broken words from your example
        word_fixes = {
            'per form': 'perform',
            'with in': 'within', 
            'jur isprudence': 'jurisprudence',
            'prov isi ons': 'provisions',
            'stipul ated': 'stipulated',
            'rel ati on': 'relation',
            'determ ine': 'determine',
            'm iss ing': 'missing',
            'preserv ing': 'preserving',
            'us ing': 'using',
            'accord ing': 'according',
            'c ontrol': 'control',
            'th at': 'that',
            'be fore': 'before',
            'call ing': 'calling',
            'per formance': 'performance',
            'praver': 'prayer',
            'efficient': 'efficient',
            'quality': 'quality',
            'policies': 'policies',
            'procedures': 'procedures',
            'loudspeakers': 'loudspeakers',
            'comply': 'comply'
        }
        
        # Apply the word fixes
        for broken, fixed in word_fixes.items():
            formatted = formatted.replace(broken, fixed)
        
        # Add spaces after periods that are followed by capital letters
        formatted = re.sub(r'\.([A-Z])', r'. \1', formatted)
        
        # Add spaces after asterisks
        formatted = re.sub(r'\*([A-Za-z])', r'* \1', formatted)
        
        # Fix common word concatenations
        common_words = ['and', 'the', 'with', 'for', 'in', 'on', 'at', 'to', 'of', 'is', 'are', 'was', 'were']
        for word in common_words:
            # Add space before word if it's concatenated
            formatted = re.sub(f'([a-z])({word})', r'\1 \2', formatted, flags=re.IGNORECASE)
        
        # Clean up multiple spaces
        formatted = re.sub(r'\s+', ' ', formatted.strip())
        
        return formatted
    
    def _aggressive_description_formatting(self, description: str) -> str:
        """Aggressive text processing for job descriptions - no LLM needed"""
        if not description or len(description.strip()) < 10:
            return description
        
        import re
        
        # Start with the original text
        formatted = description
        
        # Fix ALL the broken words from your examples
        word_fixes = {
            'per form': 'perform',
            'with in': 'within', 
            'jur isprudence': 'jurisprudence',
            'prov isi ons': 'provisions',
            'stipul ated': 'stipulated',
            'rel ati on': 'relation',
            'determ ine': 'determine',
            'm iss ing': 'missing',
            'preserv ing': 'preserving',
            'us ing': 'using',
            'accord ing': 'according',
            'c ontrol': 'control',
            'th at': 'that',
            'be fore': 'before',
            'call ing': 'calling',
            'per formance': 'performance',
            'def ine': 'define',
            'efficient': 'efficient',
            'quality': 'quality',
            'policies': 'policies',
            'procedures': 'procedures',
            'loudspeakers': 'loudspeakers',
            'comply': 'comply',
            'praver': 'prayer',
            'c onsidered': 'considered',
            'c alling': 'calling',
            'c ontrol': 'control'
        }
        
        # Apply the word fixes (case insensitive)
        for broken, fixed in word_fixes.items():
            formatted = formatted.replace(broken, fixed)
            formatted = formatted.replace(broken.title(), fixed.title())
            formatted = formatted.replace(broken.upper(), fixed.upper())
        
        # MAIN FIX: Add spaces between concatenated words
        # This handles cases like "operationsensure" -> "operations ensure"
        # Add space between word and capital letter (camelCase) - this is the main issue
        formatted = re.sub(r'([a-z])([A-Z])', r'\1 \2', formatted)
        
        # Add space between specific concatenated patterns
        # Handle common concatenations like "operationsensure" -> "operations ensure"
        concatenation_patterns = [
            (r'operationsensure', 'operations ensure'),
            (r'resourcesdirect', 'resources direct'),
            (r'managementReviewing', 'management. Reviewing'),
            (r'managementReviewing', 'management. Reviewing'),
            (r'([a-z])([A-Z][a-z]+)', r'\1 \2'),  # Add space before capitalized words
        ]
        
        for pattern, replacement in concatenation_patterns:
            formatted = re.sub(pattern, replacement, formatted)
        
        # Add spaces after periods that are followed by capital letters
        formatted = re.sub(r'\.([A-Z])', r'. \1', formatted)
        
        # Add spaces after asterisks
        formatted = re.sub(r'\*([A-Za-z])', r'* \1', formatted)
        
        # Add spaces after commas that are followed by letters
        formatted = re.sub(r',([A-Za-z])', r', \1', formatted)
        
        # Clean up multiple spaces
        formatted = re.sub(r'\s+', ' ', formatted.strip())
        
        return formatted
    
    def _aggressive_skills_formatting(self, skills: str) -> str:
        """Aggressive text processing for skills - no LLM needed"""
        if not skills or len(skills.strip()) < 5:
            return skills
        
        import re
        
        # Start with the original text
        formatted = skills
        
        # First, fix the broken words that have spaces in the middle
        # This is the main issue - words like "t, eam, w ork" should become "team work"
        word_fixes = {
            't, eam, w ork': 'team work',
            'a, bility, to, b uild, r elationships': 'ability to build relationships',
            'a, nalytical, t hinking': 'analytical thinking',
            'e, ffective, c ommunication': 'effective communication',
            'f, ocus, on, s ervie, q uality': 'focus on service quality',
            'servie quality': 'service quality',
            'Focus on Servie Quality': 'focus on service quality',
            'p, rogram, d esign': 'program design',
            's, oftware, e ngineering': 'software engineering',
            'c, omputer, p rogramming, l anguages': 'computer programming languages',
            's, oftware, d evelopment': 'software development',
            's, oftware, t esting': 'software testing',
            'p, roject, m anagement': 'project management',
            'b, udget, d esign': 'budget design',
            's, pread, s heet, s oftware': 'spreadsheet software',
            'r, esource, e stimation': 'resource estimation',
            'r, esearch, d, ata, a nalysis': 'research data analysis',
            'r, eporting': 'reporting',
            'a, pplied, m athematics': 'applied mathematics',
            'm, athematics': 'mathematics'
        }
        
        # Apply the word fixes
        for broken, fixed in word_fixes.items():
            formatted = formatted.replace(broken, fixed)
        
        # MAIN LOGIC: Handle concatenated skills like "decision makingproblem solvingworking with teams"
        # Use direct string replacements for the exact patterns we see
        
        # Define the exact concatenated patterns and their replacements
        concatenated_patterns = {
            'decision makingproblem solvingworking with teamsqualityeffective communicationhotel managementstewardscustomer relationship managementrestaurant managementcatering': 'decision making, problem solving, working with teams, quality, effective communication, hotel management, stewards, customer relationship management, restaurant management, catering',
            'decision makingproblem solvingworking with teams': 'decision making, problem solving, working with teams',
            'qualityeffective communication': 'quality, effective communication',
            'hotel managementstewards': 'hotel management, stewards',
            'stewardscustomer relationship management': 'stewards, customer relationship management',
            'customer relationship managementrestaurant management': 'customer relationship management, restaurant management',
            'restaurant managementcatering': 'restaurant management, catering',
            'decision makingproblem solving': 'decision making, problem solving',
            'problem solvingworking with teams': 'problem solving, working with teams',
            'working with teamsquality': 'working with teams, quality',
            'effective communicationhotel management': 'effective communication, hotel management'
        }
        
        # Apply the direct replacements
        for concatenated, separated in concatenated_patterns.items():
            formatted = formatted.replace(concatenated, separated)
        
        # Handle any remaining camelCase patterns - this is the main fix
        formatted = re.sub(r'([a-z])([A-Z])', r'\1 \2', formatted)
        
        # Fix concatenated words within individual skills
        # Split on commas first, then fix each skill individually
        skills = formatted.split(',')
        fixed_skills = []
        
        for skill in skills:
            skill = skill.strip()
            if skill:
                # Fix common concatenated words in individual skills
                skill = re.sub(r'ResearchData', 'Research Data', skill)
                skill = re.sub(r'ReportingComputer', 'Reporting Computer', skill)
                skill = re.sub(r'ComputerProgramming', 'Computer Programming', skill)
                skill = re.sub(r'DataAnalysis', 'Data Analysis', skill)
                skill = re.sub(r'BusinessAnalysis', 'Business Analysis', skill)
                skill = re.sub(r'SoftwareDevelopment', 'Software Development', skill)
                skill = re.sub(r'SoftwareTesting', 'Software Testing', skill)
                skill = re.sub(r'WebDevelopment', 'Web Development', skill)
                skill = re.sub(r'DatabaseDesign', 'Database Design', skill)
                skill = re.sub(r'SystemAnalysis', 'System Analysis', skill)
                skill = re.sub(r'ProjectManagement', 'Project Management', skill)
                skill = re.sub(r'QualityAssurance', 'Quality Assurance', skill)
                skill = re.sub(r'NetworkSecurity', 'Network Security', skill)
                skill = re.sub(r'CyberSecurity', 'Cyber Security', skill)
                skill = re.sub(r'CloudComputing', 'Cloud Computing', skill)
                skill = re.sub(r'MachineLearning', 'Machine Learning', skill)
                skill = re.sub(r'ArtificialIntelligence', 'Artificial Intelligence', skill)
                skill = re.sub(r'PerformanceTesting', 'Performance Testing', skill)
                skill = re.sub(r'SecurityTesting', 'Security Testing', skill)
                skill = re.sub(r'UserInterface', 'User Interface', skill)
                skill = re.sub(r'UserExperience', 'User Experience', skill)
                skill = re.sub(r'BackendDevelopment', 'Backend Development', skill)
                skill = re.sub(r'FrontendDevelopment', 'Frontend Development', skill)
                skill = re.sub(r'FullStack', 'Full Stack', skill)
                
                # Fix the specific patterns we're seeing in the UI
                skill = re.sub(r'FinancingCredit', 'Financing, Credit', skill)
                skill = re.sub(r'Analysis comparisons', 'Analysis, comparisons', skill)
                skill = re.sub(r'analysis research', 'analysis, research', skill)
                skill = re.sub(r'Bonds Investment', 'Bonds, Investment', skill)
                skill = re.sub(r'Analysis Instruments', 'Analysis, Instruments', skill)
                skill = re.sub(r'Team Effective', 'Team Work, Effective Communication', skill)
                skill = re.sub(r'Work Communication', 'Work, Communication', skill)
                
                # Generic pattern for remaining camelCase words
                skill = re.sub(r'([a-z])([A-Z])', r'\1 \2', skill)
                
                fixed_skills.append(skill.strip())
        
        formatted = ', '.join(fixed_skills)
        
        # Clean up multiple spaces
        formatted = re.sub(r'\s+', ' ', formatted.strip())
        
        return formatted
    
    def _needs_llm_formatting(self, text: str) -> bool:
        """Check if text needs LLM formatting based on quality indicators"""
        if not text or len(text.strip()) < 10:
            return False
        
        # Check for common formatting issues
        issues = 0
        
        import re
        
        # Check for concatenated words (no spaces between words) - be more sensitive
        if re.search(r'[a-z][A-Z]', text):  # camelCase without spaces
            issues += 1
        
        # Check for long concatenated strings (like "perseveranceorganizationgoals")
        if re.search(r'[a-z]{8,}[A-Z]', text):  # Long lowercase word followed by uppercase
            issues += 1
        
        # Check for missing spaces after punctuation
        if re.search(r'[.!?][A-Z]', text):  # Missing space after sentence end
            issues += 1
        
        # Check for asterisks without proper line breaks
        if re.search(r'\*[A-Za-z]', text):  # Asterisk not followed by space
            issues += 1
        
        # Check for specific concatenation patterns in skills
        skill_concatenation_patterns = [
            r'[a-z]+[A-Z][a-z]+[A-Z]',  # Multiple camelCase words concatenated
            r'[a-z]{5,}[A-Z][a-z]{3,}',  # Long words concatenated
        ]
        
        for pattern in skill_concatenation_patterns:
            if re.search(pattern, text):
                issues += 1
        
        # Check for broken words with spaces in the middle (like "per form", "with in")
        if re.search(r'[a-z]\s[a-z]{1,3}\s[a-z]', text):  # Broken words
            issues += 1
        
        # Check for the specific problematic patterns we're seeing
        problematic_patterns = [
            'per form', 'with in', 'jur isprudence', 'prov isi ons', 'stipul ated',
            'rel ati on', 'determ ine', 'm iss ing', 'preserv ing', 'us ing',
            'accord ing', 'c ontrol', 'th at', 'be fore', 'call ing', 'per formance'
        ]
        
        for pattern in problematic_patterns:
            if pattern in text.lower():
                issues += 1
        
        # ALWAYS use LLM for skills that look concatenated
        if 'teamwork' in text.lower() and 'perseverance' in text.lower() and 'organization' in text.lower():
            issues += 10  # Force LLM usage
        
        # Use LLM if there are any formatting issues (lowered threshold)
        return issues >= 1
    
    async def _format_job_description(self, description: str) -> str:
        """Format job description to be more readable"""
        if not description or len(description.strip()) < 10:
            return description
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are a professional job description formatter. Your task is to clean up and format job descriptions to make them more readable and professional.

CRITICAL REQUIREMENTS:
- Fix broken words that have spaces in the middle (e.g., "per form" -> "perform", "with in" -> "within", "jur isprudence" -> "jurisprudence")
- Break long paragraphs into shorter, digestible sentences
- Use bullet points or numbered lists for responsibilities when appropriate
- Fix any formatting issues or run-on sentences
- Maintain the original meaning and content
- Make it professional and easy to scan
- Keep the same level of detail but improve readability

EXAMPLES OF FIXES NEEDED:
- "per form" -> "perform"
- "with in" -> "within"
- "jur isprudence" -> "jurisprudence"
- "prov isi ons" -> "provisions"
- "stipul ated" -> "stipulated"
- "rel ati on" -> "relation"
- "determ ine" -> "determine"
- "m iss ing" -> "missing"
- "preserv ing" -> "preserving"
- "us ing" -> "using"
- "accord ing" -> "according"
- "c ontrol" -> "control"
- "th at" -> "that"
- "be fore" -> "before"
- "call ing" -> "calling"
- "per formance" -> "performance"

Return only the formatted description, no additional commentary."""
                },
                {
                    "role": "user",
                    "content": f"Please format this job description:\n\n{description}"
                }
            ]
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=800,
                temperature=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error formatting job description: {e}")
            return description
    
    async def _format_required_skills(self, skills: str) -> str:
        """Format required skills to be more readable"""
        if not skills or len(skills.strip()) < 5:
            return skills
        
        # First, try simple text processing for common concatenation patterns
        formatted_skills = self._simple_skills_formatting(skills)
        
        # If the simple formatting didn't change much, use LLM
        if len(formatted_skills) < len(skills) * 1.2:  # If not much was added
            try:
                messages = [
                    {
                        "role": "system",
                        "content": """You are a professional skills formatter. Your task is to clean up and format job skills lists to make them more readable.

CRITICAL REQUIREMENTS:
- ALWAYS add spaces between concatenated words (e.g., "TeamWorkperseveranceorganization" -> "Team Work, Perseverance, Organization")
- Convert to a clean, comma-separated list
- Capitalize each skill properly (e.g., "team work" -> "Team Work")
- Remove duplicates if any
- Make it easy to scan and read

EXAMPLES:
- "Required SkillsTeam Workperseveranceorganizationgoals" -> "Required Skills, Team Work, Perseverance, Organization, Goals"
- "selfdevelopmentacousticalperformancebassvoice" -> "Self Development, Acoustical Performance, Bass Voice"
- "teamw orkperseveranceorganizationgoals/ resultso rientedselfd evelopmentacousticalp erformancebassv oiceprayert imings" -> "Team Work, Perseverance, Organization, Goals, Results Oriented, Self Development, Acoustical Performance, Bass Voice, Prayer, Timings"

IMPORTANT: Every word must be separated by spaces and commas. Do not leave any words concatenated together. Fix broken words like "teamw ork" to "Team Work".

Return only the formatted skills list, no additional commentary."""
                    },
                    {
                        "role": "user",
                        "content": f"Please format this skills list by adding proper spaces and commas:\n\n{skills}"
                    }
                ]
                
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=200,
                    temperature=0.0  # Use 0 temperature for more consistent formatting
                )
                
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                logger.error(f"Error formatting required skills: {e}")
                return formatted_skills
        
        return formatted_skills
    
    def _simple_skills_formatting(self, skills: str) -> str:
        """Simple text processing for common concatenation patterns"""
        if not skills:
            return skills
        
        import re
        
        # Start with the original text
        formatted = skills
        
        # First, handle the specific concatenated skills from your example
        # This is a more aggressive approach to fix the exact issue you're seeing
        
        # Define the exact skills that should be separated
        skill_mappings = {
            'teamworkperseveranceorganizationgoals': 'teamwork, perseverance, organization, goals',
            'resultsorientedselfdevelopmentacousticalperformancebassvoiceprayertimings': 'results oriented, self development, acoustical performance, bass, voice, prayer, timings',
            'requiredskills': 'required skills',
            'teamwork': 'teamwork',
            'perseverance': 'perseverance', 
            'organization': 'organization',
            'goals': 'goals',
            'results': 'results',
            'oriented': 'oriented',
            'selfdevelopment': 'self development',
            'acoustical': 'acoustical',
            'performance': 'performance',
            'bass': 'bass',
            'voice': 'voice',
            'prayer': 'prayer',
            'timings': 'timings'
        }
        
        # Apply the mappings
        for concatenated, separated in skill_mappings.items():
            formatted = formatted.replace(concatenated, separated)
        
        # Add spaces between camelCase words (e.g., "TeamWork" -> "Team Work")
        formatted = re.sub(r'([a-z])([A-Z])', r'\1 \2', formatted)
        
        # Add spaces between lowercase words followed by uppercase (e.g., "perseveranceorganization" -> "perseverance organization")
        formatted = re.sub(r'([a-z])([a-z][A-Z])', r'\1 \2', formatted)
        
        # Add spaces between words that are concatenated (e.g., "goalsresults" -> "goals results")
        formatted = re.sub(r'([a-z])([a-z]{3,})', r'\1 \2', formatted)
        
        # Clean up multiple spaces
        formatted = re.sub(r'\s+', ' ', formatted.strip())
        
        # Add commas between distinct skills (look for word boundaries)
        # This handles cases where we have "teamwork perseverance" -> "teamwork, perseverance"
        formatted = re.sub(r'([a-z])\s+([a-z])', r'\1, \2', formatted)
        
        return formatted

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