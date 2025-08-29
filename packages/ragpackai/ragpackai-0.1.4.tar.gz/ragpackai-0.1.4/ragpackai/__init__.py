"""
ragpackai - Portable Retrieval-Augmented Generation Library

A Python library for creating, saving, loading, and querying portable RAG packs
containing documents, embeddings, vectorstores, and configuration metadata.

Example usage:
    >>> from ragpackai import ragpackai
    >>> 
    >>> # Create a pack from files
    >>> pack = ragpackai.from_files(["doc1.txt", "doc2.pdf"])
    >>> pack.save("my_pack.rag")
    >>> 
    >>> # Load and query
    >>> pack = ragpackai.load("my_pack.rag")
    >>> answer = pack.ask("What is this about?")
    >>> print(answer)
"""

from .ragpackai import ragpackai
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
__version__ = "0.1.4"
__author__ = "ragpackai Team"
__email__ = "aistudentlearn4@gmail.com"
__description__ = "Portable Retrieval-Augmented Generation Library"

# Main exports
__all__ = [
    # Core classes
    "ragpackai",
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
    "name": "ragpackai",
    "version": __version__,
    "description": __description__,
    "author": __author__,
    "author_email": __email__,
    "url": "https://github.com/ragpackai/ragpackai",
    "license": "MIT",
    "python_requires": ">=3.9",
}


def get_version() -> str:
    """Get the current version of ragpackai."""
    return __version__


def get_package_info() -> dict:
    """Get package information."""
    return __package_info__.copy()


# Convenience functions for quick access
def create_pack(files, name="ragpackai", **kwargs):
    """
    Convenience function to create a ragpackai from files.
    
    Args:
        files: List of file paths
        name: Pack name
        **kwargs: Additional arguments for ragpackai.from_files()
        
    Returns:
        ragpackai instance
    """
    return ragpackai.from_files(files, name=name, **kwargs)


def load_pack(path, **kwargs):
    """
    Convenience function to load a ragpackai from file.
    
    Args:
        path: Path to .rag file
        **kwargs: Additional arguments for ragpackai.load()
        
    Returns:
        ragpackai instance
    """
    return ragpackai.load(path, **kwargs)


# Add convenience functions to __all__
__all__.extend(["create_pack", "load_pack", "get_version", "get_package_info"])


# Dependency checking with installation guidance
def _check_dependencies():
    """Check for optional dependencies and provide helpful warnings."""
    import warnings
    
    # Core RAG functionality
    try:
        import langchain
        import chromadb
        import langchain_chroma
    except ImportError as e:
        warnings.warn(
            f"Core RAG dependencies missing: {e}\n"
            f"Install with: pip install ragpackai[core]",
            ImportWarning
        )
    
    # LLM providers
    try:
        import openai
        import langchain_openai
    except ImportError:
        warnings.warn(
            "OpenAI dependencies missing. Install with: pip install ragpackai[openai]",
            ImportWarning
        )
    
    # Document processing
    try:
        import PyPDF2
    except ImportError:
        warnings.warn(
            "PDF processing unavailable. Install with: pip install ragpackai[documents]",
            ImportWarning
        )
    
    # Embeddings
    try:
        import sentence_transformers
    except ImportError:
        warnings.warn(
            "Sentence transformers unavailable. Install with: pip install ragpackai[embeddings]",
            ImportWarning
        )
    
    # FAISS (known to be problematic)
    try:
        import faiss
    except ImportError:
        warnings.warn(
            "FAISS unavailable (this is common on some systems).\n"
            f"Try: pip install ragpackai[faiss]\n"
            f"If that fails, use: conda install -c conda-forge faiss-cpu\n"
            f"FAISS is optional - ChromaDB works without it.",
            ImportWarning
        )


def check_dependencies():
    """
    Manually check dependencies and provide installation guidance.
    
    This function checks for optional dependencies and provides specific
    installation commands for missing components.
    """
    _check_dependencies()


def install_guide():
    """
    Print installation guide for different use cases.
    """
    print("🚀 ragpackai Installation Guide")
    print("=" * 40)
    print()
    print("📦 Basic installation (minimal dependencies):")
    print("   pip install ragpackai")
    print()
    print("🔧 Common installations:")
    print("   pip install ragpackai[standard]    # Most common use case")
    print("   pip install ragpackai[core]        # Core RAG functionality")
    print("   pip install ragpackai[openai]      # OpenAI integration")
    print("   pip install ragpackai[documents]   # PDF processing")
    print("   pip install ragpackai[embeddings]  # Sentence transformers")
    print()
    print("🏢 Provider-specific:")
    print("   pip install ragpackai[google]      # Google/Gemini")
    print("   pip install ragpackai[groq]        # Groq")
    print("   pip install ragpackai[cerebras]    # Cerebras")
    print("   pip install ragpackai[nvidia]      # NVIDIA")
    print()
    print("⚠️  Problematic dependencies:")
    print("   pip install ragpackai[faiss]       # May fail on some systems")
    print("   conda install -c conda-forge faiss-cpu  # Alternative for FAISS")
    print()
    print("🎯 Everything (may have issues):")
    print("   pip install ragpackai[all]")
    print()
    print("💡 If you encounter installation issues:")
    print("   1. Start with: pip install ragpackai[standard]")
    print("   2. Add specific providers as needed")
    print("   3. Skip FAISS if it fails to install")
    print("   4. Use conda for problematic packages")


# Add new functions to exports
__all__.extend(["check_dependencies", "install_guide"])
