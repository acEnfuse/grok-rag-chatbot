"""
Unit tests for MilvusService class.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from backend.services.milvus_service import MilvusService


class TestMilvusService:
    """Test suite for MilvusService class."""
    
    @pytest.fixture
    def mock_milvus_client(self):
        """Create a mock Milvus client"""
        mock_client = Mock()
        mock_client.has_collection.return_value = False
        mock_client.create_schema.return_value = Mock()
        mock_client.prepare_index_params.return_value = Mock()
        mock_client.create_collection.return_value = None
        mock_client.insert.return_value = {"insert_count": 3}
        mock_client.search.return_value = [[]]
        mock_client.query.return_value = []
        mock_client.delete.return_value = None
        mock_client.list_collections.return_value = []
        return mock_client
    
    @pytest.fixture
    def mock_sentence_transformer(self):
        """Create a mock SentenceTransformer"""
        import numpy as np
        mock_model = Mock()
        
        # Mock encode to return the correct number of embeddings based on input
        def mock_encode(texts):
            if isinstance(texts, str):
                texts = [texts]
            # Return one embedding per text
            return np.array([[0.1, 0.2, 0.3] * 128 for _ in texts])  # 384 dimensions each
        
        mock_model.encode.side_effect = mock_encode
        return mock_model
    
    @pytest.fixture
    def milvus_service(self, mock_milvus_client, mock_sentence_transformer):
        """Create a MilvusService instance with mocked dependencies"""
        with patch.dict('os.environ', {
            'MILVUS_COLLECTION_PREFIX': 'test_',
            'COLLECTION_NAME': 'documents',
            'EMBEDDING_MODEL': 'all-MiniLM-L6-v2'
        }):
            service = MilvusService()
            service.client = mock_milvus_client
            service.embedding_model = mock_sentence_transformer
            return service
    
    def test_init(self):
        """Test MilvusService initialization"""
        with patch.dict('os.environ', {
            'MILVUS_COLLECTION_PREFIX': 'test_',
            'COLLECTION_NAME': 'documents',
            'EMBEDDING_MODEL': 'all-MiniLM-L6-v2'
        }):
            service = MilvusService()
            assert service.collection_name == "test_documents"
            assert service.embedding_model_name == "all-MiniLM-L6-v2"
            assert service.dimension == 384
    
    @pytest.mark.asyncio
    async def test_initialize_creates_collection(self, milvus_service, mock_milvus_client):
        """Test that initialize creates collection when it doesn't exist"""
        mock_milvus_client.has_collection.return_value = False
        
        with patch('backend.services.milvus_service.MilvusClient') as mock_client_class:
            mock_client_class.return_value = mock_milvus_client
            
            await milvus_service.initialize()
            
            mock_milvus_client.has_collection.assert_called_once()
            mock_milvus_client.create_collection.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_initialize_skips_existing_collection(self, milvus_service, mock_milvus_client):
        """Test that initialize skips creation when collection exists"""
        mock_milvus_client.has_collection.return_value = True
        
        with patch('backend.services.milvus_service.MilvusClient') as mock_client_class:
            mock_client_class.return_value = mock_milvus_client
            
            await milvus_service.initialize()
            
            mock_milvus_client.has_collection.assert_called_once()
            mock_milvus_client.create_collection.assert_not_called()
    
    def test_get_embedding_model_lazy_loading(self, milvus_service):
        """Test that embedding model is loaded lazily"""
        # Initially no model
        milvus_service.embedding_model = None
        
        with patch('backend.services.milvus_service.SentenceTransformer') as mock_st:
            mock_model = Mock()
            mock_st.return_value = mock_model
            
            result = milvus_service._get_embedding_model()
            
            assert result == mock_model
            assert milvus_service.embedding_model == mock_model
            mock_st.assert_called_once_with(milvus_service.embedding_model_name)
    
    def test_get_embedding_model_already_loaded(self, milvus_service):
        """Test that embedding model is not reloaded if already exists"""
        existing_model = Mock()
        milvus_service.embedding_model = existing_model
        
        with patch('backend.services.milvus_service.SentenceTransformer') as mock_st:
            result = milvus_service._get_embedding_model()
            
            assert result == existing_model
            mock_st.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_add_documents_success(self, milvus_service, mock_milvus_client, sample_document_chunks):
        """Test successful document addition"""
        mock_milvus_client.insert.return_value = {"insert_count": 3}
        
        result = await milvus_service.add_documents(sample_document_chunks)
        
        assert result["inserted_count"] == len(sample_document_chunks)
        mock_milvus_client.insert.assert_called_once()
        
        # Verify the insert call structure
        call_args = mock_milvus_client.insert.call_args
        assert call_args[1]["collection_name"] == milvus_service.collection_name
        assert len(call_args[1]["data"]) == len(sample_document_chunks)
    
    @pytest.mark.asyncio
    async def test_add_documents_empty_list(self, milvus_service):
        """Test adding empty document list"""
        result = await milvus_service.add_documents([])
        
        assert result["message"] == "No chunks to add"
    
    @pytest.mark.asyncio
    async def test_add_documents_embedding_failure(self, milvus_service, sample_document_chunks):
        """Test handling of embedding generation failure"""
        # Mock embedding model to raise exception
        with patch.object(milvus_service, '_generate_embeddings') as mock_embed:
            mock_embed.side_effect = Exception("Embedding failed")
            
            with pytest.raises(Exception) as exc_info:
                await milvus_service.add_documents(sample_document_chunks)
            
            assert "Embedding failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_search_documents_success(self, milvus_service, mock_milvus_client):
        """Test successful document search"""
        # Mock search results - Fix the structure to match actual Milvus response
        mock_hit1 = Mock()
        mock_hit1.get.side_effect = lambda key, default=None: {
            'id': 'doc1',
            'entity': {'text': 'Sample text 1', 'filename': 'doc1.pdf', 'chunk_index': 0},
            'distance': 0.8
        }.get(key, default)
        
        mock_hit2 = Mock()
        mock_hit2.get.side_effect = lambda key, default=None: {
            'id': 'doc2',
            'entity': {'text': 'Sample text 2', 'filename': 'doc2.pdf', 'chunk_index': 1},
            'distance': 0.7
        }.get(key, default)
        
        mock_hits = [mock_hit1, mock_hit2]
        mock_milvus_client.search.return_value = [mock_hits]
        
        query = "test query"
        results = await milvus_service.search_documents(query)
        
        assert len(results) == 2
        assert results[0]["text"] == "Sample text 1"
        assert results[0]["filename"] == "doc1.pdf"
        assert results[0]["score"] == 0.8
        
        mock_milvus_client.search.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_documents_no_results(self, milvus_service, mock_milvus_client):
        """Test search with no results"""
        mock_milvus_client.search.return_value = [[]]  # Empty results
        
        query = "no match query"
        results = await milvus_service.search_documents(query)
        
        assert results == []
    
    @pytest.mark.asyncio
    async def test_search_documents_embedding_failure(self, milvus_service):
        """Test search with embedding generation failure"""
        with patch.object(milvus_service, '_generate_embeddings') as mock_embed:
            mock_embed.side_effect = Exception("Embedding failed")
            
            with pytest.raises(Exception) as exc_info:
                await milvus_service.search_documents("test query")
            
            assert "Embedding failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_list_documents_success(self, milvus_service, mock_milvus_client):
        """Test successful document listing"""
        # Mock query results with duplicate filenames
        mock_results = [
            {"filename": "doc1.pdf", "chunk_index": 0},
            {"filename": "doc1.pdf", "chunk_index": 1},
            {"filename": "doc2.pdf", "chunk_index": 0},
        ]
        mock_milvus_client.query.return_value = mock_results
        
        documents = await milvus_service.list_documents()
        
        assert len(documents) == 2  # Should be deduplicated
        doc_names = [doc["filename"] for doc in documents]
        assert "doc1.pdf" in doc_names
        assert "doc2.pdf" in doc_names
        
        # Check chunk counts
        doc1 = next(doc for doc in documents if doc["filename"] == "doc1.pdf")
        assert doc1["chunk_count"] == 2
    
    @pytest.mark.asyncio
    async def test_list_documents_empty(self, milvus_service, mock_milvus_client):
        """Test listing documents when collection is empty"""
        mock_milvus_client.query.return_value = []
        
        documents = await milvus_service.list_documents()
        
        assert documents == []
    
    @pytest.mark.asyncio
    async def test_delete_document_success(self, milvus_service, mock_milvus_client):
        """Test successful document deletion"""
        filename = "test_document.pdf"
        
        await milvus_service.delete_document(filename)
        
        mock_milvus_client.delete.assert_called_once()
        call_args = mock_milvus_client.delete.call_args
        assert call_args[1]["collection_name"] == milvus_service.collection_name
        assert filename in call_args[1]["filter"]
    
    @pytest.mark.asyncio
    async def test_delete_document_not_found(self, milvus_service, mock_milvus_client):
        """Test deleting non-existent document"""
        filename = "nonexistent.pdf"
        
        # Should not raise exception even if document doesn't exist
        await milvus_service.delete_document(filename)
        
        mock_milvus_client.delete.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_collection_info_success(self, milvus_service, mock_milvus_client):
        """Test getting collection information"""
        # Mock has_collection to return True
        mock_milvus_client.has_collection.return_value = True
        
        # Mock query results for document count
        mock_milvus_client.query.return_value = [{"id": "1"}, {"id": "2"}]
        
        info = await milvus_service.get_collection_info()
        
        assert "collection_name" in info
        assert "row_count" in info
        assert info["row_count"] == 2
    
    def test_collection_name_with_prefix(self):
        """Test collection name generation with prefix"""
        with patch.dict('os.environ', {
            'MILVUS_COLLECTION_PREFIX': 'test_prefix_',
            'COLLECTION_NAME': 'docs'
        }):
            service = MilvusService()
            assert service.collection_name == "test_prefix_docs"
    
    def test_collection_name_without_prefix(self):
        """Test collection name generation without prefix"""
        with patch.dict('os.environ', {
            'COLLECTION_NAME': 'docs'
        }, clear=True):
            service = MilvusService()
            assert service.collection_name == "rag_app_docs"  # Default prefix
    
    @pytest.mark.asyncio
    async def test_create_collection_schema(self, milvus_service, mock_milvus_client):
        """Test collection schema creation"""
        mock_schema = Mock()
        mock_milvus_client.create_schema.return_value = mock_schema
        
        await milvus_service._create_collection()
        
        # Verify schema creation calls
        mock_milvus_client.create_schema.assert_called_once()
        mock_schema.add_field.assert_called()  # Should be called multiple times
        mock_milvus_client.create_collection.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_with_custom_params(self, milvus_service, mock_milvus_client):
        """Test search with custom parameters"""
        mock_milvus_client.search.return_value = [[]]
        
        await milvus_service.search_documents("test query", top_k=10)
        
        call_args = mock_milvus_client.search.call_args[1]
        assert call_args["limit"] == 10
    
    @pytest.mark.asyncio
    async def test_error_handling_in_search(self, milvus_service, mock_milvus_client):
        """Test error handling during search"""
        mock_milvus_client.search.side_effect = Exception("Search failed")
        
        with pytest.raises(Exception) as exc_info:
            await milvus_service.search_documents("test query")
        
        assert "Search failed" in str(exc_info.value)
    
    def test_generate_embeddings(self, milvus_service, mock_sentence_transformer):
        """Test embedding generation"""
        import numpy as np
        texts = ["text1", "text2", "text3"]
        mock_sentence_transformer.encode.return_value = np.array([[0.1, 0.2, 0.3]] * 3)
        
        embeddings = milvus_service._generate_embeddings(texts)
        
        assert len(embeddings) == 3
        mock_sentence_transformer.encode.assert_called_once_with(texts)
    
    @pytest.mark.asyncio
    async def test_batch_processing_large_documents(self, milvus_service, mock_milvus_client):
        """Test batch processing of large document sets"""
        # Create 100 sample chunks
        large_chunks = []
        for i in range(100):
            large_chunks.append({
                "text": f"Chunk {i} content",
                "filename": f"doc_{i//10}.pdf",
                "chunk_index": i % 10
            })
        
        mock_milvus_client.insert.return_value = {"insert_count": 100}
        
        result = await milvus_service.add_documents(large_chunks)
        
        assert result["inserted_count"] == 100
        mock_milvus_client.insert.assert_called_once()
        
        # Verify all chunks were processed
        call_args = mock_milvus_client.insert.call_args
        assert len(call_args[1]["data"]) == 100
    
    def test_embedding_dimension_consistency(self, milvus_service):
        """Test that embedding dimensions are consistent"""
        assert milvus_service.dimension == 384  # all-MiniLM-L6-v2 dimension
    
    @pytest.mark.asyncio
    async def test_logging_on_operations(self, milvus_service, sample_document_chunks):
        """Test that operations are logged appropriately"""
        with patch('backend.services.milvus_service.logger') as mock_logger:
            await milvus_service.add_documents(sample_document_chunks)
            
            # Verify logging occurred
            mock_logger.info.assert_called()
    
    @pytest.mark.asyncio
    async def test_list_app_collections(self, milvus_service, mock_milvus_client):
        """Test listing collections that belong to the app"""
        all_collections = [
            "test_documents",
            "test_other_collection", 
            "different_prefix_collection",
            "test_another"
        ]
        mock_milvus_client.list_collections.return_value = all_collections
        
        app_collections = await milvus_service.list_app_collections()
        
        expected = ["test_documents", "test_other_collection", "test_another"]
        assert sorted(app_collections) == sorted(expected)
    
    @pytest.mark.asyncio
    async def test_connection_parameters(self):
        """Test connection parameter handling"""
        with patch.dict('os.environ', {
            'MILVUS_HOST': 'localhost',
            'MILVUS_PORT': '19530',
            'MILVUS_TOKEN': 'test_token'
        }):
            with patch('backend.services.milvus_service.MilvusClient') as mock_client_class:
                service = MilvusService()
                await service.initialize()
                
                mock_client_class.assert_called_once_with(
                    uri='http://localhost:19530',
                    token='test_token'
                ) 