"""
RAGPack - Portable Retrieval-Augmented Generation Library

A Python library for creating, saving, loading, and querying portable RAG packs
containing documents, embeddings, vectorstores, and configuration metadata.

Example usage:
    >>> from ragpack import RAGPack
    >>> 
    >>> # Create a pack from files
    >>> pack = RAGPack.from_files(["doc1.txt", "doc2.pdf"])
    >>> pack.save("my_pack.rag")
    >>> 
    >>> # Load and query
    >>> pack = RAGPack.load("my_pack.rag")
    >>> answer = pack.ask("What is this about?")
    >>> print(answer)
"""

from .ragpack import RAGPack
from .pipeline import RAGPipeline
from .providers import (
    ProviderError,
    get_embedding_provider,
    get_llm_provider,
    parse_model_string,
    validate_provider_config
)
from .storage import (
    StorageError,
    EncryptionError,
    save_rag_pack,
    load_rag_pack,
    validate_rag_pack
)

# Import embedding and LLM wrappers
from . import embeddings
from . import llms

# Version information
__version__ = "0.1.0"
__author__ = "RAGPack Team"
__email__ = "contact@ragpack.dev"
__description__ = "Portable Retrieval-Augmented Generation Library"

# Main exports
__all__ = [
    # Core classes
    "RAGPack",
    "RAGPipeline",
    
    # Provider functions
    "get_embedding_provider",
    "get_llm_provider",
    "parse_model_string",
    "validate_provider_config",
    
    # Storage functions
    "save_rag_pack",
    "load_rag_pack",
    "validate_rag_pack",
    
    # Exceptions
    "ProviderError",
    "StorageError", 
    "EncryptionError",
    
    # Submodules
    "embeddings",
    "llms",
]

# Package metadata
__package_info__ = {
    "name": "ragpack",
    "version": __version__,
    "description": __description__,
    "author": __author__,
    "author_email": __email__,
    "url": "https://github.com/ragpack/ragpack",
    "license": "MIT",
    "python_requires": ">=3.9",
}


def get_version() -> str:
    """Get the current version of RAGPack."""
    return __version__


def get_package_info() -> dict:
    """Get package information."""
    return __package_info__.copy()


# Convenience functions for quick access
def create_pack(files, name="ragpack", **kwargs):
    """
    Convenience function to create a RAGPack from files.
    
    Args:
        files: List of file paths
        name: Pack name
        **kwargs: Additional arguments for RAGPack.from_files()
        
    Returns:
        RAGPack instance
    """
    return RAGPack.from_files(files, name=name, **kwargs)


def load_pack(path, **kwargs):
    """
    Convenience function to load a RAGPack from file.
    
    Args:
        path: Path to .rag file
        **kwargs: Additional arguments for RAGPack.load()
        
    Returns:
        RAGPack instance
    """
    return RAGPack.load(path, **kwargs)


# Add convenience functions to __all__
__all__.extend(["create_pack", "load_pack", "get_version", "get_package_info"])


# Optional: Check for common dependencies and warn if missing
def _check_dependencies():
    """Check for optional dependencies and provide helpful warnings."""
    missing_deps = []
    
    try:
        import langchain
    except ImportError:
        missing_deps.append("langchain")
    
    try:
        import chromadb
    except ImportError:
        missing_deps.append("chromadb")
    
    try:
        import openai
    except ImportError:
        missing_deps.append("openai")
    
    if missing_deps:
        import warnings
        warnings.warn(
            f"Some core dependencies are missing: {', '.join(missing_deps)}. "
            f"Install them with: pip install {' '.join(missing_deps)}",
            ImportWarning
        )


# Run dependency check on import (optional)
# Uncomment the next line if you want to check dependencies on import
# _check_dependencies()
