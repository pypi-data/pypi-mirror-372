"""
Google embedding wrapper for ragpackai.

Provides a convenient wrapper around Google embeddings with proper error handling
and configuration management. Supports both Google Generative AI (API key) and Vertex AI.
"""

from typing import List, Optional, Dict, Any
import os
from ..providers import get_embedding_provider, ProviderError


class Google:
    """
    Google embedding wrapper with lazy loading and error handling.

    This class provides a convenient interface to Google embeddings.
    It automatically detects whether to use Google Generative AI (with API key)
    or Vertex AI (with project configuration).

    Args:
        model_name: Google embedding model name (default: "models/embedding-001")
        api_key: Google API key (optional, will use GOOGLE_API_KEY or GEMINI_API_KEY env var)
        project: Google Cloud project ID (optional, for Vertex AI)
        location: Google Cloud location (default: "us-central1", for Vertex AI)
        use_vertex: Force use of Vertex AI instead of Generative AI (default: False)
        **kwargs: Additional arguments passed to the underlying embedding class

    Example:
        >>> # Using API key (Generative AI)
        >>> embeddings = Google(model_name="models/embedding-001")
        >>> vectors = embeddings.embed_documents(["Hello world", "How are you?"])

        >>> # Using Vertex AI
        >>> embeddings = Google(model_name="textembedding-gecko", use_vertex=True, project="my-project")
        >>> vectors = embeddings.embed_documents(["Hello world", "How are you?"])
    """

    def __init__(
        self,
        model_name: str = "models/embedding-001",
        api_key: Optional[str] = None,
        project: Optional[str] = None,
        location: str = "us-central1",
        use_vertex: bool = False,
        **kwargs
    ):
        self.model_name = model_name
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.project = project or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = location
        self.use_vertex = use_vertex
        self.kwargs = kwargs
        self._embedding_instance = None

        # Determine which provider to use
        if self.use_vertex or (not self.api_key and self.project):
            self.provider = "google-vertex"
            if not self.project:
                raise ProviderError(
                    "Google Cloud project not found for Vertex AI. Please set GOOGLE_CLOUD_PROJECT environment variable "
                    "or pass project parameter."
                )
        else:
            self.provider = "google"
            if not self.api_key:
                raise ProviderError(
                    "Google API key not found. Please set GOOGLE_API_KEY or GEMINI_API_KEY environment variable "
                    "or pass api_key parameter."
                )
    
    @property
    def embedding_instance(self):
        """Lazy-loaded embedding instance."""
        if self._embedding_instance is None:
            if self.provider == "google-vertex":
                provider_kwargs = {
                    "project": self.project,
                    "location": self.location,
                }
                provider_kwargs.update(self.kwargs)
            else:
                provider_kwargs = {
                    "google_api_key": self.api_key,
                }
                provider_kwargs.update(self.kwargs)

            self._embedding_instance = get_embedding_provider(
                provider=self.provider,
                model_name=self.model_name,
                **provider_kwargs
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
        dims = get_embedding_dimensions(self.provider, self.model_name)
        if dims is None:
            # Fallback: embed a test string to get dimensions
            test_embedding = self.embed_query("test")
            dims = len(test_embedding)
        return dims

    def __repr__(self) -> str:
        if self.provider == "google-vertex":
            return f"Google(model_name='{self.model_name}', provider='vertex', project='{self.project}')"
        else:
            return f"Google(model_name='{self.model_name}', provider='genai')"
