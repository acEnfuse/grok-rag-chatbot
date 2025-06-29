import streamlit as st
import os
import asyncio
from dotenv import load_dotenv
import logging
from typing import List, Dict

from backend.services.milvus_service import MilvusService
from backend.services.groq_service import GroqService
from backend.services.document_processor import DocumentProcessor

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services
@st.cache_resource
def init_services():
    """Initialize services with caching"""
    milvus_service = MilvusService()
    groq_service = GroqService()
    document_processor = DocumentProcessor()
    
    # Initialize Milvus connection (fast now!)
    asyncio.run(milvus_service.initialize())
    
    return milvus_service, groq_service, document_processor

# Initialize session state
def init_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "documents" not in st.session_state:
        st.session_state.documents = []

async def process_uploaded_file(file, document_processor, milvus_service):
    """Process and store uploaded file"""
    try:
        # Save uploaded file temporarily
        temp_path = f"temp_{file.name}"
        with open(temp_path, "wb") as f:
            f.write(file.getvalue())
        
        # Process document
        with st.spinner(f"Processing {file.name}..."):
            chunks = await document_processor.process_document(temp_path, file.name)
            
            # Store in Milvus (embedding model loads here if first time)
            with st.spinner("🧠 Loading AI model (first time only)..."):
                result = await milvus_service.add_documents(chunks)
            
            # Clean up temp file
            os.remove(temp_path)
            
            return len(chunks), result
    
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e

async def get_chat_response(message, milvus_service, groq_service):
    """Get response from the RAG system"""
    try:
        # Search for relevant documents (embedding model loads here if first time)
        with st.spinner("🔍 Searching knowledge base..."):
            relevant_docs = await milvus_service.search_documents(message)
        
        # Generate response using Groq
        with st.spinner("🤖 Generating response..."):
            response = await groq_service.generate_response(
                query=message,
                context_docs=relevant_docs,
                chat_history=st.session_state.messages[-10:]  # Last 10 messages for context
            )
        
        return response, relevant_docs
    
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        return f"Sorry, I encountered an error: {str(e)}", []

def load_documents_safely(milvus_service):
    """Safely load documents with error handling"""
    try:
        documents = asyncio.run(milvus_service.list_documents())
        logger.info(f"Loaded {len(documents)} documents")
        return documents
    except Exception as e:
        logger.error(f"Failed to load documents: {e}")
        return []

def main():
    st.title("🤖 RAG Chatbot")
    st.markdown("Upload documents and chat with your knowledge base!")
    
    # Initialize session state
    init_session_state()
    
    # Initialize services
    try:
        milvus_service, groq_service, document_processor = init_services()
        st.success("🚀 Services initialized successfully!")
    except Exception as e:
        st.error(f"Failed to initialize services: {e}")
        st.stop()
    
    # ALWAYS load documents on every run - this ensures they show up
    st.session_state.documents = load_documents_safely(milvus_service)
    
    # Sidebar for document management
    with st.sidebar:
        st.header("📄 Document Management")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload a document",
            type=['pdf', 'txt', 'docx', 'doc', 'rtf'],
            help="Supported formats: PDF, TXT, DOCX, DOC, RTF"
        )
        
        if uploaded_file is not None:
            if st.button("Process Document"):
                try:
                    chunks_count, result = asyncio.run(
                        process_uploaded_file(uploaded_file, document_processor, milvus_service)
                    )
                    st.success(f"✅ Successfully processed {uploaded_file.name}")
                    st.info(f"Added {chunks_count} chunks to the knowledge base")
                    
                    # Refresh document list
                    st.session_state.documents = load_documents_safely(milvus_service)
                    
                except Exception as e:
                    st.error(f"❌ Error processing document: {str(e)}")

        # Document Management Section
        with st.expander("📄 Your Documents", expanded=True):
            
            # Manual refresh button
            if st.button("🔄 Refresh Document List"):
                st.session_state.documents = load_documents_safely(milvus_service)
                if st.session_state.documents:
                    st.success(f"✅ Found {len(st.session_state.documents)} document(s)")
                else:
                    st.info("📝 No documents found in collection")
                st.rerun()
            
            # List documents with delete option
            if hasattr(st.session_state, 'documents') and st.session_state.documents:
                for doc in st.session_state.documents:
                    col_doc, col_del = st.columns([5, 1])
                    with col_doc:
                        st.write(f"📄 **{doc['filename']}**")
                    with col_del:
                        # Check if this document is in "delete confirmation" mode
                        delete_key = f"delete_confirm_{doc['filename']}"
                        if delete_key in st.session_state and st.session_state[delete_key]:
                            # Show confirmation buttons
                            col_confirm, col_cancel = st.columns(2)
                            with col_confirm:
                                if st.button("✅", key=f"confirm_{doc['filename']}", help="Confirm delete"):
                                    try:
                                        asyncio.run(milvus_service.delete_document(doc['filename']))
                                        st.success(f"✅ Deleted {doc['filename']}")
                                        # Clear confirmation state and refresh
                                        if delete_key in st.session_state:
                                            del st.session_state[delete_key]
                                        st.session_state.documents = asyncio.run(milvus_service.list_documents())
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Error: {str(e)}")
                                        if delete_key in st.session_state:
                                            del st.session_state[delete_key]
                            with col_cancel:
                                if st.button("❌", key=f"cancel_{doc['filename']}", help="Cancel delete"):
                                    # Clear confirmation state
                                    if delete_key in st.session_state:
                                        del st.session_state[delete_key]
                                    st.rerun()
                        else:
                            # Show delete button
                            if st.button("🗑️", key=f"del_{doc['filename']}", help=f"Delete {doc['filename']}"):
                                # Set confirmation state
                                st.session_state[delete_key] = True
                                st.rerun()
            else:
                st.info("📝 No documents uploaded yet. Upload a document above to get started!")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
    
    # Main chat interface
    st.header("💬 Chat")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display sources for assistant messages
            if message["role"] == "assistant" and "sources" in message:
                if message["sources"]:
                    with st.expander("📖 Sources", expanded=False):
                        for i, source in enumerate(message["sources"]):
                            st.markdown(f"**{source['filename']}** (Score: {source['score']:.3f})")
                            st.markdown(f"_{source['content']}_")
                            if i < len(message["sources"]) - 1:
                                st.divider()
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            try:
                response, sources = asyncio.run(
                    get_chat_response(prompt, milvus_service, groq_service)
                )
                
                st.markdown(response)
                
                # Display sources
                if sources:
                    with st.expander("📖 Sources", expanded=False):
                        for i, source in enumerate(sources):
                            st.markdown(f"**{source['filename']}** (Score: {source['score']:.3f})")
                            st.markdown(f"_{source['text'][:300]}..._")
                            if i < len(sources) - 1:
                                st.divider()
                
                # Add assistant message to chat history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response,
                    "sources": [
                        {
                            "filename": s["filename"],
                            "content": s["text"][:200] + "...",
                            "score": s["score"]
                        } for s in sources
                    ]
                })
            
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

if __name__ == "__main__":
    main() 