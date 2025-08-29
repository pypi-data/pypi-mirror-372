"""
Groq LLM wrapper for RAGPack.

Provides a convenient wrapper around Groq chat models with proper error handling
and configuration management.
"""

from typing import List, Optional, Dict, Any, Union
import os
from ..providers import get_llm_provider, ProviderError


class GroqChat:
    """
    Groq chat model wrapper with lazy loading and error handling.
    
    This class provides a convenient interface to Groq chat models while
    handling API key management and model configuration.
    
    Args:
        model_name: Groq model name (default: "mixtral-8x7b-32768")
        api_key: Groq API key (optional, will use GROQ_API_KEY env var)
        temperature: Sampling temperature (default: 0.0)
        max_tokens: Maximum tokens to generate (optional)
        **kwargs: Additional arguments passed to the underlying LLM class
        
    Example:
        >>> llm = GroqChat(model_name="llama2-70b-4096", temperature=0.7)
        >>> response = llm.invoke("What is the capital of France?")
    """
    
    def __init__(
        self, 
        model_name: str = "mixtral-8x7b-32768",
        api_key: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        self.model_name = model_name
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.kwargs = kwargs
        self._llm_instance = None
        
        if not self.api_key:
            raise ProviderError(
                "Groq API key not found. Please set GROQ_API_KEY environment variable "
                "or pass api_key parameter."
            )
    
    @property
    def llm_instance(self):
        """Lazy-loaded LLM instance."""
        if self._llm_instance is None:
            provider_kwargs = {
                "groq_api_key": self.api_key,
                "temperature": self.temperature,
            }
            
            if self.max_tokens:
                provider_kwargs["max_tokens"] = self.max_tokens
            
            provider_kwargs.update(self.kwargs)
            
            self._llm_instance = get_llm_provider(
                provider="groq",
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
        return f"GroqChat(model_name='{self.model_name}', temperature={self.temperature})"
