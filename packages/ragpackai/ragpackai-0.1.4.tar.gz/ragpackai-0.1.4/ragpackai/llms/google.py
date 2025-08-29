"""
Google LLM wrapper for ragpackai.

Provides a convenient wrapper around Google Vertex AI chat models with proper error handling
and configuration management.
"""

from typing import List, Optional, Dict, Any, Union
import os
from ..providers import get_llm_provider, ProviderError


class GoogleChat:
    """
    Google Vertex AI chat model wrapper with lazy loading and error handling.
    
    This class provides a convenient interface to Google Vertex AI chat models
    with proper authentication and project configuration.
    
    Args:
        model_name: Google model name (default: "gemini-1.5-flash")
        project: Google Cloud project ID (optional, will use GOOGLE_CLOUD_PROJECT env var)
        location: Google Cloud location (default: "us-central1")
        temperature: Sampling temperature (default: 0.0)
        max_tokens: Maximum tokens to generate (optional)
        credentials: Path to service account JSON file (optional)
        **kwargs: Additional arguments passed to the underlying LLM class
        
    Example:
        >>> llm = GoogleChat(model_name="gemini-pro", project="my-project", temperature=0.7)
        >>> response = llm.invoke("What is the capital of France?")
    """
    
    def __init__(
        self, 
        model_name: str = "gemini-1.5-flash",
        project: Optional[str] = None,
        location: str = "us-central1",
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        credentials: Optional[str] = None,
        **kwargs
    ):
        self.model_name = model_name
        self.project = project or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = location
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.credentials = credentials
        self.kwargs = kwargs
        self._llm_instance = None
        
        if not self.project:
            raise ProviderError(
                "Google Cloud project not found. Please set GOOGLE_CLOUD_PROJECT environment variable "
                "or pass project parameter."
            )
    
    @property
    def llm_instance(self):
        """Lazy-loaded LLM instance."""
        if self._llm_instance is None:
            provider_kwargs = {
                "project": self.project,
                "location": self.location,
                "temperature": self.temperature,
            }
            
            if self.max_tokens:
                provider_kwargs["max_output_tokens"] = self.max_tokens
            
            if self.credentials:
                provider_kwargs["credentials"] = self.credentials
            
            provider_kwargs.update(self.kwargs)
            
            self._llm_instance = get_llm_provider(
                provider="google",
                model_name=self.model_name,
                **provider_kwargs
            )
        return self._llm_instance
    
    def invoke(self, prompt: str) -> str:
        """
        Generate a response to a prompt.
        
        Args:
            prompt: Input prompt text
            
        Returns:
            Generated response text
        """
        response = self.llm_instance.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)
    
    def batch(self, prompts: List[str]) -> List[str]:
        """
        Generate responses to multiple prompts in batch.
        
        Args:
            prompts: List of input prompt texts
            
        Returns:
            List of generated response texts
        """
        responses = self.llm_instance.batch(prompts)
        return [resp.content if hasattr(resp, 'content') else str(resp) for resp in responses]
    
    def stream(self, prompt: str):
        """
        Stream a response to a prompt.
        
        Args:
            prompt: Input prompt text
            
        Yields:
            Response chunks as they are generated
        """
        for chunk in self.llm_instance.stream(prompt):
            yield chunk.content if hasattr(chunk, 'content') else str(chunk)
    
    def __repr__(self) -> str:
        return f"GoogleChat(model_name='{self.model_name}', project='{self.project}', temperature={self.temperature})"
