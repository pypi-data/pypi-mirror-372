#!/bin/bash

# RAGPack CLI Examples
# This script demonstrates various CLI commands for RAGPack

echo "🚀 RAGPack CLI Examples"
echo "======================="

# Create sample documents for testing
echo "📄 Creating sample documents..."
mkdir -p sample_docs

cat > sample_docs/ai_basics.txt << 'EOF'
Artificial Intelligence Basics

AI is the simulation of human intelligence in machines. Key concepts include:
- Machine Learning: Algorithms that improve through experience
- Deep Learning: Neural networks with multiple layers
- Natural Language Processing: Understanding human language
- Computer Vision: Interpreting visual information

Applications include healthcare, finance, autonomous vehicles, and more.
EOF

cat > sample_docs/ml_guide.txt << 'EOF'
Machine Learning Guide

Types of Machine Learning:
1. Supervised Learning - Learning from labeled data
2. Unsupervised Learning - Finding patterns in unlabeled data
3. Reinforcement Learning - Learning through trial and error

Popular algorithms:
- Linear Regression
- Decision Trees
- Random Forest
- Neural Networks
- Support Vector Machines

Tools: Python, scikit-learn, TensorFlow, PyTorch
EOF

cat > sample_docs/installation.txt << 'EOF'
RAGPack Installation Instructions

Basic Installation:
pip install ragpack

With optional providers:
pip install ragpack[google]     # Google Vertex AI
pip install ragpack[groq]       # Groq
pip install ragpack[cerebras]   # Cerebras
pip install ragpack[all]        # All providers

Environment Setup:
export OPENAI_API_KEY="your-key"
export GOOGLE_CLOUD_PROJECT="your-project"

Verification:
python -c "import ragpack; print(ragpack.get_version())"
EOF

echo "✅ Sample documents created"

# Example 1: Create a basic RAG pack
echo ""
echo "📦 Example 1: Creating a basic RAG pack"
echo "Command: ragpack create sample_docs/ --output my_knowledge.rag --name 'AI Knowledge Base'"

ragpack create sample_docs/ --output my_knowledge.rag --name "AI Knowledge Base"

if [ $? -eq 0 ]; then
    echo "✅ Pack created successfully"
else
    echo "❌ Pack creation failed (check API keys)"
fi

# Example 2: Get pack information
echo ""
echo "📊 Example 2: Getting pack information"
echo "Command: ragpack info my_knowledge.rag"

if [ -f "my_knowledge.rag" ]; then
    ragpack info my_knowledge.rag
else
    echo "❌ Pack file not found"
fi

# Example 3: Query the pack (retrieval only)
echo ""
echo "🔍 Example 3: Querying the pack"
echo "Command: ragpack query my_knowledge.rag 'What is machine learning?' --top-k 2"

if [ -f "my_knowledge.rag" ]; then
    ragpack query my_knowledge.rag "What is machine learning?" --top-k 2
else
    echo "❌ Pack file not found"
fi

# Example 4: Ask questions (with LLM)
echo ""
echo "🤖 Example 4: Asking questions with LLM"
echo "Command: ragpack ask my_knowledge.rag 'How do I install RAGPack?' --show-sources"

if [ -f "my_knowledge.rag" ]; then
    ragpack ask my_knowledge.rag "How do I install RAGPack?" --show-sources
else
    echo "❌ Pack file not found"
fi

# Example 5: Create pack with custom settings
echo ""
echo "⚙️ Example 5: Creating pack with custom settings"
echo "Command: ragpack create sample_docs/ --output custom_pack.rag --chunk-size 1024 --chunk-overlap 100 --embedding-provider openai --embedding-model text-embedding-3-large"

ragpack create sample_docs/ \
    --output custom_pack.rag \
    --chunk-size 1024 \
    --chunk-overlap 100 \
    --embedding-provider openai \
    --embedding-model text-embedding-3-large

# Example 6: Query with provider overrides
echo ""
echo "🔄 Example 6: Query with provider overrides"
echo "Command: ragpack ask custom_pack.rag 'What are the types of machine learning?' --llm-provider openai --llm-model gpt-3.5-turbo --temperature 0.7"

if [ -f "custom_pack.rag" ]; then
    ragpack ask custom_pack.rag "What are the types of machine learning?" \
        --llm-provider openai \
        --llm-model gpt-3.5-turbo \
        --temperature 0.7
else
    echo "❌ Custom pack file not found"
fi

# Example 7: Create encrypted pack
echo ""
echo "🔒 Example 7: Creating encrypted pack"
echo "Command: ragpack create sample_docs/ --output encrypted_pack.rag --encrypt-key 'demo_password'"

ragpack create sample_docs/ \
    --output encrypted_pack.rag \
    --encrypt-key "demo_password"

# Example 8: Query encrypted pack
echo ""
echo "🔓 Example 8: Querying encrypted pack"
echo "Command: ragpack query encrypted_pack.rag 'What is AI?' --decrypt-key 'demo_password'"

if [ -f "encrypted_pack.rag" ]; then
    ragpack query encrypted_pack.rag "What is AI?" --decrypt-key "demo_password"
else
    echo "❌ Encrypted pack file not found"
fi

# Example 9: Multiple provider demonstration
echo ""
echo "🌐 Example 9: Multiple provider examples"

# Try HuggingFace (offline)
echo "Command: ragpack create sample_docs/ --output hf_pack.rag --embedding-provider huggingface --embedding-model all-MiniLM-L6-v2"
ragpack create sample_docs/ \
    --output hf_pack.rag \
    --embedding-provider huggingface \
    --embedding-model all-MiniLM-L6-v2

# Try Google (if configured)
if [ ! -z "$GOOGLE_CLOUD_PROJECT" ]; then
    echo "Command: ragpack create sample_docs/ --output google_pack.rag --embedding-provider google --embedding-model textembedding-gecko"
    ragpack create sample_docs/ \
        --output google_pack.rag \
        --embedding-provider google \
        --embedding-model textembedding-gecko
else
    echo "⚠️ GOOGLE_CLOUD_PROJECT not set, skipping Google example"
fi

# Example 10: Batch operations
echo ""
echo "📋 Example 10: Batch operations"

# Create multiple packs
for provider in openai huggingface; do
    if [ "$provider" = "openai" ] && [ -z "$OPENAI_API_KEY" ]; then
        echo "⚠️ Skipping OpenAI (no API key)"
        continue
    fi
    
    echo "Creating pack with $provider..."
    ragpack create sample_docs/ \
        --output "${provider}_batch.rag" \
        --embedding-provider "$provider" \
        --name "Batch Pack ($provider)"
done

# Query all available packs
echo ""
echo "Querying all available packs..."
for pack in *.rag; do
    if [ -f "$pack" ]; then
        echo "📦 Querying $pack:"
        ragpack query "$pack" "What is artificial intelligence?" --top-k 1 2>/dev/null || echo "❌ Query failed"
    fi
done

# Cleanup section
echo ""
echo "🧹 Cleanup (optional)"
echo "To remove all created files, run:"
echo "rm -rf sample_docs/ *.rag"

echo ""
echo "🎉 CLI examples completed!"
echo ""
echo "💡 Key CLI features demonstrated:"
echo "   ✓ Creating packs from files/directories"
echo "   ✓ Customizing chunk size and overlap"
echo "   ✓ Using different embedding providers"
echo "   ✓ Querying and asking questions"
echo "   ✓ Provider overrides at runtime"
echo "   ✓ Encryption and decryption"
echo "   ✓ Pack information and statistics"
echo ""
echo "📖 For more help, run: ragpack --help"
