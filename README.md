# RAG Chatbot with Milvus and Groq

A Retrieval-Augmented Generation (RAG) chatbot built with Streamlit that allows you to upload documents and chat with your knowledge base using Milvus vector database and Groq LLM inference.

## Features

- 📄 **Document Upload**: Support for PDF, TXT, DOCX, DOC, and RTF files
- 🔍 **Semantic Search**: Find relevant information using vector similarity
- 💬 **Interactive Chat**: Chat interface with conversation history
- 📚 **Document Management**: View, manage, and delete uploaded documents
- 🚀 **Fast Inference**: Powered by Groq's high-speed LLM API
- 🎯 **Source Citations**: See which documents were used to answer your questions

## Prerequisites

- Python 3.8+
- Milvus cluster (provided credentials in `.env`)
- Groq API key (provided in `.env`)
- Java 8+ (required for Apache Tika)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd rag_chatbot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment setup**:
   - Copy `.env.example` to `.env` (already done with your credentials)
   - The environment file includes your Milvus cluster and Groq API configurations

4. **Install Java** (required for Tika):
   - **macOS**: `brew install openjdk@11`
   - **Ubuntu**: `sudo apt-get install openjdk-11-jdk`
   - **Windows**: Download from Oracle or use OpenJDK

## Usage

1. **Start the application**:
   ```bash
   streamlit run app.py
   ```

2. **Access the app**:
   - Open your browser to `http://localhost:8501`

3. **Upload documents**:
   - Use the sidebar to upload PDF, DOCX, TXT, or other supported files
   - Click "Process Document" to parse and store in the vector database

4. **Chat with your documents**:
   - Type questions in the chat input
   - The system will find relevant document chunks and generate answers
   - View source citations in the expandable "Sources" section

## Project Structure

```
rag_chatbot/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (your credentials)
├── .env.example                   # Environment template
├── README.md                      # This file
└── backend/
    ├── __init__.py
    └── services/
        ├── __init__.py
        ├── milvus_service.py      # Vector database operations
        ├── groq_service.py        # LLM inference
        └── document_processor.py  # Document parsing and chunking
```

## Configuration

### Environment Variables

- `GROQ_API_KEY`: Your Groq API key for LLM inference
- `MILVUS_HOST`: Milvus cluster IP address
- `MILVUS_PORT`: Milvus port (default: 19530)
- `MILVUS_TOKEN`: Authentication token for Milvus
- `COLLECTION_NAME`: Name of the vector collection
- `EMBEDDING_MODEL`: Sentence transformer model name

### Customization

You can customize various parameters in the code:

- **Chunk size**: Modify `chunk_size` in `DocumentProcessor`
- **Embedding model**: Change `EMBEDDING_MODEL` in `.env`
- **LLM model**: Update `self.model` in `GroqService`
- **Search results**: Adjust `top_k` parameter in search functions

## Supported File Types

- **PDF**: `.pdf`
- **Microsoft Word**: `.docx`, `.doc`
- **Rich Text**: `.rtf`
- **Plain Text**: `.txt`

## Troubleshooting

### Common Issues

1. **Java not found**: Install Java 8+ for Tika document processing
2. **Milvus connection**: Ensure your Milvus cluster is accessible
3. **Groq API errors**: Check your API key and rate limits
4. **Memory issues**: Reduce chunk size for large documents

### Logs

The application logs important events and errors. Check the console output for debugging information.

## Architecture

1. **Document Processing**: Apache Tika extracts text from uploaded files
2. **Text Chunking**: Documents are split into overlapping chunks for better retrieval
3. **Embedding Generation**: Sentence transformers create vector embeddings
4. **Vector Storage**: Milvus stores embeddings with metadata
5. **Retrieval**: Semantic search finds relevant document chunks
6. **Generation**: Groq LLM generates responses using retrieved context

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 