"""
OpenAI embedding wrapper for RAGPack.

Provides a convenient wrapper around OpenAI embeddings with proper error handling
and configuration management.
"""

from typing import List, Optional, Dict, Any
import os
from ..providers import get_embedding_provider, ProviderError


class OpenAI:
    """
    OpenAI embedding wrapper with lazy loading and error handling.
    
    This class provides a convenient interface to OpenAI embeddings while
    handling API key management and model configuration.
    
    Args:
        model_name: OpenAI embedding model name (default: "text-embedding-3-small")
        api_key: OpenAI API key (optional, will use OPENAI_API_KEY env var)
        **kwargs: Additional arguments passed to the underlying embedding class
        
    Example:
        >>> embeddings = OpenAI(model_name="text-embedding-3-large")
        >>> vectors = embeddings.embed_documents(["Hello world", "How are you?"])
    """
    
    def __init__(
        self, 
        model_name: str = "text-embedding-3-small",
        api_key: Optional[str] = None,
        **kwargs
    ):
        self.model_name = model_name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.kwargs = kwargs
        self._embedding_instance = None
        
        if not self.api_key:
            raise ProviderError(
                "OpenAI API key not found. Please set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
    
    @property
    def embedding_instance(self):
        """Lazy-loaded embedding instance."""
        if self._embedding_instance is None:
            self._embedding_instance = get_embedding_provider(
                provider="openai",
                model_name=self.model_name,
                openai_api_key=self.api_key,
                **self.kwargs
            )
        return self._embedding_instance
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of documents.
        
        Args:
            texts: List of text documents to embed
            
        Returns:
            List of embedding vectors
        """
        return self.embedding_instance.embed_documents(texts)
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query text.
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding vector
        """
        return self.embedding_instance.embed_query(text)
    
    def get_dimensions(self) -> int:
        """
        Get the embedding dimensions for the current model.
        
        Returns:
            Number of dimensions in the embedding vectors
        """
        from ..providers import get_embedding_dimensions
        dims = get_embedding_dimensions("openai", self.model_name)
        if dims is None:
            # Fallback: embed a test string to get dimensions
            test_embedding = self.embed_query("test")
            dims = len(test_embedding)
        return dims
    
    def __repr__(self) -> str:
        return f"OpenAI(model_name='{self.model_name}')"
