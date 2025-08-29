"""
Provider Override Example

This example demonstrates how to use different embedding and LLM providers
with RAGPack, including runtime overrides and provider switching.
"""

import os
import tempfile
from pathlib import Path
from ragpack import RAGPack

def create_sample_documents():
    """Create sample documents for demonstration."""
    temp_dir = tempfile.mkdtemp()
    
    doc_path = Path(temp_dir) / "provider_guide.txt"
    doc_path.write_text("""
    RAGPack Provider Guide
    
    RAGPack supports multiple embedding and LLM providers:
    
    Embedding Providers:
    - OpenAI: text-embedding-3-small, text-embedding-3-large
    - HuggingFace: all-MiniLM-L6-v2, all-mpnet-base-v2 (offline)
    - Google: textembedding-gecko
    
    LLM Providers:
    - OpenAI: gpt-4o, gpt-4o-mini, gpt-3.5-turbo
    - Google: gemini-pro, gemini-1.5-flash
    - Groq: mixtral-8x7b-32768, llama2-70b-4096
    - Cerebras: llama3.1-8b, llama3.1-70b
    
    You can override providers at runtime without rebuilding the vectorstore,
    as long as the embedding dimensions match.
    """)
    
    return [str(doc_path)]

def demonstrate_creation_with_different_providers():
    """Show creating packs with different embedding providers."""
    print("🔧 Creating packs with different embedding providers...")
    
    document_files = create_sample_documents()
    
    # Example 1: OpenAI embeddings (default)
    print("\n1️⃣ Creating pack with OpenAI embeddings...")
    try:
        pack_openai = RAGPack.from_files(
            files=document_files,
            embed_model="openai:text-embedding-3-small",
            name="openai_pack"
        )
        pack_openai.save("openai_pack.rag")
        print("✅ OpenAI pack created and saved")
        
    except Exception as e:
        print(f"❌ Error with OpenAI: {e}")
        print("💡 Set OPENAI_API_KEY environment variable")
    
    # Example 2: HuggingFace embeddings (offline)
    print("\n2️⃣ Creating pack with HuggingFace embeddings...")
    try:
        pack_hf = RAGPack.from_files(
            files=document_files,
            embed_model="huggingface:all-MiniLM-L6-v2",
            name="huggingface_pack"
        )
        pack_hf.save("huggingface_pack.rag")
        print("✅ HuggingFace pack created and saved")
        
    except Exception as e:
        print(f"❌ Error with HuggingFace: {e}")
        print("💡 Install sentence-transformers: pip install sentence-transformers")
    
    # Example 3: Google embeddings
    print("\n3️⃣ Creating pack with Google embeddings...")
    try:
        pack_google = RAGPack.from_files(
            files=document_files,
            embed_model="google:textembedding-gecko",
            name="google_pack"
        )
        pack_google.save("google_pack.rag")
        print("✅ Google pack created and saved")
        
    except Exception as e:
        print(f"❌ Error with Google: {e}")
        print("💡 Set GOOGLE_CLOUD_PROJECT and install: pip install ragpack[google]")

def demonstrate_runtime_overrides():
    """Show loading packs with different provider overrides."""
    print("\n🔄 Demonstrating runtime provider overrides...")
    
    # Try to load an existing pack
    pack_files = ["openai_pack.rag", "huggingface_pack.rag", "google_pack.rag"]
    available_pack = None
    
    for pack_file in pack_files:
        if os.path.exists(pack_file):
            available_pack = pack_file
            break
    
    if not available_pack:
        print("❌ No pack files available for override demonstration")
        return
    
    print(f"📂 Using pack: {available_pack}")
    
    # Example 1: Load with original configuration
    print("\n1️⃣ Loading with original configuration...")
    try:
        pack_original = RAGPack.load(available_pack)
        stats = pack_original.get_stats()
        embed_config = stats['config']['embedding']
        llm_config = stats['config']['llm']
        
        print(f"✅ Original embedding: {embed_config['provider']}:{embed_config['model_name']}")
        print(f"✅ Original LLM: {llm_config['provider']}:{llm_config['model_name']}")
        
        # Test query
        results = pack_original.query("What providers does RAGPack support?", top_k=2)
        print(f"📊 Query returned {len(results)} results")
        
    except Exception as e:
        print(f"❌ Error loading original: {e}")
        return
    
    # Example 2: Override LLM provider only
    print("\n2️⃣ Loading with LLM override...")
    try:
        pack_llm_override = RAGPack.load(
            available_pack,
            llm_config={
                "provider": "openai",
                "model_name": "gpt-3.5-turbo",
                "temperature": 0.7
            }
        )
        
        # Test question answering
        answer = pack_llm_override.ask(
            "What are the main embedding providers?",
            top_k=2,
            temperature=0.3  # Override temperature for this query
        )
        print(f"✅ LLM override successful")
        print(f"🤖 Answer: {answer[:100]}...")
        
    except Exception as e:
        print(f"❌ Error with LLM override: {e}")
    
    # Example 3: Override both embedding and LLM (if dimensions match)
    print("\n3️⃣ Loading with both embedding and LLM overrides...")
    try:
        pack_both_override = RAGPack.load(
            available_pack,
            embedding_config={
                "provider": "openai",
                "model_name": "text-embedding-3-small"
            },
            llm_config={
                "provider": "openai", 
                "model_name": "gpt-4o-mini"
            },
            reindex_on_mismatch=True  # Rebuild if dimensions don't match
        )
        
        answer = pack_both_override.ask("How many LLM providers are supported?")
        print(f"✅ Both overrides successful")
        print(f"🤖 Answer: {answer[:100]}...")
        
    except Exception as e:
        print(f"❌ Error with both overrides: {e}")

def demonstrate_provider_specific_features():
    """Show provider-specific features and configurations."""
    print("\n⚙️ Demonstrating provider-specific features...")
    
    # HuggingFace with custom device
    print("\n1️⃣ HuggingFace with custom configuration...")
    try:
        from ragpack.embeddings import HuggingFace
        
        # Create HuggingFace embeddings with custom settings
        hf_embeddings = HuggingFace(
            model_name="all-MiniLM-L6-v2",
            device="cpu",  # or "cuda" if available
        )
        
        # Test embedding
        test_text = "This is a test sentence."
        embedding = hf_embeddings.embed_query(test_text)
        print(f"✅ HuggingFace embedding dimensions: {len(embedding)}")
        
    except Exception as e:
        print(f"❌ HuggingFace error: {e}")
    
    # OpenAI with custom parameters
    print("\n2️⃣ OpenAI with custom configuration...")
    try:
        from ragpack.llms import OpenAIChat
        
        # Create OpenAI LLM with custom settings
        openai_llm = OpenAIChat(
            model_name="gpt-3.5-turbo",
            temperature=0.8,
            max_tokens=150
        )
        
        response = openai_llm.invoke("What is RAGPack in one sentence?")
        print(f"✅ OpenAI response: {response}")
        
    except Exception as e:
        print(f"❌ OpenAI error: {e}")
        print("💡 Set OPENAI_API_KEY environment variable")

def cleanup_example_files():
    """Clean up example files."""
    print("\n🧹 Cleaning up example files...")
    
    files_to_remove = [
        "openai_pack.rag",
        "huggingface_pack.rag", 
        "google_pack.rag"
    ]
    
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"✅ Removed {file_path}")

def main():
    """Main example function."""
    print("🔧 RAGPack Provider Override Example")
    print("=" * 50)
    
    # Check available API keys
    print("\n🔑 Checking available API keys...")
    api_keys = {
        "OpenAI": os.getenv("OPENAI_API_KEY"),
        "Google Cloud Project": os.getenv("GOOGLE_CLOUD_PROJECT"),
        "Groq": os.getenv("GROQ_API_KEY"),
        "Cerebras": os.getenv("CEREBRAS_API_KEY")
    }
    
    for provider, key in api_keys.items():
        status = "✅ Available" if key else "❌ Not set"
        print(f"   {provider}: {status}")
    
    try:
        # Demonstrate different provider creation
        demonstrate_creation_with_different_providers()
        
        # Demonstrate runtime overrides
        demonstrate_runtime_overrides()
        
        # Demonstrate provider-specific features
        demonstrate_provider_specific_features()
        
    except KeyboardInterrupt:
        print("\n⏹️ Example interrupted by user")
    
    finally:
        # Cleanup
        cleanup_example_files()
    
    print("\n🎉 Provider override example completed!")
    print("\n💡 Key takeaways:")
    print("   - Different providers can be used for embeddings and LLMs")
    print("   - Runtime overrides allow flexibility without rebuilding")
    print("   - HuggingFace models work offline")
    print("   - Each provider has specific configuration options")

if __name__ == "__main__":
    main()
