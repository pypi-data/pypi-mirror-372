"""
HuggingFace embedding wrapper for RAGPack.

Provides a convenient wrapper around HuggingFace embeddings with proper error handling
and configuration management for offline/local embedding models.
"""

from typing import List, Optional, Dict, Any
from ..providers import get_embedding_provider, ProviderError


class HuggingFace:
    """
    HuggingFace embedding wrapper with lazy loading and error handling.
    
    This class provides a convenient interface to HuggingFace embeddings,
    particularly useful for offline scenarios or when using local models.
    
    Args:
        model_name: HuggingFace model name (default: "all-MiniLM-L6-v2")
        cache_folder: Directory to cache downloaded models (optional)
        device: Device to run the model on ('cpu', 'cuda', etc.)
        **kwargs: Additional arguments passed to the underlying embedding class
        
    Example:
        >>> embeddings = HuggingFace(model_name="all-mpnet-base-v2")
        >>> vectors = embeddings.embed_documents(["Hello world", "How are you?"])
    """
    
    def __init__(
        self, 
        model_name: str = "all-MiniLM-L6-v2",
        cache_folder: Optional[str] = None,
        device: str = "cpu",
        **kwargs
    ):
        self.model_name = model_name
        self.cache_folder = cache_folder
        self.device = device
        self.kwargs = kwargs
        self._embedding_instance = None
    
    @property
    def embedding_instance(self):
        """Lazy-loaded embedding instance."""
        if self._embedding_instance is None:
            model_kwargs = {"device": self.device}
            if self.cache_folder:
                model_kwargs["cache_folder"] = self.cache_folder
            
            self._embedding_instance = get_embedding_provider(
                provider="huggingface",
                model_name=self.model_name,
                model_kwargs=model_kwargs,
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
        dims = get_embedding_dimensions("huggingface", self.model_name)
        if dims is None:
            # Fallback: embed a test string to get dimensions
            test_embedding = self.embed_query("test")
            dims = len(test_embedding)
        return dims
    
    def __repr__(self) -> str:
        return f"HuggingFace(model_name='{self.model_name}', device='{self.device}')"
