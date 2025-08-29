"""
Tests for the core ragpackai functionality.
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import Mock, patch, MagicMock

# Import ragpackai components
from ragpackai import ragpackai, ProviderError, StorageError
from ragpackai.providers import parse_model_string, get_embedding_dimensions


class Testragpackai:
    """Test cases for ragpackai core functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_files = []
        
        # Create test documents
        self.doc1_path = Path(self.temp_dir) / "doc1.txt"
        self.doc1_path.write_text("This is a test document about artificial intelligence.")
        self.test_files.append(str(self.doc1_path))
        
        self.doc2_path = Path(self.temp_dir) / "doc2.txt"
        self.doc2_path.write_text("This document discusses machine learning algorithms.")
        self.test_files.append(str(self.doc2_path))
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('ragpackai.ragpackai.get_embedding_provider')
    @patch('ragpackai.ragpackai.Chroma')
    def test_from_files_basic(self, mock_chroma, mock_embedding_provider):
        """Test basic pack creation from files."""
        # Mock embedding provider
        mock_embeddings = Mock()
        mock_embedding_provider.return_value = mock_embeddings
        
        # Mock Chroma vectorstore
        mock_vectorstore = Mock()
        mock_chroma.from_documents.return_value = mock_vectorstore
        
        # Create pack
        pack = ragpackai.from_files(
            files=self.test_files,
            embed_model="openai:text-embedding-3-small",
            name="test_pack"
        )
        
        # Assertions
        assert pack.name == "test_pack"
        assert len(pack.documents) == 2
        assert pack.vectorstore is not None
        assert pack.metadata["name"] == "test_pack"
        assert pack.metadata["doc_count"] == 2
        assert pack.metadata["embed_model"] == "openai:text-embedding-3-small"
        
        # Verify embedding provider was called
        mock_embedding_provider.assert_called_once()
        mock_chroma.from_documents.assert_called_once()
    
    def test_from_files_invalid_files(self):
        """Test pack creation with invalid files."""
        with pytest.raises(ValueError, match="No documents could be loaded"):
            ragpackai.from_files(files=["nonexistent.txt"])
    
    @patch('ragpackai.storage.load_rag_pack')
    @patch('ragpackai.ragpackai.get_embedding_provider')
    @patch('ragpackai.ragpackai.Chroma')
    def test_load_basic(self, mock_chroma, mock_embedding_provider, mock_load_rag_pack):
        """Test basic pack loading."""
        # Mock load_rag_pack return
        mock_metadata = {
            "name": "test_pack",
            "embed_model": "openai:text-embedding-3-small",
            "doc_count": 2
        }
        mock_config = {
            "embedding": {"provider": "openai", "model_name": "text-embedding-3-small"},
            "llm": {"provider": "openai", "model_name": "gpt-4o-mini"}
        }
        mock_documents = [
            {"filename": "doc1.txt", "content": "test content 1"},
            {"filename": "doc2.txt", "content": "test content 2"}
        ]
        mock_vectorstore_path = "/tmp/vectorstore"
        
        mock_load_rag_pack.return_value = (
            mock_metadata, mock_config, mock_documents, mock_vectorstore_path
        )
        
        # Mock embedding provider and vectorstore
        mock_embeddings = Mock()
        mock_embedding_provider.return_value = mock_embeddings
        mock_vectorstore = Mock()
        mock_chroma.return_value = mock_vectorstore
        
        # Load pack
        pack = ragpackai.load("test.rag")
        
        # Assertions
        assert pack.name == "test_pack"
        assert len(pack.documents) == 2
        assert pack.vectorstore is not None
        assert pack.config["embedding"]["provider"] == "openai"
        assert pack.config["llm"]["provider"] == "openai"
        
        mock_load_rag_pack.assert_called_once_with("test.rag", decrypt_key=None)
        mock_embedding_provider.assert_called_once()
        mock_chroma.assert_called_once()
    
    @patch('ragpackai.storage.save_rag_pack')
    def test_save_basic(self, mock_save_rag_pack):
        """Test basic pack saving."""
        # Create a mock pack
        pack = ragpackai(name="test_pack")
        pack.documents = [{"filename": "test.txt", "content": "test"}]
        
        # Mock vectorstore
        mock_vectorstore = Mock()
        mock_vectorstore._persist_directory = "/tmp/vectorstore"
        mock_vectorstore.persist = Mock()
        pack.vectorstore = mock_vectorstore
        
        # Save pack
        pack.save("test.rag")
        
        # Assertions
        mock_vectorstore.persist.assert_called_once()
        mock_save_rag_pack.assert_called_once()
        
        # Check save_rag_pack arguments
        call_args = mock_save_rag_pack.call_args
        assert call_args[1]["pack_path"] == "test.rag"
        assert call_args[1]["encrypt_key"] is None
    
    def test_save_without_vectorstore(self):
        """Test saving pack without vectorstore raises error."""
        pack = ragpackai(name="test_pack")
        
        with pytest.raises(ValueError, match="No vectorstore available"):
            pack.save("test.rag")
    
    @patch('ragpackai.pipeline.RAGPipeline')
    def test_query(self, mock_pipeline_class):
        """Test pack querying."""
        # Create pack with mock vectorstore
        pack = ragpackai(name="test_pack")
        pack.vectorstore = Mock()
        pack.config = {"llm": {"provider": "openai", "model_name": "gpt-4o-mini"}}
        
        # Mock pipeline
        mock_pipeline = Mock()
        mock_pipeline.retrieve.return_value = [
            {"chunk": "test chunk", "source": "doc1.txt", "score": 0.9}
        ]
        mock_pipeline_class.return_value = mock_pipeline
        
        # Query pack
        results = pack.query("test question", top_k=3)
        
        # Assertions
        assert len(results) == 1
        assert results[0]["chunk"] == "test chunk"
        assert results[0]["source"] == "doc1.txt"
        
        mock_pipeline_class.assert_called_once()
        mock_pipeline.retrieve.assert_called_once_with("test question", top_k=3)
    
    @patch('ragpackai.pipeline.RAGPipeline')
    def test_ask(self, mock_pipeline_class):
        """Test pack question answering."""
        # Create pack with mock vectorstore
        pack = ragpackai(name="test_pack")
        pack.vectorstore = Mock()
        pack.config = {"llm": {"provider": "openai", "model_name": "gpt-4o-mini"}}
        
        # Mock pipeline
        mock_pipeline = Mock()
        mock_pipeline.ask.return_value = "This is the answer."
        mock_pipeline_class.return_value = mock_pipeline
        
        # Ask question
        answer = pack.ask("test question", top_k=4, temperature=0.7)
        
        # Assertions
        assert answer == "This is the answer."
        
        mock_pipeline_class.assert_called_once()
        mock_pipeline.ask.assert_called_once_with(
            question="test question",
            top_k=4,
            temperature=0.7,
            custom_prompt=None
        )
    
    def test_query_without_vectorstore(self):
        """Test querying without vectorstore raises error."""
        pack = ragpackai(name="test_pack")
        
        with pytest.raises(ValueError, match="No vectorstore available"):
            pack.query("test question")
    
    def test_ask_without_vectorstore(self):
        """Test asking without vectorstore raises error."""
        pack = ragpackai(name="test_pack")
        
        with pytest.raises(ValueError, match="No vectorstore available"):
            pack.ask("test question")
    
    def test_ask_without_llm_config(self):
        """Test asking without LLM config raises error."""
        pack = ragpackai(name="test_pack")
        pack.vectorstore = Mock()
        pack.config = {}
        
        with pytest.raises(ValueError, match="No LLM configuration available"):
            pack.ask("test question")
    
    def test_update_llm_config(self):
        """Test updating LLM configuration."""
        pack = ragpackai(name="test_pack")
        pack.config = {"llm": {"provider": "openai", "model_name": "gpt-4o-mini"}}
        
        new_config = {"provider": "google", "model_name": "gemini-pro"}
        pack.update_llm_config(new_config)
        
        assert pack.config["llm"] == new_config
    
    def test_get_stats(self):
        """Test getting pack statistics."""
        pack = ragpackai(name="test_pack")
        pack.documents = [{"filename": "test.txt"}]
        pack.vectorstore = Mock()
        
        stats = pack.get_stats()
        
        assert stats["name"] == "test_pack"
        assert stats["document_count"] == 1
        assert stats["has_vectorstore"] is True
        assert stats["has_pipeline"] is False
    
    def test_repr(self):
        """Test pack string representation."""
        pack = ragpackai(name="test_pack")
        pack.documents = [{"filename": "test.txt"}]
        pack.vectorstore = Mock()
        
        repr_str = repr(pack)
        assert "test_pack" in repr_str
        assert "docs=1" in repr_str
        assert "✓" in repr_str  # vectorstore present


class TestProviders:
    """Test cases for provider utilities."""
    
    def test_parse_model_string_with_provider(self):
        """Test parsing model string with provider."""
        provider, model = parse_model_string("openai:gpt-4o-mini")
        assert provider == "openai"
        assert model == "gpt-4o-mini"
    
    def test_parse_model_string_without_provider(self):
        """Test parsing model string without provider."""
        provider, model = parse_model_string("gpt-4o-mini")
        assert provider == "openai"  # Default
        assert model == "gpt-4o-mini"
    
    def test_get_embedding_dimensions_known_model(self):
        """Test getting dimensions for known model."""
        dims = get_embedding_dimensions("openai", "text-embedding-3-small")
        assert dims == 1536
    
    def test_get_embedding_dimensions_unknown_model(self):
        """Test getting dimensions for unknown model."""
        dims = get_embedding_dimensions("unknown", "unknown-model")
        assert dims is None


if __name__ == "__main__":
    pytest.main([__file__])
