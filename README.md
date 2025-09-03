# HRSD Job Matching System

A comprehensive AI-powered job matching platform for the Human Resources and Social Development (HRSD) ministry of Saudi Arabia. This system helps job seekers find relevant career opportunities by analyzing their CVs and matching them with available positions using advanced semantic search and AI-powered career advice.

## 🚀 Features

### Core Functionality
- **CV Processing**: Supports multiple file formats (PDF, DOC, DOCX, TXT)
- **AI-Powered Job Matching**: Uses semantic search to find relevant job opportunities
- **Career Advice**: Interactive AI assistant powered by Groq LLM
- **Real-time Analysis**: Instant CV analysis and job matching results
- **Secure Processing**: CV data is processed securely and not stored permanently

### Technical Features
- **Vector Database**: Milvus integration for efficient job opportunity storage and retrieval
- **Semantic Search**: Advanced embedding-based job matching
- **Modern UI**: React frontend with HRSD branding and responsive design
- **RESTful API**: FastAPI backend with comprehensive endpoints
- **Document Processing**: Robust text extraction and cleaning from various file formats

## 🏗️ Architecture

### Frontend (React)
- **Components**: FileUpload, JobMatches, ChatInterface
- **Styling**: Tailwind CSS with HRSD color scheme
- **State Management**: React hooks for application state
- **API Integration**: RESTful communication with backend

### Backend (FastAPI)
- **Services**: 
  - `MilvusService`: Vector database operations
  - `CVProcessor`: Document parsing and text extraction
  - `JobEmbedder`: Job opportunity management and embedding
  - `GroqService`: AI-powered career advice and analysis
- **Endpoints**: Health checks, CV upload, job matching, chat functionality

### Database (Milvus)
- **Collection**: `hrsd` - stores job opportunities with embeddings
- **Schema**: Job title, description, requirements, location, salary, etc.
- **Search**: Semantic similarity search for job matching

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- Conda (recommended for environment management)
- Milvus database instance

### Backend Setup

1. **Create Conda Environment**
   ```bash
   conda create -n hrsd-job-matcher python=3.9
   conda activate hrsd-job-matcher
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements-hrsd.txt
   ```

3. **Set Environment Variables**
   ```bash
   export GROQ_API_KEY="your_groq_api_key_here"
   ```

4. **Start Backend Server**
   ```bash
   ./run-hrsd.sh
   ```
   Or manually:
   ```bash
   uvicorn app_hrsd:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to Frontend Directory**
   ```bash
   cd frontend
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Start Development Server**
   ```bash
   npm start
   ```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 📁 Project Structure

```
rag_chatbot/
├── app_hrsd.py                 # Main FastAPI application
├── backend/
│   └── services/
│       ├── milvus_service.py   # Milvus database operations
│       ├── cv_processor.py     # CV document processing
│       ├── job_embedder.py     # Job opportunity management
│       ├── groq_service.py     # AI/LLM integration
│       └── document_processor.py # Legacy document processor
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── services/           # API service functions
│   │   └── styles/             # CSS styling
│   └── public/                 # Static assets
├── requirements-hrsd.txt       # Python dependencies
├── run-hrsd.sh                # Backend startup script
└── README.md                  # This file
```

## 🔧 Configuration

### Environment Variables
- `GROQ_API_KEY`: Required for AI-powered features
- `MILVUS_HOST`: Milvus database host (default: localhost)
- `MILVUS_PORT`: Milvus database port (default: 19530)

### HRSD Branding
The application uses the official HRSD color scheme:
- Primary Green: `#10412A`
- Light Green: `#F3FCF5`
- Gray: `#F3F4F6`
- White: `#FFFFFF`

## 📊 API Endpoints

### Core Endpoints
- `GET /` - Health check and system information
- `POST /upload-cv` - Upload and process CV for job matching
- `GET /collection-stats` - Get database collection statistics
- `POST /chat` - AI-powered career advice chat

### Job Management
- `POST /add-job` - Add individual job opportunity
- `POST /add-jobs` - Bulk add job opportunities
- `POST /add-sample-jobs` - Add sample job data for testing

## 🎯 Usage

### For Job Seekers
1. **Upload CV**: Drag and drop or browse to upload your CV
2. **Get Matches**: System analyzes your CV and finds matching job opportunities
3. **AI Advice**: Ask questions about your career or job opportunities
4. **Review Results**: View detailed job matches with compatibility scores

### For Administrators
1. **Add Jobs**: Use API endpoints to add new job opportunities
2. **Monitor System**: Check collection statistics and system health
3. **Manage Data**: Update or remove job opportunities as needed

## 🔒 Security & Privacy

- **Data Processing**: CVs are processed in memory and not permanently stored
- **Secure API**: All endpoints require proper authentication
- **Privacy First**: User data is handled according to privacy best practices
- **Local Processing**: Document parsing happens locally for security

## 🧪 Testing

Run the test suite to verify system functionality:
```bash
python test_hrsd_system.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is developed for the Human Resources and Social Development (HRSD) ministry of Saudi Arabia.

## 🆘 Support

For technical support or questions:
- Check the API documentation at `/docs` endpoint
- Review the test files for usage examples
- Contact the development team

## 🔄 Version History

- **v1.0.0**: Initial HRSD Job Matching System release
  - Complete CV processing and job matching
  - AI-powered career advice
  - HRSD-branded React frontend
  - FastAPI backend with Milvus integration

---

**Powered by Groq AI** 🤖