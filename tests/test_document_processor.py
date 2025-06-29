"""
Unit tests for DocumentProcessor class.
"""
import pytest
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock
from backend.services.document_processor import DocumentProcessor


class TestDocumentProcessor:
    """Test suite for DocumentProcessor class."""
    
    @pytest.fixture
    def processor(self):
        """Create a DocumentProcessor instance for testing."""
        return DocumentProcessor()
    
    def test_init(self, processor):
        """Test DocumentProcessor initialization."""
        assert processor.chunk_size == 1000
        assert processor.chunk_overlap == 200
    
    @pytest.mark.asyncio
    async def test_process_document_success(self, processor):
        """Test successful document processing."""
        # Create a temporary PDF file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(b"Mock PDF content")
            temp_file_path = temp_file.name
        
        try:
            # Mock the Tika parser
            with patch('backend.services.document_processor.parser') as mock_parser:
                mock_parser.from_file.return_value = {
                    "content": "This is a test document with enough content to create multiple chunks. " * 20
                }
                
                filename = "test_document.pdf"
                chunks = await processor.process_document(temp_file_path, filename)
                
                assert len(chunks) > 0
                for chunk in chunks:
                    assert "text" in chunk
                    assert "filename" in chunk
                    assert "chunk_index" in chunk
                    assert chunk["filename"] == filename
                    assert len(chunk["text"]) > 50  # Minimum chunk size
                
                # Verify Tika was called
                mock_parser.from_file.assert_called_once_with(temp_file_path)
        finally:
            # Clean up
            os.unlink(temp_file_path)
    
    @pytest.mark.asyncio
    async def test_process_document_empty_content(self, processor):
        """Test processing document with empty content."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        try:
            with patch('backend.services.document_processor.parser') as mock_parser:
                mock_parser.from_file.return_value = {"content": ""}
                
                with pytest.raises(ValueError) as exc_info:
                    await processor.process_document(temp_file_path, "empty.pdf")
                
                assert "No text content extracted" in str(exc_info.value)
        finally:
            os.unlink(temp_file_path)
    
    @pytest.mark.asyncio
    async def test_process_document_extraction_failure(self, processor):
        """Test processing document when extraction fails."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        try:
            with patch('backend.services.document_processor.parser') as mock_parser:
                mock_parser.from_file.side_effect = Exception("Tika parsing failed")
                
                with pytest.raises(Exception) as exc_info:
                    await processor.process_document(temp_file_path, "test.pdf")
                
                assert "Tika parsing failed" in str(exc_info.value)
        finally:
            os.unlink(temp_file_path)
    
    def test_chunk_text_basic(self, processor):
        """Test basic text chunking functionality."""
        text = "This is a test document. " * 100  # Long enough for multiple chunks
        filename = "test.pdf"
        
        chunks = processor._chunk_text(text, filename)
        
        assert len(chunks) > 0
        for chunk in chunks:
            assert "text" in chunk
            assert "filename" in chunk
            assert "chunk_index" in chunk
            assert chunk["filename"] == filename
            assert len(chunk["text"]) > 50  # Minimum chunk size
    
    def test_chunk_text_empty(self, processor):
        """Test chunking empty text."""
        chunks = processor._chunk_text("", "test.pdf")
        assert chunks == []
    
    def test_chunk_text_short(self, processor):
        """Test chunking very short text"""
        text = "Short text"
        chunks = processor._chunk_text(text, "test.pdf")
        assert chunks == []  # Too short to meet minimum chunk size
    
    def test_chunk_text_preserves_words(self, processor):
        """Test that chunking preserves word boundaries."""
        text = "word1 word2 word3 " * 200  # Create text with clear word boundaries
        chunks = processor._chunk_text(text, "test.pdf")
        
        assert len(chunks) > 1  # Should create multiple chunks
        
        # Check that chunks don't break words
        for chunk in chunks:
            chunk_text = chunk["text"]
            # Should start and end with complete words (no partial words)
            assert not chunk_text.startswith(" ")
            assert not chunk_text.endswith(" ") or chunk_text.strip() == chunk_text
    
    def test_chunk_size_configuration(self, processor):
        """Test chunk size configuration"""
        custom_chunk_size = 500
        custom_overlap = 100
        
        processor.set_chunk_parameters(custom_chunk_size, custom_overlap)
        
        assert processor.chunk_size == custom_chunk_size
        assert processor.chunk_overlap == custom_overlap
    
    def test_chunk_text_with_custom_size(self, processor):
        """Test chunking with custom chunk size."""
        processor.set_chunk_parameters(chunk_size=500, chunk_overlap=50)  # Larger size to ensure chunks are created
        
        text = "word " * 200  # Create longer text
        chunks = processor._chunk_text(text, "test.pdf")
        
        # With custom chunk size, should create chunks
        assert len(chunks) > 0
        for chunk in chunks:
            # Chunks should respect minimum size requirement
            assert len(chunk["text"]) > 50
    
    def test_chunk_overlap_functionality(self, processor):
        """Test that chunk overlap works correctly."""
        processor.set_chunk_parameters(chunk_size=100, chunk_overlap=20)
        
        text = "unique_word_" + "common_word " * 50  # Create text with identifiable words
        chunks = processor._chunk_text(text, "test.pdf")
        
        if len(chunks) > 1:
            # Check that there's some overlap between consecutive chunks
            # This is approximate since we work with word boundaries
            first_chunk_words = chunks[0]["text"].split()
            second_chunk_words = chunks[1]["text"].split()
            
            # There should be some common words due to overlap
            common_words = set(first_chunk_words[-5:]) & set(second_chunk_words[:5])
            assert len(common_words) > 0  # Some overlap should exist
    
    @pytest.mark.asyncio
    async def test_logging_on_success(self, processor):
        """Test that successful processing logs appropriately."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        try:
            with patch('backend.services.document_processor.parser') as mock_parser, \
                 patch('backend.services.document_processor.logger') as mock_logger:
                
                mock_parser.from_file.return_value = {
                    "content": "This is test content. " * 50
                }
                
                filename = "test.pdf"
                chunks = await processor.process_document(temp_file_path, filename)
                
                # Verify logging occurred
                mock_logger.info.assert_called()
                log_call = mock_logger.info.call_args[0][0]
                assert filename in log_call
                assert f"{len(chunks)} chunks" in log_call
        finally:
            os.unlink(temp_file_path)
    
    def test_chunk_index_sequence(self, processor):
        """Test that chunk indices are sequential."""
        text = "word " * 200  # Create text for multiple chunks
        chunks = processor._chunk_text(text, "test.pdf")
        
        if len(chunks) > 1:
            for i, chunk in enumerate(chunks):
                assert chunk["chunk_index"] == i
    
    def test_filename_preservation(self, processor):
        """Test that filename is preserved in all chunks."""
        text = "word " * 200
        filename = "special_document.pdf"
        chunks = processor._chunk_text(text, filename)
        
        for chunk in chunks:
            assert chunk["filename"] == filename
    
    def test_chunk_text_unicode_handling(self, processor):
        """Test chunking text with unicode characters."""
        text = "Unicode test: café, naïve, résumé. " * 50
        chunks = processor._chunk_text(text, "unicode_test.pdf")
        
        assert len(chunks) > 0
        for chunk in chunks:
            # Verify unicode characters are preserved
            chunk_text = chunk["text"]
            assert "café" in chunk_text or "naïve" in chunk_text or "résumé" in chunk_text
    
    def test_very_long_document(self, processor):
        """Test processing very long documents."""
        # Create a very long text
        long_text = "This is sentence number {}. ".format("test") * 1000
        
        chunks = processor._chunk_text(long_text, "long_document.pdf")
        
        assert len(chunks) > 5  # Should create many chunks
        
        # Verify all chunks meet minimum size requirement
        for chunk in chunks:
            assert len(chunk["text"]) > 50
    
    def test_clean_text_functionality(self, processor):
        """Test the text cleaning functionality."""
        dirty_text = "This   has    excessive     whitespace\n\n\nand\t\ttabs."
        clean_text = processor._clean_text(dirty_text)
        
        # Should normalize whitespace
        assert "   " not in clean_text
        assert "\n" not in clean_text
        assert "\t" not in clean_text
        assert clean_text == "This has excessive whitespace and tabs."
    
    def test_clean_text_empty(self, processor):
        """Test cleaning empty text."""
        assert processor._clean_text("") == ""
        assert processor._clean_text(None) == ""
    
    @pytest.mark.asyncio
    async def test_extract_text_success(self, processor):
        """Test successful text extraction."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        try:
            with patch('backend.services.document_processor.parser') as mock_parser:
                expected_text = "This is extracted text from the document."
                mock_parser.from_file.return_value = {"content": expected_text}
                
                result = await processor._extract_text(temp_file_path)
                
                # Should return cleaned text
                assert result == expected_text
                mock_parser.from_file.assert_called_once_with(temp_file_path)
        finally:
            os.unlink(temp_file_path)
    
    @pytest.mark.asyncio
    async def test_extract_text_no_content(self, processor):
        """Test extraction when no content is found."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        try:
            with patch('backend.services.document_processor.parser') as mock_parser:
                mock_parser.from_file.return_value = {"content": None}
                
                with pytest.raises(ValueError) as exc_info:
                    await processor._extract_text(temp_file_path)
                
                assert "No text content extracted" in str(exc_info.value)
        finally:
            os.unlink(temp_file_path) 