# ragpackai Documentation

Welcome to ragpackai - the Portable Retrieval-Augmented Generation Library!

ragpackai allows you to create, save, load, and query portable RAG packs containing documents, embeddings, vectorstores, and configuration metadata in a single `.rag` file.

## Quick Start

```python
from ragpackai import ragpackai

# Create a pack from documents
pack = ragpackai.from_files([
    "docs/manual.pdf", 
    "notes.txt",
    "knowledge_base/"
])

# Save the pack
pack.save("my_knowledge.rag")

# Load and query
pack = ragpackai.load("my_knowledge.rag")
answer = pack.ask("What are the main features?")
print(answer)
```

## Table of Contents

```{toctree}
:maxdepth: 2
:caption: Contents:

installation
quickstart
api_reference
examples
providers
cli
security
contributing
changelog
```

## Features

- 🚀 **Portable RAG Packs**: Bundle everything into a single `.rag` file
- 🔄 **Provider Flexibility**: Support for OpenAI, Google, Groq, Cerebras, and HuggingFace
- 🔒 **Encryption Support**: Optional AES-GCM encryption for sensitive data
- 🎯 **Runtime Overrides**: Change embedding/LLM providers without rebuilding
- 📚 **Multiple Formats**: Support for PDF, TXT, MD, and more
- 🛠️ **CLI Tools**: Command-line interface for easy pack management
- 🔧 **Lazy Loading**: Efficient dependency management with lazy imports

## Indices and tables

* {ref}`genindex`
* {ref}`modindex`
* {ref}`search`