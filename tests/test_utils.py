"""
Utility tests and helper functions for the test suite.
"""
import pytest
from unittest.mock import Mock
import tempfile
import os


def create_mock_pdf_file(filename="test.pdf", content=b"fake pdf content"):
    """Create a mock PDF file for testing."""
    mock_file = Mock()
    mock_file.name = filename
    mock_file.type = "application/pdf"
    mock_file.size = len(content)
    mock_file.read.return_value = content
    mock_file.getvalue.return_value = content
    return mock_file


def create_sample_chunks(filename="test.pdf", num_chunks=3):
    """Create sample document chunks for testing."""
    return [
        {
            "text": f"This is chunk {i} of the document.",
            "chunk_index": i,
            "filename": filename
        }
        for i in range(num_chunks)
    ]


def create_sample_embeddings(num_embeddings=3, dim=384):
    """Create sample embeddings for testing."""
    return [
        [0.1 * (i + 1)] * dim
        for i in range(num_embeddings)
    ]


def assert_valid_chunk_structure(chunk):
    """Assert that a chunk has the required structure."""
    required_fields = ["text", "chunk_index", "filename"]
    for field in required_fields:
        assert field in chunk, f"Missing required field: {field}"
    
    assert isinstance(chunk["text"], str), "Text should be string"
    assert isinstance(chunk["chunk_index"], int), "Chunk index should be integer"
    assert isinstance(chunk["filename"], str), "Filename should be string"
    assert len(chunk["text"]) > 0, "Text should not be empty"
    assert chunk["chunk_index"] >= 0, "Chunk index should be non-negative"


def assert_valid_search_result(result):
    """Assert that a search result has the required structure."""
    required_fields = ["text", "filename"]
    for field in required_fields:
        assert field in result, f"Missing required field: {field}"
    
    assert isinstance(result["text"], str), "Text should be string"
    assert isinstance(result["filename"], str), "Filename should be string"
    assert len(result["text"]) > 0, "Text should not be empty"


class TestUtilityFunctions:
    """Test the utility functions themselves."""
    
    def test_create_mock_pdf_file(self):
        """Test mock PDF file creation."""
        mock_file = create_mock_pdf_file("test.pdf", b"content")
        
        assert mock_file.name == "test.pdf"
        assert mock_file.type == "application/pdf"
        assert mock_file.read() == b"content"
        assert mock_file.getvalue() == b"content"
        assert mock_file.size == len(b"content")
    
    def test_create_sample_chunks(self):
        """Test sample chunk creation."""
        chunks = create_sample_chunks("test.pdf", 3)
        
        assert len(chunks) == 3
        for i, chunk in enumerate(chunks):
            assert_valid_chunk_structure(chunk)
            assert chunk["chunk_index"] == i
            assert chunk["filename"] == "test.pdf"
    
    def test_create_sample_embeddings(self):
        """Test sample embedding creation."""
        embeddings = create_sample_embeddings(3, 384)
        
        assert len(embeddings) == 3
        for embedding in embeddings:
            assert len(embedding) == 384
            assert all(isinstance(x, float) for x in embedding)
    
    def test_assert_valid_chunk_structure_valid(self):
        """Test chunk structure validation with valid chunk."""
        valid_chunk = {
            "text": "Sample text",
            "chunk_index": 0,
            "filename": "test.pdf"
        }
        
        # Should not raise any assertion
        assert_valid_chunk_structure(valid_chunk)
    
    def test_assert_valid_chunk_structure_invalid(self):
        """Test chunk structure validation with invalid chunk."""
        invalid_chunk = {
            "text": "",  # Empty text
            "chunk_index": -1,  # Negative index
            "filename": "test.pdf"
        }
        
        with pytest.raises(AssertionError):
            assert_valid_chunk_structure(invalid_chunk)
    
    def test_assert_valid_search_result_valid(self):
        """Test search result validation with valid result."""
        valid_result = {
            "text": "Sample search result",
            "filename": "test.pdf"
        }
        
        # Should not raise any assertion
        assert_valid_search_result(valid_result)
    
    def test_assert_valid_search_result_invalid(self):
        """Test search result validation with invalid result."""
        invalid_result = {
            "text": "",  # Empty text
            "filename": "test.pdf"
        }
        
        with pytest.raises(AssertionError):
            assert_valid_search_result(invalid_result)


class TestEnvironmentHelpers:
    """Test environment setup helpers."""
    
    def test_temp_directory_creation(self, temp_dir):
        """Test temporary directory fixture."""
        assert os.path.exists(temp_dir)
        assert os.path.isdir(temp_dir)
        
        # Should be able to create files in it
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test content")
        
        assert os.path.exists(test_file)
    
    def test_environment_variables_set(self):
        """Test that test environment variables are set."""
        required_vars = [
            "GROQ_API_KEY",
            "MILVUS_HOST", 
            "MILVUS_TOKEN",
            "MILVUS_COLLECTION_PREFIX"
        ]
        
        for var in required_vars:
            assert os.getenv(var) is not None, f"Environment variable {var} not set"


class TestMockHelpers:
    """Test mock helper functions."""
    
    def test_mock_milvus_client_setup(self, mock_milvus_client):
        """Test that mock Milvus client is properly configured."""
        # Test collection operations
        assert mock_milvus_client.has_collection.return_value == True
        assert mock_milvus_client.list_collections.return_value == ["test_documents"]
        
        # Test data operations
        insert_result = mock_milvus_client.insert.return_value
        assert hasattr(insert_result, 'insert_count')
        
        query_result = mock_milvus_client.query.return_value
        assert isinstance(query_result, list)
        
        search_result = mock_milvus_client.search.return_value
        assert isinstance(search_result, list)
        assert len(search_result) > 0
        assert len(search_result[0]) > 0
    
    def test_mock_groq_client_setup(self, mock_groq_client):
        """Test that mock Groq client is properly configured."""
        # Should be async mock
        assert hasattr(mock_groq_client, 'chat')
        assert hasattr(mock_groq_client.chat, 'completions')
        assert hasattr(mock_groq_client.chat.completions, 'create')
        
        # Test response structure
        response = mock_groq_client.chat.completions.create.return_value
        assert hasattr(response, 'choices')
        assert len(response.choices) > 0
        assert hasattr(response.choices[0], 'message')
        assert hasattr(response.choices[0].message, 'content')
    
    def test_mock_sentence_transformer_setup(self, mock_sentence_transformer):
        """Test that mock sentence transformer is properly configured."""
        assert hasattr(mock_sentence_transformer, 'encode')
        
        # Test encoding
        result = mock_sentence_transformer.encode(["test"])
        # The mock returns numpy array, so check it has the right properties
        assert hasattr(result, 'shape') or isinstance(result, list)
        assert len(result) == 1  # Should return one embedding for one input
        
        # Test with multiple inputs
        result_multi = mock_sentence_transformer.encode(["test1", "test2"])
        assert len(result_multi) == 2  # Should return two embeddings for two inputs
    
    def test_sample_data_fixtures(self, sample_document_chunks, sample_embeddings, sample_chat_history):
        """Test that sample data fixtures are properly structured."""
        # Test document chunks
        assert isinstance(sample_document_chunks, list)
        assert len(sample_document_chunks) > 0
        for chunk in sample_document_chunks:
            assert_valid_chunk_structure(chunk)
        
        # Test embeddings
        assert isinstance(sample_embeddings, list)
        assert len(sample_embeddings) > 0
        for embedding in sample_embeddings:
            assert isinstance(embedding, list)
            assert len(embedding) > 0
        
        # Test chat history
        assert isinstance(sample_chat_history, list)
        assert len(sample_chat_history) > 0
        for message in sample_chat_history:
            assert "role" in message
            assert "content" in message
            assert message["role"] in ["user", "assistant"]


class TestDataValidation:
    """Test data validation utilities."""
    
    def test_embedding_validation(self):
        """Test embedding validation utility."""
        from tests.conftest import assert_valid_embedding
        
        # Valid embedding
        valid_embedding = [0.1] * 384
        assert_valid_embedding(valid_embedding)
        
        # Invalid dimension
        with pytest.raises(AssertionError):
            assert_valid_embedding([0.1] * 100)
        
        # Invalid type
        with pytest.raises(AssertionError):
            assert_valid_embedding("not a list")
    
    def test_document_chunk_validation(self):
        """Test document chunk validation utility."""
        from tests.conftest import assert_valid_document_chunk
        
        # Valid chunk
        valid_chunk = {
            "text": "Sample text",
            "chunk_index": 0,
            "filename": "test.pdf"
        }
        assert_valid_document_chunk(valid_chunk)
        
        # Missing field
        with pytest.raises(AssertionError):
            invalid_chunk = {"text": "Sample text", "chunk_index": 0}
            assert_valid_document_chunk(invalid_chunk)
    
    def test_search_result_validation(self):
        """Test search result validation utility."""
        from tests.conftest import assert_valid_search_result
        
        # Valid result
        valid_result = {
            "text": "Sample result",
            "filename": "test.pdf"
        }
        assert_valid_search_result(valid_result)
        
        # Missing field
        with pytest.raises(AssertionError):
            invalid_result = {"text": "Sample result"}
            assert_valid_search_result(invalid_result)


class TestPerformanceHelpers:
    """Test performance testing utilities."""
    
    def test_large_data_generation(self):
        """Test generation of large datasets for performance testing."""
        # Generate large chunk set
        large_chunks = create_sample_chunks("large_doc.pdf", 1000)
        
        assert len(large_chunks) == 1000
        for i, chunk in enumerate(large_chunks):
            assert chunk["chunk_index"] == i
            assert_valid_chunk_structure(chunk)
    
    def test_memory_efficient_operations(self):
        """Test that test utilities don't consume excessive memory."""
        # Generate moderately large dataset
        chunks = create_sample_chunks("test.pdf", 100)
        embeddings = create_sample_embeddings(100, 384)
        
        # Basic memory usage check (should complete without issues)
        assert len(chunks) == 100
        assert len(embeddings) == 100
        
        # Cleanup
        del chunks
        del embeddings 