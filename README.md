# HRSD Job Matching System

A comprehensive AI-powered job matching platform for the Human Resources and Social Development (HRSD) ministry of Saudi Arabia. This system helps job seekers find relevant career opportunities by analyzing their CVs and matching them with available positions using advanced semantic search, intelligent LLM-based scoring, and AI-powered career advice.

## 🚀 Features

### Core Functionality
- **CV Processing**: Supports multiple file formats (PDF, DOC, DOCX, TXT) with advanced text cleaning
- **AI-Powered Job Matching**: Uses semantic search with LLM-based intelligent rescoring for accurate matches
- **Interactive Career Assistant**: Real-time AI chat powered by Groq LLM with persistent conversation history
- **Tabbed Interface**: Seamless switching between job matches and AI assistant with sticky navigation
- **Real-time Analysis**: Instant CV analysis and job matching results with detailed compatibility scores
- **Secure Processing**: CV data is processed securely and not stored permanently

### Advanced Features
- **Intelligent Scoring**: LLM-based job match rescoring for more accurate and logical results
- **Persistent Chat**: Conversation history persists when switching between tabs
- **Sticky Navigation**: Always-accessible toggle button in the header for seamless tab switching
- **Enhanced UI/UX**: Professional design with perfect centering, proper spacing, and responsive layout
- **Smart Text Processing**: Aggressive regex-based formatting for clean job descriptions and skills

### Technical Features
- **Vector Database**: Milvus integration for efficient job opportunity storage and retrieval
- **Semantic Search**: Advanced embedding-based job matching with cosine similarity
- **Modern UI**: React frontend with HRSD branding, responsive design, and professional styling
- **RESTful API**: FastAPI backend with comprehensive endpoints and Pydantic validation
- **Document Processing**: Robust text extraction and cleaning from various file formats
- **LLM Integration**: Groq API integration for intelligent analysis and career advice

## 🏗️ Architecture

### Frontend (React)
- **Components**: 
  - `FileUpload`: CV upload with drag-and-drop functionality
  - `JobMatches`: Job results display with enhanced formatting
  - `AIAssistant`: Interactive chat interface with persistent history
  - `App`: Main application with tabbed navigation and state management
- **Styling**: Tailwind CSS with HRSD color scheme and professional design
- **State Management**: React hooks with persistent chat state across tab switches
- **API Integration**: RESTful communication with backend using axios
- **Navigation**: Sticky header with perfectly centered toggle button

### Backend (FastAPI)
- **Services**: 
  - `MilvusService`: Vector database operations with LLM-based rescoring
  - `CVProcessor`: Document parsing and text extraction with advanced cleaning
  - `JobEmbedder`: Job opportunity management and embedding generation
  - `GroqService`: AI-powered career advice, analysis, and intelligent job scoring
- **Endpoints**: Health checks, CV upload, job matching, chat functionality with Pydantic validation
- **AI Integration**: Groq LLM for intelligent job rescoring and career advice

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

## ✨ Recent Improvements

### UI/UX Enhancements
- **Perfect Centering**: Toggle button in header is now perfectly centered using absolute positioning
- **Persistent State**: Chat history and conversation state persist when switching between tabs
- **Professional Design**: Enhanced spacing, indentation, and visual hierarchy throughout the application
- **Responsive Layout**: Improved mobile and desktop experience with proper padding and margins
- **Sticky Navigation**: Always-accessible toggle button that stays visible while scrolling

### AI & Matching Improvements
- **Intelligent Scoring**: LLM-based job match rescoring provides more logical and accurate results
- **Smart Text Processing**: Advanced regex-based formatting for clean job descriptions and skills display
- **Enhanced Chat**: Improved AI assistant with better context awareness and response quality
- **Better Formatting**: Skills are displayed as comma-separated strings for better readability

### Technical Improvements
- **State Management**: Moved chat state to parent component for better persistence
- **Code Organization**: Cleaner component structure and better separation of concerns
- **Performance**: Optimized rendering and state updates for smoother user experience
- **Error Handling**: Improved error handling and user feedback throughout the application

## 🎯 Usage

### For Job Seekers
1. **Upload CV**: Drag and drop or browse to upload your CV
2. **View Job Matches**: System analyzes your CV and displays matching job opportunities with intelligent scoring
3. **Switch to AI Assistant**: Click the toggle button in the header to access the AI career advisor
4. **Ask Questions**: Get personalized career advice, CV improvement tips, and job match explanations
5. **Switch Back**: Toggle between job matches and AI assistant - your conversation history persists
6. **Review Results**: View detailed job matches with compatibility scores, required skills, and descriptions

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

- **v2.0.0**: Major UI/UX and AI Enhancement Release
  - **Tabbed Interface**: Seamless switching between job matches and AI assistant
  - **Persistent Chat**: Conversation history persists across tab switches
  - **Sticky Navigation**: Always-accessible toggle button in header with perfect centering
  - **LLM-Based Scoring**: Intelligent job match rescoring for more accurate results
  - **Enhanced UI**: Professional design with proper spacing, indentation, and responsive layout
  - **Smart Text Processing**: Advanced regex-based formatting for clean job descriptions and skills
  - **Improved UX**: Better file upload, scroll-to-top, and overall user experience

- **v1.0.0**: Initial HRSD Job Matching System release
  - Complete CV processing and job matching
  - AI-powered career advice
  - HRSD-branded React frontend
  - FastAPI backend with Milvus integration

---

**Powered by Groq AI** 🤖