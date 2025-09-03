import os
import csv
import json
from typing import List, Dict, Any, Optional
import logging
from .milvus_service import MilvusService

logger = logging.getLogger(__name__)

class JobEmbedder:
    def __init__(self):
        self.milvus_service = MilvusService()
    
    async def initialize(self):
        """Initialize the job embedder"""
        await self.milvus_service.initialize()
        logger.info("Job embedder initialized successfully")
    
    async def add_jobs_from_csv(self, csv_file_path: str) -> Dict[str, Any]:
        """Add jobs from a CSV file to the HRSD collection"""
        try:
            jobs = self._parse_csv_jobs(csv_file_path)
            if not jobs:
                return {"error": "No valid jobs found in CSV file"}
            
            result = await self.milvus_service.add_jobs(jobs)
            logger.info(f"Added {len(jobs)} jobs from CSV file")
            return result
            
        except Exception as e:
            logger.error(f"Error adding jobs from CSV: {e}")
            raise
    
    async def add_jobs_from_json(self, json_file_path: str) -> Dict[str, Any]:
        """Add jobs from a JSON file to the HRSD collection"""
        try:
            jobs = self._parse_json_jobs(json_file_path)
            if not jobs:
                return {"error": "No valid jobs found in JSON file"}
            
            result = await self.milvus_service.add_jobs(jobs)
            logger.info(f"Added {len(jobs)} jobs from JSON file")
            return result
            
        except Exception as e:
            logger.error(f"Error adding jobs from JSON: {e}")
            raise
    
    async def add_single_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a single job to the HRSD collection"""
        try:
            # Validate job data
            if not self._validate_job_data(job_data):
                return {"error": "Invalid job data provided"}
            
            result = await self.milvus_service.add_jobs([job_data])
            logger.info("Added single job to collection")
            return result
            
        except Exception as e:
            logger.error(f"Error adding single job: {e}")
            raise
    
    def _parse_csv_jobs(self, csv_file_path: str) -> List[Dict[str, Any]]:
        """Parse jobs from CSV file"""
        jobs = []
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(file, delimiter=delimiter)
                
                for row_num, row in enumerate(reader, 1):
                    try:
                        job = self._convert_csv_row_to_job(row)
                        if job:
                            jobs.append(job)
                    except Exception as e:
                        logger.warning(f"Error parsing row {row_num}: {e}")
                        continue
            
            logger.info(f"Parsed {len(jobs)} jobs from CSV file")
            return jobs
            
        except Exception as e:
            logger.error(f"Error parsing CSV file: {e}")
            raise
    
    def _parse_json_jobs(self, json_file_path: str) -> List[Dict[str, Any]]:
        """Parse jobs from JSON file"""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            jobs = []
            if isinstance(data, list):
                # Array of jobs
                for job_data in data:
                    if self._validate_job_data(job_data):
                        jobs.append(job_data)
            elif isinstance(data, dict):
                # Single job or object with jobs array
                if 'jobs' in data and isinstance(data['jobs'], list):
                    for job_data in data['jobs']:
                        if self._validate_job_data(job_data):
                            jobs.append(job_data)
                elif self._validate_job_data(data):
                    jobs.append(data)
            
            logger.info(f"Parsed {len(jobs)} jobs from JSON file")
            return jobs
            
        except Exception as e:
            logger.error(f"Error parsing JSON file: {e}")
            raise
    
    def _convert_csv_row_to_job(self, row: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Convert CSV row to job dictionary"""
        try:
            # Map common CSV column names to our job structure
            job = {}
            
            # Job title mapping
            title_fields = ['job_title', 'title', 'position', 'role', 'job_name']
            job['job_title'] = self._get_field_value(row, title_fields)
            
            # Company mapping
            company_fields = ['company', 'employer', 'organization', 'firm']
            job['company'] = self._get_field_value(row, company_fields)
            
            # Description mapping
            desc_fields = ['description', 'job_description', 'summary', 'details']
            job['description'] = self._get_field_value(row, desc_fields)
            
            # Skills mapping
            skills_fields = ['skills', 'required_skills', 'qualifications', 'requirements']
            job['required_skills'] = self._get_field_value(row, skills_fields)
            
            # Experience level mapping
            exp_fields = ['experience_level', 'level', 'seniority', 'experience']
            job['experience_level'] = self._get_field_value(row, exp_fields)
            
            # Education mapping
            edu_fields = ['education', 'education_requirements', 'degree', 'qualification']
            job['education_requirements'] = self._get_field_value(row, edu_fields)
            
            # Location mapping
            loc_fields = ['location', 'city', 'address', 'place']
            job['location'] = self._get_field_value(row, loc_fields)
            
            # Salary mapping
            salary_fields = ['salary', 'salary_range', 'compensation', 'pay']
            job['salary_range'] = self._get_field_value(row, salary_fields)
            
            # Validate that we have at least job title and description
            if not job.get('job_title') or not job.get('description'):
                return None
            
            return job
            
        except Exception as e:
            logger.error(f"Error converting CSV row to job: {e}")
            return None
    
    def _get_field_value(self, row: Dict[str, str], field_names: List[str]) -> str:
        """Get field value from row using multiple possible field names"""
        for field_name in field_names:
            # Try exact match
            if field_name in row and row[field_name]:
                return str(row[field_name]).strip()
            
            # Try case-insensitive match
            for key, value in row.items():
                if key.lower() == field_name.lower() and value:
                    return str(value).strip()
        
        return ""
    
    def _validate_job_data(self, job_data: Dict[str, Any]) -> bool:
        """Validate job data structure"""
        try:
            # Check required fields
            required_fields = ['job_title', 'description']
            for field in required_fields:
                if not job_data.get(field) or not str(job_data[field]).strip():
                    return False
            
            # Check field types
            string_fields = [
                'job_title', 'company', 'description', 'required_skills',
                'experience_level', 'education_requirements', 'location', 'salary_range'
            ]
            
            for field in string_fields:
                if field in job_data and not isinstance(job_data[field], str):
                    job_data[field] = str(job_data[field])
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating job data: {e}")
            return False
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the HRSD collection"""
        try:
            return await self.milvus_service.get_collection_info()
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"error": str(e)}
    
    async def clear_collection(self) -> Dict[str, Any]:
        """Clear all jobs from the HRSD collection"""
        try:
            # This would require implementing a clear method in MilvusService
            # For now, return a message
            return {"message": "Collection clear functionality not implemented yet"}
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            return {"error": str(e)}
    
    def create_sample_jobs(self) -> List[Dict[str, Any]]:
        """Create sample job data for testing"""
        sample_jobs = [
            {
                "job_title": "Software Engineer",
                "company": "TechCorp",
                "description": "We are looking for a skilled software engineer to join our development team. You will be responsible for designing, developing, and maintaining software applications using modern technologies.",
                "required_skills": "Python, JavaScript, React, SQL, Git, Docker",
                "experience_level": "Mid-level",
                "education_requirements": "Bachelor's degree in Computer Science or related field",
                "location": "Riyadh, Saudi Arabia",
                "salary_range": "15,000 - 25,000 SAR"
            },
            {
                "job_title": "Data Scientist",
                "company": "DataAnalytics Inc",
                "description": "Join our data science team to analyze large datasets and build machine learning models. You will work with stakeholders to understand business requirements and deliver actionable insights.",
                "required_skills": "Python, Machine Learning, Statistics, SQL, Pandas, Scikit-learn",
                "experience_level": "Senior",
                "education_requirements": "Master's degree in Data Science, Statistics, or related field",
                "location": "Jeddah, Saudi Arabia",
                "salary_range": "20,000 - 35,000 SAR"
            },
            {
                "job_title": "Project Manager",
                "company": "Construction Solutions",
                "description": "Lead construction projects from planning to completion. Coordinate with teams, manage budgets, and ensure projects are delivered on time and within scope.",
                "required_skills": "Project Management, Leadership, Communication, Budget Management, Risk Assessment",
                "experience_level": "Senior",
                "education_requirements": "Bachelor's degree in Engineering or Project Management",
                "location": "Dammam, Saudi Arabia",
                "salary_range": "18,000 - 30,000 SAR"
            }
        ]
        
        return sample_jobs
