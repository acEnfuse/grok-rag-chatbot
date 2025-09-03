# HRSD Job Matching System

An AI-powered job matching system for the Human Resources and Social Development (HRSD) ministry of Saudi Arabia. This system helps job seekers find suitable employment opportunities by analyzing their CVs and matching them with available positions using advanced AI and vector search technology.

## 🚀 Features

- **CV Processing**: Supports PDF, DOC, DOCX, and TXT file formats
- **AI-Powered Matching**: Uses Groq's LLM and vector embeddings for intelligent job matching
- **Interactive Chat**: Chat with an AI career advisor for personalized guidance
- **Modern UI**: Clean, responsive React frontend with HRSD branding
- **RESTful API**: FastAPI backend with comprehensive endpoints
- **Vector Database**: Milvus for efficient similarity search

## 🏗️ Architecture

### Backend (FastAPI)
- **CV Processor**: Extracts and parses CV information
- **Job Embedder**: Manages job opportunity data in vector database
- **Milvus Service**: Handles vector search and similarity matching
- **Groq Service**: AI-powered job matching and career advice

### Frontend (React)
- **File Upload**: Drag-and-drop CV upload interface
- **Job Matches**: Display matching opportunities with scores
- **Chat Interface**: Interactive career advisor
- **Responsive Design**: Mobile-friendly HRSD-themed UI

## 🛠️ Installation

### Prerequisites
- Python 3.13+
- Node.js 16+
- Conda or Miniconda
- Milvus database (local or cloud)

### Backend Setup

1. **Create Conda Environment**:
   ```bash
   conda create -n hrsd-job-matcher python=3.13
   conda activate hrsd-job-matcher
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements-hrsd.txt
   ```

3. **Set Environment Variables**:
   ```bash
   export GROQ_API_KEY="your-groq-api-key"
   export MILVUS_HOST="localhost"  # or your Milvus host
   export MILVUS_PORT="19530"
   export MILVUS_TOKEN="your-milvus-token"  # if required
   ```

4. **Start Backend**:
   ```bash
   ./run-hrsd.sh
   ```

### Frontend Setup

1. **Install Dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start Development Server**:
   ```bash
   npm start
   ```

## 📖 Usage

### 1. Upload CV
- Navigate to the web interface
- Upload your CV in PDF, DOC, DOCX, or TXT format
- The system will automatically process and analyze your CV

### 2. View Job Matches
- Get personalized job recommendations with match scores
- View detailed job descriptions, requirements, and locations
- See AI-generated analysis of your profile

### 3. Chat with Advisor
- Ask questions about career development
- Get advice on skills improvement
- Receive guidance on job applications

### 4. Admin Functions
- Add job opportunities via CSV or JSON upload
- View collection statistics
- Manage the job database

## 🔧 API Endpoints

### CV Processing
- `POST /upload-cv` - Upload and process CV file
- `POST /upload-cv-and-match` - Upload CV and get job matches
- `POST /match-jobs` - Match jobs based on CV text

### Job Management
- `POST /add-jobs` - Add jobs from CSV/JSON file
- `POST /add-sample-jobs` - Add sample job data
- `GET /collection-stats` - Get database statistics

### Chat
- `POST /chat` - Chat with AI career advisor

### Health
- `GET /health` - Health check endpoint
- `GET /` - API information

## 🎨 Design System

### Colors
- **Primary Green**: `#10412A` (HRSD brand color)
- **Light Green**: `#F3FCF5` (background)
- **Gray**: `#F3F4F6` (secondary background)
- **White**: `#FFFFFF` (cards and content)

### Typography
- **Headings**: Bold, modern sans-serif
- **Body**: Regular weight, readable sans-serif
- **UI Elements**: Clear, accessible contrast

## 🔒 Security & Privacy

- CV data is processed securely and not stored permanently
- All API communications use HTTPS in production
- Environment variables protect sensitive API keys
- File uploads are validated and sanitized

## 🚀 Deployment

### Backend Deployment
1. Set up production environment variables
2. Use a production ASGI server (e.g., Gunicorn with Uvicorn)
3. Configure reverse proxy (Nginx)
4. Set up SSL certificates

### Frontend Deployment
1. Build production bundle: `npm run build`
2. Serve static files with a web server
3. Configure API endpoint URLs
4. Set up CDN for assets

## 🧪 Testing

### Backend Tests
```bash
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📊 Monitoring

- Health check endpoint for uptime monitoring
- Logging configured for debugging and monitoring
- Collection statistics for database monitoring
- Error handling with detailed error messages

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is developed for the Human Resources and Social Development ministry of Saudi Arabia.

## 🆘 Support

For technical support or questions:
- Check the API documentation at `/docs` when running the backend
- Review the logs for error details
- Ensure all environment variables are properly set
- Verify Milvus database connectivity

## 🔄 Updates

### Version 1.0.0
- Initial release with core job matching functionality
- CV processing for multiple formats
- AI-powered matching with Groq
- React frontend with HRSD branding
- FastAPI backend with comprehensive endpoints
