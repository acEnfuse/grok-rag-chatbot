#!/usr/bin/env python3
"""
Simple test script for the HRSD Job Matching System
"""

import asyncio
import os
import sys
from backend.services.milvus_service import MilvusService
from backend.services.groq_service import GroqService
from backend.services.cv_processor import CVProcessor
from backend.services.job_embedder import JobEmbedder

async def test_hrsd_system():
    """Test the HRSD system components"""
    print("🧪 Testing HRSD Job Matching System...")
    print("=" * 50)
    
    # Check environment variables
    print("1. Checking environment variables...")
    if not os.getenv("GROQ_API_KEY"):
        print("❌ GROQ_API_KEY not set")
        return False
    else:
        print("✅ GROQ_API_KEY is set")
    
    if not os.getenv("MILVUS_HOST"):
        print("⚠️  MILVUS_HOST not set, using localhost")
        os.environ["MILVUS_HOST"] = "localhost"
    
    print("✅ Environment variables OK")
    print()
    
    # Test CV Processor
    print("2. Testing CV Processor...")
    try:
        cv_processor = CVProcessor()
        test_cv_text = """
        John Doe
        Software Engineer
        john.doe@email.com
        +966 50 123 4567
        
        Experience:
        - 5 years of Python development
        - React and JavaScript expertise
        - SQL and database management
        - Team leadership experience
        
        Education:
        - Bachelor's in Computer Science
        - Master's in Software Engineering
        
        Skills:
        Python, JavaScript, React, SQL, Git, Docker, AWS
        """
        
        cv_data = await cv_processor.process_cv_from_text(test_cv_text)
        print(f"✅ CV processed successfully")
        print(f"   - Name: {cv_data.get('personal_info', {}).get('name', 'N/A')}")
        print(f"   - Skills found: {len(cv_data.get('skills', []))}")
        print(f"   - Experience entries: {len(cv_data.get('experience', []))}")
        
    except Exception as e:
        print(f"❌ CV Processor test failed: {e}")
        return False
    
    print()
    
    # Test Milvus Service
    print("3. Testing Milvus Service...")
    try:
        milvus_service = MilvusService()
        await milvus_service.initialize()
        print("✅ Milvus service initialized")
        
        # Get collection info
        stats = await milvus_service.get_collection_info()
        print(f"   - Collection: {stats.get('collection_name', 'N/A')}")
        print(f"   - Document count: {stats.get('row_count', 0)}")
        
    except Exception as e:
        print(f"❌ Milvus service test failed: {e}")
        print("   Make sure Milvus is running and accessible")
        return False
    
    print()
    
    # Test Job Embedder
    print("4. Testing Job Embedder...")
    try:
        job_embedder = JobEmbedder()
        await job_embedder.initialize()
        print("✅ Job embedder initialized")
        
        # Create sample jobs
        sample_jobs = job_embedder.create_sample_jobs()
        print(f"   - Created {len(sample_jobs)} sample jobs")
        
        # Add one sample job
        if sample_jobs:
            result = await job_embedder.add_single_job(sample_jobs[0])
            print(f"   - Added sample job: {result.get('inserted_count', 0)}")
        
    except Exception as e:
        print(f"❌ Job embedder test failed: {e}")
        return False
    
    print()
    
    # Test Groq Service
    print("5. Testing Groq Service...")
    try:
        groq_service = GroqService()
        
        # Test simple response
        test_response = await groq_service.generate_response(
            query="Hello, can you help me with job matching?",
            context_docs=[],
            chat_history=[]
        )
        
        print("✅ Groq service working")
        print(f"   - Response length: {len(test_response)} characters")
        
    except Exception as e:
        print(f"❌ Groq service test failed: {e}")
        return False
    
    print()
    
    # Test Job Matching
    print("6. Testing Job Matching...")
    try:
        # Search for jobs
        matched_jobs = await milvus_service.search_jobs(test_cv_text, top_k=3)
        print(f"✅ Job search completed")
        print(f"   - Found {len(matched_jobs)} job matches")
        
        if matched_jobs:
            best_match = matched_jobs[0]
            print(f"   - Best match: {best_match.get('job_title', 'N/A')} ({best_match.get('match_score', 0)}%)")
        
    except Exception as e:
        print(f"❌ Job matching test failed: {e}")
        return False
    
    print()
    print("🎉 All tests passed! HRSD system is ready to use.")
    print("=" * 50)
    return True

async def main():
    """Main test function"""
    try:
        success = await test_hrsd_system()
        if success:
            print("\n✅ System is ready! You can now:")
            print("   1. Run the backend: ./run-hrsd.sh")
            print("   2. Start the frontend: cd frontend && npm start")
            print("   3. Visit: http://localhost:3000")
        else:
            print("\n❌ System tests failed. Please check the errors above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
