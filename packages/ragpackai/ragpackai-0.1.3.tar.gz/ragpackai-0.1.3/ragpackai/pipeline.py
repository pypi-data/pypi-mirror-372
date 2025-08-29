"""
Pipeline module for ragpackai.

Handles retrieval + LLM chaining for question answering with proper
integration of vectorstore and LLM components.
"""

from typing import List, Dict, Any, Optional, Union
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from .providers import get_llm_provider, validate_provider_config, ProviderError


class RAGPipeline:
    """
    RAG pipeline for retrieval-augmented generation.
    
    This class combines a vectorstore retriever with an LLM to provide
    question answering capabilities over a document collection.
    
    Args:
        vectorstore: Vectorstore instance for document retrieval
        llm_config: LLM configuration dictionary
        retrieval_kwargs: Additional arguments for retrieval
        
    Example:
        >>> pipeline = RAGPipeline(vectorstore, {"provider": "openai", "model_name": "gpt-4o-mini"})
        >>> answer = pipeline.ask("What is the main topic?", top_k=3)
    """
    
    def __init__(
        self,
        vectorstore,
        llm_config: Dict[str, Any],
        retrieval_kwargs: Optional[Dict[str, Any]] = None
    ):
        self.vectorstore = vectorstore
        self.llm_config = llm_config
        self.retrieval_kwargs = retrieval_kwargs or {}
        self._llm = None
        self._retriever = None
        self._qa_chain = None
        
        # Validate LLM config
        validate_provider_config(llm_config, "llm")
    
    @property
    def llm(self):
        """Lazy-loaded LLM instance."""
        if self._llm is None:
            provider = self.llm_config["provider"]
            model_name = self.llm_config["model_name"]
            
            # Extract additional LLM parameters
            llm_kwargs = {k: v for k, v in self.llm_config.items() 
                         if k not in ["provider", "model_name"]}
            
            self._llm = get_llm_provider(provider, model_name, **llm_kwargs)
        return self._llm
    
    @property
    def retriever(self):
        """Lazy-loaded retriever instance."""
        if self._retriever is None:
            self._retriever = self.vectorstore.as_retriever(**self.retrieval_kwargs)
        return self._retriever
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Query string
            top_k: Number of documents to retrieve
            
        Returns:
            List of dictionaries with chunk, source, and score information
        """
        # Update retriever search kwargs
        search_kwargs = {"k": top_k}
        if hasattr(self.retriever, 'search_kwargs'):
            self.retriever.search_kwargs.update(search_kwargs)
        
        # Perform retrieval using invoke (new API)
        docs = self.retriever.invoke(query)
        
        results = []
        for doc in docs:
            result = {
                "chunk": doc.page_content,
                "source": doc.metadata.get("source", "unknown"),
                "score": doc.metadata.get("score", 0.0)
            }
            # Add any additional metadata
            for key, value in doc.metadata.items():
                if key not in ["source", "score"]:
                    result[key] = value
            results.append(result)
        return results
    
    def ask(
        self, 
        question: str, 
        top_k: int = 4, 
        temperature: Optional[float] = None,
        custom_prompt: Optional[str] = None
    ) -> str:
        """
        Ask a question and get an answer using retrieval + LLM.
        
        Args:
            question: Question to ask
            top_k: Number of documents to retrieve for context
            temperature: Override temperature for this query
            custom_prompt: Custom prompt template to use
            
        Returns:
            Generated answer string
        """
        # Retrieve relevant documents
        retrieved_docs = self.retrieve(question, top_k=top_k)
        
        if not retrieved_docs:
            return "I couldn't find any relevant information to answer your question."
        
        # Prepare context from retrieved documents
        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            source = doc.get("source", "unknown")
            chunk = doc.get("chunk", "")
            context_parts.append(f"[{i}] Source: {source}\n{chunk}")
        
        context = "\n\n".join(context_parts)
        
        # Prepare prompt
        if custom_prompt:
            prompt_template = custom_prompt
        else:
            prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer based on the context, just say that you don't know, don't try to make up an answer.

Context:
{context}

Question: {question}

Answer:"""
        
        # Format the prompt
        formatted_prompt = prompt_template.format(context=context, question=question)
        
        # Generate answer
        try:
            # Create a temporary LLM instance with custom temperature if provided
            if temperature is not None:
                llm_config = self.llm_config.copy()
                llm_config["temperature"] = temperature
                
                provider = llm_config["provider"]
                model_name = llm_config["model_name"]
                llm_kwargs = {k: v for k, v in llm_config.items() 
                             if k not in ["provider", "model_name"]}
                
                temp_llm = get_llm_provider(provider, model_name, **llm_kwargs)
                response = temp_llm.invoke(formatted_prompt)
            else:
                response = self.llm.invoke(formatted_prompt)
            
            # Extract content from response
            if hasattr(response, 'content'):
                return response.content
            else:
                return str(response)
        
        except Exception as e:
            return f"Error generating answer: {str(e)}"
    
    def batch_ask(
        self, 
        questions: List[str], 
        top_k: int = 4,
        temperature: Optional[float] = None
    ) -> List[str]:
        """
        Ask multiple questions in batch.
        
        Args:
            questions: List of questions to ask
            top_k: Number of documents to retrieve for each question
            temperature: Override temperature for these queries
            
        Returns:
            List of generated answers
        """
        answers = []
        for question in questions:
            answer = self.ask(question, top_k=top_k, temperature=temperature)
            answers.append(answer)
        return answers
    
    def update_llm_config(self, new_config: Dict[str, Any]) -> None:
        """
        Update LLM configuration and reset cached instances.
        
        Args:
            new_config: New LLM configuration dictionary
        """
        validate_provider_config(new_config, "llm")
        self.llm_config = new_config
        self._llm = None  # Reset cached LLM
        self._qa_chain = None  # Reset cached chain
    
    def update_retrieval_config(self, new_kwargs: Dict[str, Any]) -> None:
        """
        Update retrieval configuration and reset cached retriever.
        
        Args:
            new_kwargs: New retrieval keyword arguments
        """
        self.retrieval_kwargs = new_kwargs
        self._retriever = None  # Reset cached retriever
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get pipeline statistics and configuration.
        
        Returns:
            Dictionary with pipeline information
        """
        stats = {
            "llm_config": self.llm_config,
            "retrieval_kwargs": self.retrieval_kwargs,
            "vectorstore_type": type(self.vectorstore).__name__,
        }
        
        # Add vectorstore-specific stats if available
        if hasattr(self.vectorstore, '_collection'):
            try:
                collection = self.vectorstore._collection
                if hasattr(collection, 'count'):
                    stats["document_count"] = collection.count()
            except:
                pass
        
        return stats
    
    def __repr__(self) -> str:
        provider = self.llm_config.get("provider", "unknown")
        model = self.llm_config.get("model_name", "unknown")
        return f"RAGPipeline(llm={provider}:{model}, vectorstore={type(self.vectorstore).__name__})"
