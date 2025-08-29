# ragpackai 📦

**Portable Retrieval-Augmented Generation Library**

ragpackai is a Python library for creating, saving, loading, and querying portable RAG (Retrieval-Augmented Generation) packs. It allows you to bundle documents, embeddings, vectorstores, and configuration into a single `.rag` file that can be easily shared and deployed across different environments.

## ✨ Features

- 🚀 **Portable RAG Packs**: Bundle everything into a single `.rag` file
- 🔄 **Provider Flexibility**: Support for OpenAI, Google, Groq, Cerebras, and HuggingFace
- 🔒 **Encryption Support**: Optional AES-GCM encryption for sensitive data
- 🎯 **Runtime Overrides**: Change embedding/LLM providers without rebuilding
- 📚 **Multiple Formats**: Support for PDF, TXT, MD, and more
- 🛠️ **CLI Tools**: Command-line interface for easy pack management
- 🔧 **Lazy Loading**: Efficient dependency management with lazy imports

## 🚀 Quick Start

### Installation

```bash
# Core installation
pip install ragpackai

# With optional providers
pip install ragpackai[google]     # Google Vertex AI
pip install ragpackai[groq]       # Groq
pip install ragpackai[cerebras]   # Cerebras
pip install ragpackai[all]        # All providers
```

### Basic Usage

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

# Simple retrieval (no LLM)
results = pack.query("How do I install this?", top_k=3)
print(results)

# Question answering with LLM
answer = pack.ask("What are the main features?")
print(answer)
```

### Provider Overrides

```python
# Load with different providers
pack = ragpackai.load(
    "my_knowledge.rag",
    embedding_config={
        "provider": "google", 
        "model_name": "textembedding-gecko"
    },
    llm_config={
        "provider": "groq", 
        "model_name": "mixtral-8x7b-32768"
    }
)

answer = pack.ask("Explain the architecture")
```

## 🛠️ Command Line Interface

### Create a RAG Pack

```bash
# From files and directories
ragpackai create docs/ notes.txt --output knowledge.rag

# With custom settings
ragpackai create docs/ \
  --embedding-provider openai \
  --embedding-model text-embedding-3-large \
  --chunk-size 1024 \
  --encrypt-key mypassword
```

### Query and Ask

```bash
# Simple retrieval
ragpackai query knowledge.rag "How to install?"

# Question answering
ragpackai ask knowledge.rag "What are the requirements?" \
  --llm-provider openai \
  --llm-model gpt-4o

# With provider overrides
ragpackai ask knowledge.rag "Explain the API" \
  --embedding-provider google \
  --embedding-model textembedding-gecko \
  --llm-provider groq \
  --llm-model mixtral-8x7b-32768
```

### Pack Information

```bash
ragpackai info knowledge.rag
```

## 🏗️ Architecture

### .rag File Structure

A `.rag` file is a structured zip archive:

```
mypack.rag
├── metadata.json          # Pack metadata
├── config.json           # Default configurations
├── documents/            # Original documents
│   ├── doc1.txt
│   └── doc2.pdf
└── vectorstore/          # Chroma vectorstore
    ├── chroma.sqlite3
    └── ...
```

### Supported Providers

**Embedding Providers:**
- `openai`: text-embedding-3-small, text-embedding-3-large
- `huggingface`: all-MiniLM-L6-v2, all-mpnet-base-v2 (offline)
- `google`: textembedding-gecko

**LLM Providers:**
- `openai`: gpt-4o, gpt-4o-mini, gpt-3.5-turbo
- `google`: gemini-pro, gemini-1.5-flash
- `groq`: mixtral-8x7b-32768, llama2-70b-4096
- `cerebras`: llama3.1-8b, llama3.1-70b

## 📖 API Reference

### ragpackai Class

#### `ragpackai.from_files(files, embed_model="openai:text-embedding-3-small", **kwargs)`

Create a RAG pack from files.

**Parameters:**
- `files`: List of file paths or directories
- `embed_model`: Embedding model in format "provider:model"
- `chunk_size`: Text chunk size (default: 512)
- `chunk_overlap`: Chunk overlap (default: 50)
- `name`: Pack name

#### `ragpackai.load(path, embedding_config=None, llm_config=None, **kwargs)`

Load a RAG pack from file.

**Parameters:**
- `path`: Path to .rag file
- `embedding_config`: Override embedding configuration
- `llm_config`: Override LLM configuration
- `reindex_on_mismatch`: Rebuild vectorstore if dimensions mismatch
- `decrypt_key`: Decryption password

#### `pack.save(path, encrypt_key=None)`

Save pack to .rag file.

#### `pack.query(question, top_k=3)`

Retrieve relevant chunks (no LLM).

#### `pack.ask(question, top_k=4, temperature=0.0)`

Ask question with LLM.

### Provider Wrappers

```python
# Direct provider access
from ragpackai.embeddings import OpenAI, HuggingFace, Google
from ragpackai.llms import OpenAIChat, GoogleChat, GroqChat

# Create embedding provider
embeddings = OpenAI(model_name="text-embedding-3-large")
vectors = embeddings.embed_documents(["Hello world"])

# Create LLM provider
llm = OpenAIChat(model_name="gpt-4o", temperature=0.7)
response = llm.invoke("What is AI?")
```

## 🔧 Configuration

### Environment Variables

```bash
# API Keys
export OPENAI_API_KEY="your-key"
export GOOGLE_CLOUD_PROJECT="your-project"
export GROQ_API_KEY="your-key"
export CEREBRAS_API_KEY="your-key"

# Optional
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
```

### Configuration Files

```python
# Custom embedding config
embedding_config = {
    "provider": "huggingface",
    "model_name": "all-mpnet-base-v2",
    "device": "cuda"  # Use GPU
}

# Custom LLM config
llm_config = {
    "provider": "openai",
    "model_name": "gpt-4o",
    "temperature": 0.7,
    "max_tokens": 2000
}
```

## 🔒 Security

### Encryption

ragpackai supports AES-GCM encryption for sensitive data:

```python
# Save with encryption
pack.save("sensitive.rag", encrypt_key="strong-password")

# Load encrypted pack
pack = ragpackai.load("sensitive.rag", decrypt_key="strong-password")
```

### Best Practices

- Use strong passwords for encryption
- Store API keys securely in environment variables
- Validate .rag files before loading in production
- Consider network security when sharing packs

## 🧪 Examples

See the `examples/` directory for complete examples:

- `basic_usage.py` - Simple pack creation and querying
- `provider_overrides.py` - Using different providers
- `encryption_example.py` - Working with encrypted packs
- `cli_examples.sh` - Command-line usage examples

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 [Documentation](https://aimldev726.github.io/ragpackai/)
- 🐛 [Issue Tracker](https://github.com/AIMLDev726/ragpackai/issues)
- 💬 [Discussions](https://github.com/AIMLDev726/ragpackai/discussions)

## 🙏 Acknowledgments

Built with:
- [LangChain](https://langchain.com/) - LLM framework
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [Sentence Transformers](https://www.sbert.net/) - Embedding models
