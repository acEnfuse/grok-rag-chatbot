"""
Pytest configuration and shared fixtures for RAG Chatbot tests.
"""
import pytest
import os
import tempfile
import shutil
import asyncio
import numpy as np
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from typing import Dict, Any, List
from io import BytesIO

# Test environment variables
TEST_ENV_VARS = {
    "GROQ_API_KEY": "test_groq_api_key",
    "MILVUS_HOST": "localhost:19530",
    "MILVUS_TOKEN": "test_token",
    "MILVUS_COLLECTION_PREFIX": "test_"
}

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    original_env = {}
    for key, value in TEST_ENV_VARS.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value
    
    yield
    
    # Restore original environment
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_pdf_content():
    """Sample PDF content for testing."""
    return "This is a sample PDF document content for testing purposes."

@pytest.fixture
def sample_document_chunks():
    """Sample document chunks for testing."""
    return [
        {
            "text": "This is the first chunk of text from a document.",
            "chunk_index": 0,
            "filename": "test_document.pdf"
        },
        {
            "text": "This is the second chunk of text from the same document.",
            "chunk_index": 1,
            "filename": "test_document.pdf"
        },
        {
            "text": "This is the third and final chunk of the document.",
            "chunk_index": 2,
            "filename": "test_document.pdf"
        }
    ]

@pytest.fixture
def sample_embeddings():
    """Sample embeddings for testing."""
    return [
        [0.1, 0.2, 0.3, 0.4, 0.5] * 77,  # 384 dimensions
        [0.2, 0.3, 0.4, 0.5, 0.6] * 77,
        [0.3, 0.4, 0.5, 0.6, 0.7] * 77
    ]

@pytest.fixture
def mock_milvus_client():
    """Mock Milvus client for testing."""
    mock_client = Mock()
    
    # Mock collection operations
    mock_client.has_collection.return_value = True
    mock_client.create_collection.return_value = None
    mock_client.drop_collection.return_value = None
    mock_client.list_collections.return_value = ["test_documents"]
    
    # Mock data operations
    mock_client.insert.return_value = Mock(insert_count=3)
    mock_client.query.return_value = [
        {"filename": "test_doc.pdf", "chunk_index": 0},
        {"filename": "test_doc.pdf", "chunk_index": 1}
    ]
    mock_client.search.return_value = [
        [
            Mock(entity={"text": "Sample text", "filename": "test.pdf"}, distance=0.1),
            Mock(entity={"text": "Another text", "filename": "test.pdf"}, distance=0.2)
        ]
    ]
    mock_client.delete.return_value = Mock(delete_count=2)
    
    return mock_client

@pytest.fixture
def mock_groq_client():
    """Mock Groq client for testing."""
    mock_client = AsyncMock()
    
    # Mock chat completion response
    mock_response = Mock()
    mock_response.choices = [
        Mock(message=Mock(content="This is a test response from the AI assistant."))
    ]
    mock_client.chat.completions.create.return_value = mock_response
    
    return mock_client

@pytest.fixture
def mock_sentence_transformer():
    """Mock SentenceTransformer for testing."""
    mock_transformer = Mock()
    
    # Mock encode to return the correct number of embeddings based on input
    def mock_encode(texts):
        if isinstance(texts, str):
            texts = [texts]
        # Return one embedding per text
        return np.array([[0.1, 0.2, 0.3] * 128 for _ in texts])  # 384 dimensions each
    
    mock_transformer.encode.side_effect = mock_encode
    return mock_transformer

@pytest.fixture
def mock_tika_parser():
    """Mock Tika parser for testing."""
    with patch('tika.parser.from_buffer') as mock_parser:
        mock_parser.return_value = {
            'content': 'This is extracted text from a PDF document for testing.',
            'metadata': {'Content-Type': 'application/pdf'}
        }
        yield mock_parser

@pytest.fixture
def sample_uploaded_file():
    """Mock Streamlit uploaded file."""
    mock_file = Mock()
    mock_file.name = "test_document.pdf"
    mock_file.type = "application/pdf"
    mock_file.size = 1024
    mock_file.read.return_value = b"PDF content bytes"
    mock_file.getvalue.return_value = b"PDF content bytes"
    return mock_file

@pytest.fixture
def mock_streamlit():
    """Mock Streamlit components for testing"""
    # Create all the mocks first
    mock_patches = {
        'title': patch('streamlit.title'),
        'markdown': patch('streamlit.markdown'),
        'success': patch('streamlit.success'),
        'error': patch('streamlit.error'),
        'info': patch('streamlit.info'),
        'warning': patch('streamlit.warning'),
        'stop': patch('streamlit.stop'),
        'button': patch('streamlit.button'),
        'file_uploader': patch('streamlit.file_uploader'),
        'text_input': patch('streamlit.text_input'),
        'selectbox': patch('streamlit.selectbox'),
        'slider': patch('streamlit.slider'),
        'checkbox': patch('streamlit.checkbox'),
        'radio': patch('streamlit.radio'),
        'multiselect': patch('streamlit.multiselect'),
        'write': patch('streamlit.write'),
        'json': patch('streamlit.json'),
        'code': patch('streamlit.code'),
        'image': patch('streamlit.image'),
        'spinner': patch('streamlit.spinner'),
        'rerun': patch('streamlit.rerun'),
        'columns': patch('streamlit.columns'),
        'expander': patch('streamlit.expander'),
        'header': patch('streamlit.header'),
        'subheader': patch('streamlit.subheader'),
        'divider': patch('streamlit.divider'),
        'chat_message': patch('streamlit.chat_message'),
        'chat_input': patch('streamlit.chat_input'),
        'session_state': patch('streamlit.session_state', new_callable=lambda: MagicMock()),
        'cache_resource': patch('streamlit.cache_resource'),
        'sidebar': patch('streamlit.sidebar')
    }
    
    # Start all patches
    mocks = {}
    for name, patcher in mock_patches.items():
        mocks[name] = patcher.start()
    
    try:
        # Configure sidebar as a proper context manager
        sidebar_context = MagicMock()
        sidebar_context.__enter__ = Mock(return_value=sidebar_context)
        sidebar_context.__exit__ = Mock(return_value=None)
        mocks['sidebar'].return_value = sidebar_context
        
        # Configure spinner as a proper context manager
        spinner_context = MagicMock()
        spinner_context.__enter__ = Mock(return_value=spinner_context)
        spinner_context.__exit__ = Mock(return_value=None)
        mocks['spinner'].return_value = spinner_context
        
        # Configure expander as a proper context manager
        expander_context = MagicMock()
        expander_context.__enter__ = Mock(return_value=expander_context)
        expander_context.__exit__ = Mock(return_value=None)
        mocks['expander'].return_value = expander_context
        
        # Configure chat_message as a proper context manager
        chat_message_context = MagicMock()
        chat_message_context.__enter__ = Mock(return_value=chat_message_context)
        chat_message_context.__exit__ = Mock(return_value=None)
        mocks['chat_message'].return_value = chat_message_context
        
        # Configure columns to return mock column objects
        mock_col1 = MagicMock()
        mock_col2 = MagicMock()
        mock_col1.__enter__ = Mock(return_value=mock_col1)
        mock_col1.__exit__ = Mock(return_value=None)
        mock_col2.__enter__ = Mock(return_value=mock_col2)
        mock_col2.__exit__ = Mock(return_value=None)
        mocks['columns'].return_value = [mock_col1, mock_col2]
        
        # Configure session state with default values
        mocks['session_state'].messages = []
        mocks['session_state'].documents = []
        
        # Configure cache_resource decorator to just return the function
        mocks['cache_resource'].side_effect = lambda func: func
        
        # Default return values
        mocks['button'].return_value = False
        mocks['file_uploader'].return_value = None
        mocks['text_input'].return_value = ""
        mocks['chat_input'].return_value = None
        mocks['checkbox'].return_value = False
        
        yield mocks
        
    finally:
        # Stop all patches
        for patcher in mock_patches.values():
            patcher.stop()

@pytest.fixture
def sample_chat_history():
    """Sample chat history for testing."""
    return [
        {"role": "user", "content": "What is BattleTech?"},
        {"role": "assistant", "content": "BattleTech is a tabletop strategy game..."},
        {"role": "user", "content": "Tell me about mechs"},
        {"role": "assistant", "content": "Mechs are giant robotic vehicles..."}
    ]

@pytest.fixture
def sample_search_results():
    """Sample search results from Milvus."""
    return [
        {
            "text": "BattleTech is a tabletop strategy board game and miniature wargame.",
            "filename": "battletech_rules.pdf",
            "chunk_index": 0
        },
        {
            "text": "Mechs are the primary units in BattleTech combat.",
            "filename": "battletech_rules.pdf", 
            "chunk_index": 1
        }
    ]

# Async test utilities
@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# Test data validation helpers
def assert_valid_embedding(embedding: List[float], expected_dim: int = 384):
    """Assert that an embedding is valid."""
    assert isinstance(embedding, list)
    assert len(embedding) == expected_dim
    assert all(isinstance(x, (int, float)) for x in embedding)

def assert_valid_document_chunk(chunk: Dict[str, Any]):
    """Assert that a document chunk has the required structure."""
    required_fields = ["text", "chunk_index", "filename"]
    for field in required_fields:
        assert field in chunk
    assert isinstance(chunk["text"], str)
    assert isinstance(chunk["chunk_index"], int)
    assert isinstance(chunk["filename"], str)
    assert len(chunk["text"]) > 0

def assert_valid_search_result(result: Dict[str, Any]):
    """Assert that a search result has the required structure."""
    required_fields = ["text", "filename"]
    for field in required_fields:
        assert field in result
    assert isinstance(result["text"], str)
    assert isinstance(result["filename"], str) 