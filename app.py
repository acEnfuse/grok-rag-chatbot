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

# Custom CSS for Groq Cloud styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons');
    
    /* Dark theme base */
    .stApp {
        background-color: #0f0f0f !important;
        color: #ffffff !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Replace the sidebar collapse button icon with a working one */
    [data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"] {
        font-family: 'Material Icons' !important;
        font-size: 24px !important;
        width: 24px !important;
        height: 24px !important;
    }
    
    /* Replace the problematic icon text with a better symbol */
    [data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"]:before {
        content: "chevron_left" !important;
        font-family: 'Material Icons' !important;
        font-size: 24px !important;
        color: rgba(250, 250, 250, 0.6) !important;
    }
    
    /* Hide the fallback text */
    [data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"] {
        font-size: 0 !important;
        color: transparent !important;
        text-indent: -9999px !important;
    }
    
    /* Ensure the icon displays properly */
    [data-testid="stSidebarCollapseButton"] {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* Main content area */
    .main .block-container {
        background-color: #0f0f0f !important;
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-1cypcdb {
        background-color: #1a1a1a !important;
        border-right: 1px solid #333333 !important;
        width: 350px !important;
        min-width: 350px !important;
        max-width: 350px !important;
        overflow: visible !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
    }
    
    h1 {
        font-size: 2rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        color: #e5e5e5 !important;
    }
    
    /* Text styling */
    .stMarkdown, .stText, p, span, div {
        font-family: 'Inter', sans-serif !important;
        color: #e5e5e5 !important;
        font-size: 14px !important;
        line-height: 1.5 !important;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #262626 !important;
        border: 1px solid #404040 !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
        padding: 12px 16px !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #f55036 !important;
        box-shadow: 0 0 0 2px rgba(245, 80, 54, 0.2) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #f55036 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        padding: 8px 16px !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background-color: #e04832 !important;
        transform: translateY(-1px) !important;
    }
    
    /* Secondary buttons */
    .stButton > button[kind="secondary"] {
        background-color: transparent !important;
        border: 1px solid #404040 !important;
        color: #e5e5e5 !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background-color: #262626 !important;
        border-color: #666666 !important;
    }
    
    /* Remove column styling since we're now using vertical stacking */
    .stButton {
        width: 100% !important;
        margin: 1px 0 !important;
    }
    
    .stButton > button {
        width: 100% !important;
        margin: 1px 0 !important;
        font-size: 14px !important;
        padding: 8px 16px !important;
    }
    
    /* Specific styling for confirm buttons (green) */
    button[title*="Confirm"], 
    button[aria-label*="Confirm"] {
        background-color: #22c55e !important;
        color: #ffffff !important;
        border: none !important;
    }
    
    button[title*="Confirm"]:hover, 
    button[aria-label*="Confirm"]:hover {
        background-color: #16a34a !important;
    }
    
    /* Specific styling for cancel buttons (gray) */
    button[title*="Cancel"], 
    button[aria-label*="Cancel"] {
        background-color: transparent !important;
        border: 1px solid #666666 !important;
        color: #e5e5e5 !important;
    }
    
    button[title*="Cancel"]:hover, 
    button[aria-label*="Cancel"]:hover {
        background-color: #374151 !important;
        border-color: #9ca3af !important;
    }
    
    /* File uploader */
    .stFileUploader {
        background-color: #1a1a1a !important;
        border: 2px dashed #404040 !important;
        border-radius: 8px !important;
        padding: 2rem !important;
    }
    
    .stFileUploader label {
        color: #e5e5e5 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1a1a1a !important;
        border: 1px solid #333333 !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        padding: 12px 16px !important;
    }
    
    .streamlit-expanderContent {
        background-color: #1a1a1a !important;
        border: 1px solid #333333 !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
        padding: 16px !important;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: #1a1a1a !important;
        border: 1px solid #333333 !important;
        border-radius: 12px !important;
        margin-bottom: 1rem !important;
        padding: 16px !important;
    }
    
    .stChatMessage .stMarkdown {
        color: #e5e5e5 !important;
    }
    
    /* Success/Error/Info messages */
    .stSuccess {
        background-color: rgba(34, 197, 94, 0.1) !important;
        border: 1px solid #22c55e !important;
        color: #22c55e !important;
    }
    
    .stError {
        background-color: rgba(239, 68, 68, 0.1) !important;
        border: 1px solid #ef4444 !important;
        color: #ef4444 !important;
    }
    
    .stInfo {
        background-color: rgba(59, 130, 246, 0.1) !important;
        border: 1px solid #3b82f6 !important;
        color: #3b82f6 !important;
    }
    
    /* Dividers */
    hr {
        border: none !important;
        height: 1px !important;
        background-color: #333333 !important;
        margin: 2rem 0 !important;
    }
    
    /* Sidebar content */
    .css-1d391kg .stMarkdown,
    .css-1cypcdb .stMarkdown {
        color: #e5e5e5 !important;
        width: 100% !important;
        overflow: visible !important;
        text-overflow: clip !important;
        white-space: normal !important;
    }
    
    /* Code blocks */
    .stCode {
        background-color: #262626 !important;
        border: 1px solid #404040 !important;
        border-radius: 8px !important;
        color: #e5e5e5 !important;
        font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background-color: #262626 !important;
        border: 1px solid #404040 !important;
        border-radius: 8px !important;
        color: #ffffff !important;
    }
    
    /* Progress bars */
    .stProgress .st-bo {
        background-color: #f55036 !important;
    }
    
    /* Metric cards */
    .metric-container {
        background-color: #1a1a1a !important;
        border: 1px solid #333333 !important;
        border-radius: 8px !important;
        padding: 16px !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Fix the stLogoSpacer that might be causing text cutoff */
    [data-testid="stLogoSpacer"] {
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        display: none !important;
    }
    
    /* Additional Streamlit spacing fixes */
    .st-emotion-cache-11ukie {
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        display: none !important;
    }
    
    /* Target and hide Material Design icon fallback text specifically */
    /* Hide elements with keyboard arrow attributes */
    [title*="keyboard_double_arrow"],
    [aria-label*="keyboard_double_arrow"],
    [data-icon*="keyboard_double_arrow"],
    [class*="keyboard_double_arrow"] {
        font-size: 0 !important;
        color: transparent !important;
        text-indent: -9999px !important;
        width: 0 !important;
        height: 0 !important;
        overflow: hidden !important;
    }
    
    /* Hide any span/div that might contain the fallback text */
    span[style*="font-family"][style*="material"] {
        text-indent: -9999px !important;
        color: transparent !important;
    }
    
    /* Ensure sidebar content doesn't get cut off */
    .css-1d391kg .stMarkdown,
    .css-1cypcdb .stMarkdown {
        width: 100% !important;
        overflow: visible !important;
        word-wrap: break-word !important;
        padding-left: 0 !important;
        margin-left: 0 !important;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1a1a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #404040;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #666666;
    }

    /* Replace the sidebar collapse button with a simple CSS arrow */
    [data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"] {
        font-size: 0 !important;
        color: transparent !important;
        text-indent: -9999px !important;
        position: relative !important;
        width: 24px !important;
        height: 24px !important;
    }
    
    [data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"]:before {
        content: "‹" !important;
        font-size: 20px !important;
        color: rgba(250, 250, 250, 0.6) !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

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
            with st.spinner("Loading AI model (first time only)..."):
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
        with st.spinner("Searching knowledge base..."):
            relevant_docs = await milvus_service.search_documents(message)
        
        # Generate response using Groq
        with st.spinner("Generating response..."):
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
    st.title("RAG Chatbot")
    st.markdown("Upload documents and chat with your knowledge base!")
    
    # Initialize session state
    init_session_state()
    
    # Initialize services
    try:
        milvus_service, groq_service, document_processor = init_services()
        st.success("Services initialized successfully!")
    except Exception as e:
        st.error(f"Failed to initialize services: {e}")
        st.stop()
    
    # ALWAYS load documents on every run - this ensures they show up
    st.session_state.documents = load_documents_safely(milvus_service)
    
    # Sidebar for document management
    with st.sidebar:
        st.header("Document Management")
        
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
                    st.success(f"Successfully processed {uploaded_file.name}")
                    st.info(f"Added {chunks_count} chunks to the knowledge base")
                    
                    # Refresh document list
                    st.session_state.documents = load_documents_safely(milvus_service)
                    
                except Exception as e:
                    st.error(f"❌ Error processing document: {str(e)}")

        # Document Management Section
        with st.expander("Your Documents", expanded=False):
            
            # Manual refresh button
            if st.button("Refresh Document List"):
                st.session_state.documents = load_documents_safely(milvus_service)
                if st.session_state.documents:
                    st.success(f"Found {len(st.session_state.documents)} document(s)")
                else:
                    st.info("No documents found in collection")
                st.rerun()
            
            # List documents with delete option
            if hasattr(st.session_state, 'documents') and st.session_state.documents:
                for doc in st.session_state.documents:
                    col_doc, col_del = st.columns([5, 1])
                    with col_doc:
                        st.write(f"**{doc['filename']}**")
                    with col_del:
                        # Check if this document is in "delete confirmation" mode
                        delete_key = f"delete_confirm_{doc['filename']}"
                        if delete_key in st.session_state and st.session_state[delete_key]:
                            # Show confirmation buttons - stacked vertically (Cancel on top, Confirm below)
                            if st.button("Cancel", key=f"cancel_{doc['filename']}", help="Cancel delete"):
                                # Clear confirmation state
                                if delete_key in st.session_state:
                                    del st.session_state[delete_key]
                                st.rerun()
                            if st.button("Confirm", key=f"confirm_{doc['filename']}", help="Confirm delete"):
                                try:
                                    asyncio.run(milvus_service.delete_document(doc['filename']))
                                    st.success(f"Deleted {doc['filename']}")
                                    # Clear confirmation state and refresh
                                    if delete_key in st.session_state:
                                        del st.session_state[delete_key]
                                    st.session_state.documents = asyncio.run(milvus_service.list_documents())
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                                    if delete_key in st.session_state:
                                        del st.session_state[delete_key]
                        else:
                            # Show delete button
                            if st.button("Delete", key=f"del_{doc['filename']}", help=f"Delete {doc['filename']}"):
                                # Set confirmation state
                                st.session_state[delete_key] = True
                                st.rerun()
            else:
                st.info("No documents uploaded yet. Upload a document above to get started!")
        
        # Clear chat button
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
        
        # Powered by Groq footer
        st.markdown("---")
        st.markdown("**Powered by**")
        st.image("assets/Groq_logo.svg", width=120)
    
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display sources for assistant messages
            if message["role"] == "assistant" and "sources" in message:
                if message["sources"]:
                    with st.expander("Sources", expanded=False):
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
                    with st.expander("Sources", expanded=False):
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