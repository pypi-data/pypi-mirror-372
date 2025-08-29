"""
Core ragpackai class for portable Retrieval-Augmented Generation.

This module contains the main ragpackai class that provides functionality to create,
save, load, and query portable RAG packs containing documents, embeddings,
vectorstores, and configuration metadata.
"""

import os
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from tqdm import tqdm

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    from langchain_chroma import Chroma
    from langchain_community.document_loaders import TextLoader, PyPDFLoader
except ImportError as e:
    raise ImportError(f"Required dependencies not installed: {e}")

from .providers import (
    get_embedding_provider, 
    get_embedding_dimensions,
    parse_model_string,
    validate_provider_config,
    ProviderError
)
from .storage import save_rag_pack, load_rag_pack, StorageError
from .pipeline import RAGPipeline


class ragpackai:
    """
    Main ragpackai class for creating and managing portable RAG packs.
    
    A ragpackai encapsulates documents, embeddings, vectorstore, and configuration
    into a portable .rag file that can be shared and loaded on different systems.
    
    Example:
        >>> # Create from files
        >>> pack = ragpackai.from_files(["doc1.txt", "doc2.pdf"])
        >>> pack.save("my_pack.rag")
        
        >>> # Load existing pack
        >>> pack = ragpackai.load("my_pack.rag")
        >>> answer = pack.ask("What is this about?")
    """
    
    def __init__(
        self,
        name: str = "ragpackai",
        metadata: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new ragpackai.
        
        Args:
            name: Name of the pack
            metadata: Pack metadata dictionary
            config: Configuration dictionary
        """
        self.name = name
        self.metadata = metadata or {}
        self.config = config or {}
        self.documents = []
        self.vectorstore = None
        self.pipeline = None
        self._temp_dir = None
        self._vectorstore_path = None
    
    @classmethod
    def from_files(
        cls,
        files: List[Union[str, Path]],
        embed_model: str = "openai:text-embedding-3-small",
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        name: str = "ragpackai",
        **kwargs
    ) -> "ragpackai":
        """
        Create a ragpackai from a list of files.
        
        Args:
            files: List of file paths to include
            embed_model: Embedding model in format "provider:model"
            chunk_size: Size of text chunks for splitting
            chunk_overlap: Overlap between chunks
            name: Name of the pack
            **kwargs: Additional arguments for embedding provider
            
        Returns:
            ragpackai instance
            
        Raises:
            ProviderError: If embedding provider is not available
            ValueError: If files cannot be processed
        """
        # Parse embedding model
        embed_provider, embed_model_name = parse_model_string(embed_model)
        
        # Create instance
        pack = cls(name=name)
        
        # Set up metadata
        pack.metadata = {
            "name": name,
            "created": datetime.now().isoformat(),
            "embed_model": embed_model,
            "embed_provider": embed_provider,
            "embed_model_name": embed_model_name,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "vectorstore": "chroma",
            "doc_count": len(files)
        }
        
        # Set up config
        pack.config = {
            "embedding": {
                "provider": embed_provider,
                "model_name": embed_model_name
            },
            "llm": {
                "provider": "openai",
                "model_name": "gpt-4o-mini"
            },
            "vectorstore": "chroma"
        }
        
        # Load and process documents
        print(f"Loading {len(files)} files...")
        documents = []
        
        for file_path in tqdm(files, desc="Loading files"):
            file_path = Path(file_path)
            
            if not file_path.exists():
                print(f"Warning: File not found: {file_path}")
                continue
            
            try:
                # Load document based on file type
                if file_path.suffix.lower() == '.pdf':
                    loader = PyPDFLoader(str(file_path))
                else:
                    loader = TextLoader(str(file_path), encoding='utf-8')
                
                docs = loader.load()
                
                # Add source metadata
                for doc in docs:
                    doc.metadata["source"] = str(file_path)
                    doc.metadata["filename"] = file_path.name
                
                documents.extend(docs)
                
                # Store document info
                pack.documents.append({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "content": docs[0].page_content if docs else "",
                    "metadata": docs[0].metadata if docs else {}
                })
                
            except Exception as e:
                print(f"Warning: Failed to load {file_path}: {e}")
                continue
        
        if not documents:
            raise ValueError("No documents could be loaded")
        
        # Split documents into chunks
        print("Splitting documents into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        split_docs = text_splitter.split_documents(documents)
        print(f"Created {len(split_docs)} chunks")
        
        # Create embeddings and vectorstore
        print("Creating embeddings...")
        embedding_provider = get_embedding_provider(
            embed_provider, 
            embed_model_name, 
            **kwargs
        )
        
        # Get embedding dimensions
        embed_dim = get_embedding_dimensions(embed_provider, embed_model_name)
        if embed_dim:
            pack.metadata["embed_dim"] = embed_dim
        
        # Create temporary directory for vectorstore
        pack._temp_dir = tempfile.mkdtemp()
        vectorstore_path = os.path.join(pack._temp_dir, "vectorstore")
        pack._vectorstore_path = vectorstore_path
        # Create Chroma vectorstore
        pack.vectorstore = Chroma.from_documents(
            documents=split_docs,
            embedding=embedding_provider,
            persist_directory=vectorstore_path
        )
        
        print(f"ragpackai '{name}' created successfully with {len(split_docs)} chunks")
        return pack
    
    @classmethod
    def load(
        cls,
        path: str,
        embedding_config: Optional[Dict[str, Any]] = None,
        llm_config: Optional[Dict[str, Any]] = None,
        reindex_on_mismatch: bool = False,
        decrypt_key: Optional[str] = None
    ) -> "ragpackai":
        """
        Load a ragpackai from a .rag file.
        
        Args:
            path: Path to the .rag file
            embedding_config: Override embedding configuration
            llm_config: Override LLM configuration
            reindex_on_mismatch: Rebuild vectorstore if embedding dimensions mismatch
            decrypt_key: Decryption key if pack is encrypted
            
        Returns:
            ragpackai instance
            
        Raises:
            StorageError: If loading fails
            ProviderError: If provider configuration is invalid
        """
        # Load pack data
        metadata, config, documents, vectorstore_path = load_rag_pack(
            path, decrypt_key=decrypt_key
        )
        
        # Create instance
        pack = cls(
            name=metadata.get("name", "loaded_pack"),
            metadata=metadata,
            config=config
        )
        pack.documents = documents
        
        # Handle configuration overrides
        final_embedding_config = config.get("embedding", {})
        final_llm_config = config.get("llm", {})
        
        if embedding_config:
            validate_provider_config(embedding_config, "embedding")
            final_embedding_config.update(embedding_config)
        
        if llm_config:
            validate_provider_config(llm_config, "llm")
            final_llm_config.update(llm_config)
        
        # Update config
        pack.config["embedding"] = final_embedding_config
        pack.config["llm"] = final_llm_config
        
        # Load vectorstore
        if os.path.exists(vectorstore_path):
            try:
                # Create embedding provider
                embedding_provider = get_embedding_provider(
                    final_embedding_config["provider"],
                    final_embedding_config["model_name"]
                )
                
                # Load Chroma vectorstore
                pack.vectorstore = Chroma(
                    persist_directory=vectorstore_path,
                    embedding_function=embedding_provider
                )
                
                # Check embedding dimension compatibility
                if embedding_config and not reindex_on_mismatch:
                    original_dim = metadata.get("embed_dim")
                    new_dim = get_embedding_dimensions(
                        final_embedding_config["provider"],
                        final_embedding_config["model_name"]
                    )
                    
                    if original_dim and new_dim and original_dim != new_dim:
                        raise ProviderError(
                            f"Embedding dimension mismatch: original={original_dim}, "
                            f"new={new_dim}. Set reindex_on_mismatch=True to rebuild vectorstore."
                        )
                
            except Exception as e:
                if reindex_on_mismatch and embedding_config:
                    print(f"Reindexing vectorstore due to: {e}")
                    pack._reindex_vectorstore(final_embedding_config)
                else:
                    raise
        
        print(f"ragpackai '{pack.name}' loaded successfully")
        return pack
    
    def _reindex_vectorstore(self, embedding_config: Dict[str, Any]) -> None:
        """Rebuild vectorstore with new embedding configuration."""
        if not self.documents:
            raise ValueError("No documents available for reindexing")
        
        # Recreate documents from stored content
        documents = []
        for doc_info in self.documents:
            doc = Document(
                page_content=doc_info["content"],
                metadata=doc_info.get("metadata", {})
            )
            documents.append(doc)
        
        # Split documents
        chunk_size = self.metadata.get("chunk_size", 512)
        chunk_overlap = self.metadata.get("chunk_overlap", 50)
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        split_docs = text_splitter.split_documents(documents)
        
        # Create new embedding provider
        embedding_provider = get_embedding_provider(
            embedding_config["provider"],
            embedding_config["model_name"]
        )
        
        # Create new vectorstore
        if self._temp_dir:
            shutil.rmtree(self._temp_dir)
        
        self._temp_dir = tempfile.mkdtemp()
        vectorstore_path = os.path.join(self._temp_dir, "vectorstore")
        
        self.vectorstore = Chroma.from_documents(
            documents=split_docs,
            embedding=embedding_provider,
            persist_directory=vectorstore_path
        )
        
        # Update metadata
        self.metadata["embed_model"] = f"{embedding_config['provider']}:{embedding_config['model_name']}"
        self.metadata["embed_provider"] = embedding_config["provider"]
        self.metadata["embed_model_name"] = embedding_config["model_name"]
        
        new_dim = get_embedding_dimensions(
            embedding_config["provider"],
            embedding_config["model_name"]
        )
        if new_dim:
            self.metadata["embed_dim"] = new_dim

    def save(self, path: str, encrypt_key: Optional[str] = None) -> None:
        """
        Save the ragpackai to a .rag file.

        Args:
            path: Path to save the .rag file
            encrypt_key: Optional encryption password

        Raises:
            StorageError: If saving fails
            ValueError: If pack is not ready to save
        """
        if not self.vectorstore:
            raise ValueError("No vectorstore available. Create pack from files first.")

        if not self.documents:
            raise ValueError("No documents available. Create pack from files first.")


        # Get vectorstore path
        vectorstore_path = getattr(self, "_vectorstore_path", None)
        if not vectorstore_path:
            raise ValueError("Vectorstore does not have a persist directory")

        # Save the pack
        save_rag_pack(
            pack_path=path,
            metadata=self.metadata,
            config=self.config,
            documents=self.documents,
            vectorstore_path=vectorstore_path,
            encrypt_key=encrypt_key
        )

        print(f"ragpackai saved to: {path}")

    def query(self, question: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a question (without LLM).

        Args:
            question: Question to search for
            top_k: Number of chunks to retrieve

        Returns:
            List of dictionaries with chunk, source, and score information

        Raises:
            ValueError: If vectorstore is not available
        """
        if not self.vectorstore:
            raise ValueError("No vectorstore available. Load or create pack first.")

        # Create pipeline if needed
        if not self.pipeline:
            self.pipeline = RAGPipeline(
                vectorstore=self.vectorstore,
                llm_config=self.config.get("llm", {})
            )

        return self.pipeline.retrieve(question, top_k=top_k)

    def ask(
        self,
        question: str,
        top_k: int = 4,
        temperature: float = 0.0,
        custom_prompt: Optional[str] = None
    ) -> str:
        """
        Ask a question and get an answer using retrieval + LLM.

        Args:
            question: Question to ask
            top_k: Number of chunks to retrieve for context
            temperature: Sampling temperature for LLM
            custom_prompt: Custom prompt template

        Returns:
            Generated answer string

        Raises:
            ValueError: If vectorstore or LLM config is not available
        """
        if not self.vectorstore:
            raise ValueError("No vectorstore available. Load or create pack first.")

        if not self.config.get("llm"):
            raise ValueError("No LLM configuration available.")

        # Create pipeline if needed
        if not self.pipeline:
            self.pipeline = RAGPipeline(
                vectorstore=self.vectorstore,
                llm_config=self.config["llm"]
            )

        return self.pipeline.ask(
            question=question,
            top_k=top_k,
            temperature=temperature,
            custom_prompt=custom_prompt
        )

    def update_llm_config(self, llm_config: Dict[str, Any]) -> None:
        """
        Update LLM configuration.

        Args:
            llm_config: New LLM configuration dictionary
        """
        validate_provider_config(llm_config, "llm")
        self.config["llm"] = llm_config

        if self.pipeline:
            self.pipeline.update_llm_config(llm_config)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get pack statistics and information.

        Returns:
            Dictionary with pack information
        """
        stats = {
            "name": self.name,
            "metadata": self.metadata,
            "config": self.config,
            "document_count": len(self.documents),
            "has_vectorstore": self.vectorstore is not None,
            "has_pipeline": self.pipeline is not None
        }

        if self.vectorstore and hasattr(self.vectorstore, '_collection'):
            try:
                collection = self.vectorstore._collection
                if hasattr(collection, 'count'):
                    stats["chunk_count"] = collection.count()
            except:
                pass

        return stats

    def __del__(self):
        """Cleanup temporary directory on deletion."""
        if self._temp_dir and os.path.exists(self._temp_dir):
            try:
                shutil.rmtree(self._temp_dir)
            except:
                pass

    def __repr__(self) -> str:
        doc_count = len(self.documents)
        has_vs = "✓" if self.vectorstore else "✗"
        return f"ragpackai(name='{self.name}', docs={doc_count}, vectorstore={has_vs})"



