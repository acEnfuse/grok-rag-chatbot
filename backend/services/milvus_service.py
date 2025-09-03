import os
import uuid
from typing import List, Dict, Any
from pymilvus import MilvusClient, DataType
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

class MilvusService:
    def __init__(self):
        self.client = None
        # Use hrsd collection for job matching
        self.collection_name = "hrsd"
        self.embedding_model = None  # Lazy load this
        self.embedding_model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self.dimension = 384  # all-MiniLM-L6-v2 embedding dimension
        
    def _get_embedding_model(self):
        """Lazy load the embedding model only when needed"""
        if self.embedding_model is None:
            logger.info(f"Loading embedding model: {self.embedding_model_name}")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            logger.info("✅ Embedding model loaded successfully")
        return self.embedding_model
        
    async def initialize(self):
        """Initialize Milvus client and create collection if needed"""
        try:
            cluster_ip = os.getenv("MILVUS_HOST")
            port = os.getenv("MILVUS_PORT", "19530")
            token = os.getenv("MILVUS_TOKEN")
            
            self.client = MilvusClient(
                uri=f"http://{cluster_ip}:{port}",
                token=token
            )
            
            # Check if collection exists
            if not self.client.has_collection(collection_name=self.collection_name):
                await self._create_collection()
                logger.info(f"Created collection: {self.collection_name}")
            else:
                logger.info(f"Collection {self.collection_name} already exists")
                
        except Exception as e:
            logger.error(f"Failed to initialize Milvus: {e}")
            raise
    
    async def _create_collection(self):
        """Create a new collection with the required schema for job opportunities"""
        schema = self.client.create_schema(
            auto_id=False,
            enable_dynamic_field=True
        )
        
        # Add fields for job opportunities
        schema.add_field(field_name="id", datatype=DataType.VARCHAR, max_length=100, is_primary=True)
        schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=self.dimension)
        schema.add_field(field_name="job_title", datatype=DataType.VARCHAR, max_length=255)
        schema.add_field(field_name="company", datatype=DataType.VARCHAR, max_length=255)
        schema.add_field(field_name="description", datatype=DataType.VARCHAR, max_length=65535)
        schema.add_field(field_name="required_skills", datatype=DataType.VARCHAR, max_length=2048)
        schema.add_field(field_name="experience_level", datatype=DataType.VARCHAR, max_length=50)
        schema.add_field(field_name="education_requirements", datatype=DataType.VARCHAR, max_length=1024)
        schema.add_field(field_name="location", datatype=DataType.VARCHAR, max_length=255)
        schema.add_field(field_name="salary_range", datatype=DataType.VARCHAR, max_length=100)
        
        # Create index
        index_params = self.client.prepare_index_params()
        index_params.add_index(
            field_name="vector",
            index_type="IVF_FLAT",
            metric_type="COSINE",
            params={"nlist": 1024}
        )
        
        # Create collection
        self.client.create_collection(
            collection_name=self.collection_name,
            schema=schema,
            index_params=index_params
        )
    
    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        model = self._get_embedding_model()  # Lazy load when needed
        embeddings = model.encode(texts)
        return embeddings.tolist()
    
    async def add_jobs(self, jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add job opportunities to the vector database"""
        try:
            if not jobs:
                return {"message": "No jobs to add"}
            
            # Prepare data for embedding (combine job description and requirements)
            texts = []
            for job in jobs:
                # Create a comprehensive text for embedding
                job_text = f"""
                Job Title: {job.get('job_title', '')}
                Company: {job.get('company', '')}
                Description: {job.get('description', '')}
                Required Skills: {job.get('required_skills', '')}
                Experience Level: {job.get('experience_level', '')}
                Education Requirements: {job.get('education_requirements', '')}
                Location: {job.get('location', '')}
                """
                texts.append(job_text.strip())
            
            embeddings = self._generate_embeddings(texts)
            
            data = []
            for job, embedding in zip(jobs, embeddings):
                data.append({
                    "id": str(uuid.uuid4()),
                    "vector": embedding,
                    "job_title": job.get("job_title", ""),
                    "company": job.get("company", ""),
                    "description": job.get("description", ""),
                    "required_skills": job.get("required_skills", ""),
                    "experience_level": job.get("experience_level", ""),
                    "education_requirements": job.get("education_requirements", ""),
                    "location": job.get("location", ""),
                    "salary_range": job.get("salary_range", "")
                })
            
            # Insert data
            result = self.client.insert(
                collection_name=self.collection_name,
                data=data
            )
            
            logger.info(f"Added {len(data)} jobs to Milvus collection: {self.collection_name}")
            return {"inserted_count": len(data), "ids": result}
            
        except Exception as e:
            logger.error(f"Error adding jobs to Milvus: {e}")
            raise
    
    async def search_jobs(self, cv_text: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Search for matching job opportunities based on CV"""
        try:
            # Generate query embedding from CV text
            query_embedding = self._generate_embeddings([cv_text])[0]
            
            # Search
            results = self.client.search(
                collection_name=self.collection_name,
                data=[query_embedding],
                anns_field="vector",
                search_params={"metric_type": "COSINE", "params": {"nprobe": 10}},
                output_fields=["job_title", "company", "description", "required_skills", 
                             "experience_level", "education_requirements", "location", "salary_range"],
                limit=top_k
            )
            
            # Format results
            jobs = []
            for hits in results:
                for hit in hits:
                    # Convert distance to similarity score (0-100%)
                    similarity_score = max(0, (1 - hit.get("distance", 1.0)) * 100)
                    
                    jobs.append({
                        "id": hit.get("id", "unknown"),
                        "job_title": hit.get("entity", {}).get("job_title", ""),
                        "company": hit.get("entity", {}).get("company", ""),
                        "description": hit.get("entity", {}).get("description", ""),
                        "required_skills": hit.get("entity", {}).get("required_skills", ""),
                        "experience_level": hit.get("entity", {}).get("experience_level", ""),
                        "education_requirements": hit.get("entity", {}).get("education_requirements", ""),
                        "location": hit.get("entity", {}).get("location", ""),
                        "salary_range": hit.get("entity", {}).get("salary_range", ""),
                        "match_score": round(similarity_score, 1)
                    })
            
            return jobs
            
        except Exception as e:
            logger.error(f"Error searching jobs: {e}")
            raise
    
    async def list_documents(self) -> List[Dict[str, Any]]:
        """List all unique documents in the collection"""
        try:
            # Query all documents grouped by filename
            results = self.client.query(
                collection_name=self.collection_name,
                filter="chunk_index >= 0",
                output_fields=["filename", "chunk_index"],
                limit=1000
            )
            
            # Group by filename
            files = {}
            for result in results:
                filename = result["filename"]
                if filename not in files:
                    files[filename] = {"filename": filename, "chunk_count": 0}
                files[filename]["chunk_count"] += 1
            
            return list(files.values())
            
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            raise
    
    async def delete_document(self, filename: str):
        """Delete all chunks of a specific document"""
        try:
            # Delete by filename
            self.client.delete(
                collection_name=self.collection_name,
                filter=f'filename == "{filename}"'
            )
            logger.info(f"Deleted document: {filename}")
            
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            raise
    
    async def list_app_collections(self) -> List[str]:
        """List only collections that belong to this app (with the prefix)"""
        try:
            all_collections = self.client.list_collections()
            app_collections = [col for col in all_collections if col.startswith(self.collection_prefix)]
            logger.info(f"Found app collections: {app_collections}")
            return app_collections
        except Exception as e:
            logger.error(f"Error listing app collections: {e}")
            raise
    
    async def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the current collection"""
        try:
            if not self.client.has_collection(self.collection_name):
                return {"error": f"Collection {self.collection_name} does not exist"}
            
            # Get actual document count by querying
            try:
                results = self.client.query(
                    collection_name=self.collection_name,
                    filter="chunk_index >= 0",
                    output_fields=["id"],
                    limit=16384  # High limit to get accurate count
                )
                actual_count = len(results)
            except Exception as query_error:
                logger.warning(f"Could not query collection for count: {query_error}")
                # Fallback to collection stats
                try:
                    stats = self.client.get_collection_stats(self.collection_name)
                    actual_count = stats.get("row_count", 0)
                except Exception:
                    actual_count = 0
            
            return {
                "collection_name": self.collection_name,
                "row_count": actual_count,
                "prefix": "hrsd",
                "base_name": self.collection_name
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {"error": str(e)} 