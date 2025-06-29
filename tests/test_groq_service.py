"""
Unit tests for GroqService class.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from backend.services.groq_service import GroqService


class TestGroqService:
    """Test suite for GroqService class."""
    
    @pytest.fixture
    def groq_service(self):
        """Create a GroqService instance for testing."""
        with patch('backend.services.groq_service.AsyncGroq') as mock_groq:
            mock_client = AsyncMock()
            mock_groq.return_value = mock_client
            service = GroqService()
            service.client = mock_client
            return service
    
    def test_init(self):
        """Test GroqService initialization."""
        with patch('backend.services.groq_service.AsyncGroq') as mock_groq:
            with patch('os.getenv') as mock_getenv:
                mock_getenv.return_value = "test_api_key"
                service = GroqService()
                
                assert service.model == "llama-3.3-70b-versatile"
                mock_groq.assert_called_once_with(api_key="test_api_key")
    
    @pytest.mark.asyncio
    async def test_generate_response_success(self, groq_service, sample_search_results, sample_chat_history):
        """Test successful response generation."""
        # Setup mock response
        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content="This is a test response about BattleTech."))
        ]
        groq_service.client.chat.completions.create.return_value = mock_response
        
        query = "What is BattleTech?"
        result = await groq_service.generate_response(query, sample_search_results, sample_chat_history)
        
        assert result == "This is a test response about BattleTech."
        groq_service.client.chat.completions.create.assert_called_once()
        
        # Verify the call arguments
        call_args = groq_service.client.chat.completions.create.call_args
        assert call_args[1]['model'] == "llama-3.3-70b-versatile"
        assert call_args[1]['max_tokens'] == 1024
        assert call_args[1]['temperature'] == 0.1
        assert call_args[1]['top_p'] == 0.9
    
    @pytest.mark.asyncio
    async def test_generate_response_no_context(self, groq_service):
        """Test response generation without context documents."""
        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content="I need documents to be uploaded first."))
        ]
        groq_service.client.chat.completions.create.return_value = mock_response
        
        query = "What is BattleTech?"
        result = await groq_service.generate_response(query, [])
        
        assert "I need documents to be uploaded first." in result
        
        # Verify the system prompt includes guidance about no context
        call_args = groq_service.client.chat.completions.create.call_args
        messages = call_args[1]['messages']
        user_message = next(msg for msg in messages if msg['role'] == 'user')
        assert "No relevant documents found" in user_message['content']
    
    @pytest.mark.asyncio
    async def test_generate_response_with_chat_history(self, groq_service, sample_search_results, sample_chat_history):
        """Test response generation with chat history."""
        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content="Based on our previous conversation..."))
        ]
        groq_service.client.chat.completions.create.return_value = mock_response
        
        query = "Tell me more about that"
        result = await groq_service.generate_response(query, sample_search_results, sample_chat_history)
        
        assert result == "Based on our previous conversation..."
        
        # Verify chat history is included in messages
        call_args = groq_service.client.chat.completions.create.call_args
        messages = call_args[1]['messages']
        
        # Should have system message + chat history + current query
        assert len(messages) >= 3
        
        # Check that chat history messages are included
        history_messages = [msg for msg in messages if msg['role'] in ['user', 'assistant']]
        assert len(history_messages) >= len(sample_chat_history)
    
    @pytest.mark.asyncio
    async def test_generate_response_limits_context_docs(self, groq_service):
        """Test that context documents are limited to top 5."""
        # Create more than 5 context documents
        many_docs = [
            {"text": f"Document {i} content", "filename": f"doc{i}.pdf"}
            for i in range(10)
        ]
        
        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content="Response based on top documents."))
        ]
        groq_service.client.chat.completions.create.return_value = mock_response
        
        query = "What do the documents say?"
        result = await groq_service.generate_response(query, many_docs)
        
        # Verify only top 5 documents are used
        call_args = groq_service.client.chat.completions.create.call_args
        messages = call_args[1]['messages']
        user_message = next(msg for msg in messages if msg['role'] == 'user')
        
        # Count document references in the context
        doc_count = user_message['content'].count("Document:")
        assert doc_count <= 5
    
    @pytest.mark.asyncio
    async def test_generate_response_limits_chat_history(self, groq_service, sample_search_results):
        """Test that chat history is limited to last 6 messages."""
        # Create long chat history
        long_history = []
        for i in range(10):
            long_history.extend([
                {"role": "user", "content": f"Question {i}"},
                {"role": "assistant", "content": f"Answer {i}"}
            ])
        
        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content="Response with limited history."))
        ]
        groq_service.client.chat.completions.create.return_value = mock_response
        
        query = "Latest question"
        result = await groq_service.generate_response(query, sample_search_results, long_history)
        
        # Verify only last 6 messages are used
        call_args = groq_service.client.chat.completions.create.call_args
        messages = call_args[1]['messages']
        
        # Count non-system messages (excluding current query)
        history_messages = [msg for msg in messages[1:-1] if msg['role'] in ['user', 'assistant']]
        assert len(history_messages) <= 6
    
    @pytest.mark.asyncio
    async def test_generate_response_exception_handling(self, groq_service, sample_search_results):
        """Test exception handling in response generation."""
        groq_service.client.chat.completions.create.side_effect = Exception("API Error")
        
        query = "What is BattleTech?"
        
        with pytest.raises(Exception) as exc_info:
            await groq_service.generate_response(query, sample_search_results)
        
        assert "API Error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_generate_summary_success(self, groq_service):
        """Test successful summary generation."""
        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content="This is a concise summary."))
        ]
        groq_service.client.chat.completions.create.return_value = mock_response
        
        text = "This is a very long text that needs to be summarized. " * 50
        result = await groq_service.generate_summary(text)
        
        assert result == "This is a concise summary."
        
        # Verify the call parameters
        call_args = groq_service.client.chat.completions.create.call_args
        assert call_args[1]['max_tokens'] == 100
        assert call_args[1]['temperature'] == 0.1
        
        # Verify the system message asks for summarization
        messages = call_args[1]['messages']
        system_message = messages[0]
        assert system_message['role'] == 'system'
        assert 'Summarize' in system_message['content']
        assert '200 characters' in system_message['content']
    
    @pytest.mark.asyncio
    async def test_generate_summary_with_custom_length(self, groq_service):
        """Test summary generation with custom max length."""
        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content="Custom length summary."))
        ]
        groq_service.client.chat.completions.create.return_value = mock_response
        
        text = "Long text to summarize"
        custom_length = 150
        result = await groq_service.generate_summary(text, max_length=custom_length)
        
        assert result == "Custom length summary."
        
        # Verify custom length is used in system message
        call_args = groq_service.client.chat.completions.create.call_args
        messages = call_args[1]['messages']
        system_message = messages[0]
        assert f'{custom_length} characters' in system_message['content']
    
    @pytest.mark.asyncio
    async def test_generate_summary_exception_fallback(self, groq_service):
        """Test summary generation fallback when API fails."""
        groq_service.client.chat.completions.create.side_effect = Exception("API Error")
        
        text = "This is a text that should be truncated when API fails."
        max_length = 20
        result = await groq_service.generate_summary(text, max_length=max_length)
        
        # Should return truncated text with ellipsis
        assert len(result) <= max_length + 3  # +3 for "..."
        assert result.endswith("...")
        assert result.startswith("This is a text")
    
    @pytest.mark.asyncio
    async def test_generate_summary_short_text_fallback(self, groq_service):
        """Test summary generation fallback for short text."""
        groq_service.client.chat.completions.create.side_effect = Exception("API Error")
        
        short_text = "Short text"
        result = await groq_service.generate_summary(short_text, max_length=200)
        
        # Should return original text since it's shorter than max_length
        assert result == short_text
    
    @pytest.mark.asyncio
    async def test_system_prompt_content(self, groq_service, sample_search_results):
        """Test that system prompt contains expected guidelines."""
        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content="Test response"))
        ]
        groq_service.client.chat.completions.create.return_value = mock_response
        
        query = "Test query"
        await groq_service.generate_response(query, sample_search_results)
        
        call_args = groq_service.client.chat.completions.create.call_args
        messages = call_args[1]['messages']
        system_message = messages[0]
        
        assert system_message['role'] == 'system'
        system_content = system_message['content']
        
        # Check for key guidelines in system prompt
        assert 'helpful AI assistant' in system_content
        assert 'context documents' in system_content
        assert 'answer is not in the context' in system_content
        assert 'Cite the relevant documents' in system_content
        assert 'concise but comprehensive' in system_content
    
    @pytest.mark.asyncio
    async def test_context_formatting(self, groq_service):
        """Test that context documents are formatted correctly."""
        context_docs = [
            {"text": "First document content", "filename": "doc1.pdf"},
            {"text": "Second document content", "filename": "doc2.pdf"}
        ]
        
        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content="Test response"))
        ]
        groq_service.client.chat.completions.create.return_value = mock_response
        
        query = "Test query"
        await groq_service.generate_response(query, context_docs)
        
        call_args = groq_service.client.chat.completions.create.call_args
        messages = call_args[1]['messages']
        user_message = next(msg for msg in messages if msg['role'] == 'user')
        
        # Verify document formatting
        assert "Document: doc1.pdf" in user_message['content']
        assert "Content: First document content" in user_message['content']
        assert "Document: doc2.pdf" in user_message['content']
        assert "Content: Second document content" in user_message['content']
    
    @pytest.mark.asyncio
    async def test_response_with_logging(self, groq_service, sample_search_results):
        """Test that errors are logged appropriately."""
        with patch('backend.services.groq_service.logger') as mock_logger:
            groq_service.client.chat.completions.create.side_effect = Exception("Test error")
            
            query = "Test query"
            
            with pytest.raises(Exception):
                await groq_service.generate_response(query, sample_search_results)
            
            # Verify error was logged
            mock_logger.error.assert_called_once()
            error_call = mock_logger.error.call_args[0][0]
            assert "Error generating response with Groq" in error_call 