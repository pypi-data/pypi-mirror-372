"""
Command Line Interface for RAGPack.

Provides command-line tools for creating, querying, and managing RAG packs.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import List, Optional

from . import RAGPack, ProviderError, StorageError, validate_rag_pack


def create_command(args) -> None:
    """Handle the create command."""
    try:
        # Collect files
        files = []
        for path in args.files:
            path = Path(path)
            if path.is_file():
                files.append(str(path))
            elif path.is_dir():
                # Add all supported files in directory
                for ext in ['.txt', '.pdf', '.md', '.rst']:
                    files.extend(str(f) for f in path.glob(f'**/*{ext}'))
            else:
                print(f"Warning: Path not found: {path}")
        
        if not files:
            print("Error: No valid files found")
            sys.exit(1)
        
        print(f"Creating RAG pack from {len(files)} files...")
        
        # Prepare embedding model
        if args.embedding_provider and args.embedding_model:
            embed_model = f"{args.embedding_provider}:{args.embedding_model}"
        else:
            embed_model = args.embed_model
        
        # Create pack
        pack = RAGPack.from_files(
            files=files,
            embed_model=embed_model,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            name=args.name or "ragpack"
        )
        
        # Save pack
        output_path = args.output or f"{args.name or 'ragpack'}.rag"
        pack.save(output_path, encrypt_key=args.encrypt_key)
        
        print(f"✓ RAG pack created: {output_path}")
        
        # Show stats
        stats = pack.get_stats()
        print(f"  Documents: {stats['document_count']}")
        if 'chunk_count' in stats:
            print(f"  Chunks: {stats['chunk_count']}")
        
    except Exception as e:
        print(f"Error creating pack: {e}")
        sys.exit(1)


def query_command(args) -> None:
    """Handle the query command."""
    try:
        # Prepare configs
        embedding_config = None
        if args.embedding_provider and args.embedding_model:
            embedding_config = {
                "provider": args.embedding_provider,
                "model_name": args.embedding_model
            }
        
        # Load pack
        pack = RAGPack.load(
            args.pack_path,
            embedding_config=embedding_config,
            decrypt_key=args.decrypt_key
        )
        
        # Query
        results = pack.query(args.question, top_k=args.top_k)
        
        print(f"Found {len(results)} relevant chunks:")
        print("=" * 50)
        
        for i, result in enumerate(results, 1):
            source = result.get('source', 'unknown')
            score = result.get('score', 0.0)
            chunk = result.get('chunk', '')
            
            print(f"\n[{i}] Source: {source} (Score: {score:.3f})")
            print("-" * 30)
            print(chunk[:500] + ("..." if len(chunk) > 500 else ""))
        
    except Exception as e:
        print(f"Error querying pack: {e}")
        sys.exit(1)


def ask_command(args) -> None:
    """Handle the ask command."""
    try:
        # Prepare configs
        embedding_config = None
        llm_config = None
        
        if args.embedding_provider and args.embedding_model:
            embedding_config = {
                "provider": args.embedding_provider,
                "model_name": args.embedding_model
            }
        
        if args.llm_provider and args.llm_model:
            llm_config = {
                "provider": args.llm_provider,
                "model_name": args.llm_model
            }
            if args.temperature is not None:
                llm_config["temperature"] = args.temperature
        
        # Load pack
        pack = RAGPack.load(
            args.pack_path,
            embedding_config=embedding_config,
            llm_config=llm_config,
            decrypt_key=args.decrypt_key
        )
        
        # Ask question
        answer = pack.ask(
            args.question,
            top_k=args.top_k,
            temperature=args.temperature
        )
        
        print("Answer:")
        print("=" * 50)
        print(answer)
        
        if args.show_sources:
            print("\nSources:")
            print("-" * 30)
            sources = pack.query(args.question, top_k=args.top_k)
            for i, source in enumerate(sources, 1):
                print(f"[{i}] {source.get('source', 'unknown')}")
        
    except Exception as e:
        print(f"Error asking question: {e}")
        sys.exit(1)


def info_command(args) -> None:
    """Handle the info command."""
    try:
        # Validate pack
        info = validate_rag_pack(args.pack_path)
        
        print(f"RAG Pack Information: {args.pack_path}")
        print("=" * 50)
        print(f"Size: {info['size_bytes']:,} bytes")
        print(f"Files: {info['files']}")
        print(f"Encrypted: {'Yes' if info['encrypted'] else 'No'}")
        print(f"Created: {info['created']}")
        
        # Try to load metadata if not encrypted
        if not info['encrypted']:
            try:
                metadata, config, documents, _ = load_rag_pack(args.pack_path)
                
                print(f"\nMetadata:")
                print(f"  Name: {metadata.get('name', 'unknown')}")
                print(f"  Documents: {metadata.get('doc_count', 'unknown')}")
                print(f"  Embedding Model: {metadata.get('embed_model', 'unknown')}")
                print(f"  Chunk Size: {metadata.get('chunk_size', 'unknown')}")
                print(f"  Vectorstore: {metadata.get('vectorstore', 'unknown')}")
                
                print(f"\nConfiguration:")
                print(f"  LLM: {config.get('llm', {}).get('provider', 'unknown')}:{config.get('llm', {}).get('model_name', 'unknown')}")
                print(f"  Embedding: {config.get('embedding', {}).get('provider', 'unknown')}:{config.get('embedding', {}).get('model_name', 'unknown')}")
                
            except Exception as e:
                print(f"\nCould not load detailed info: {e}")
        
    except Exception as e:
        print(f"Error getting pack info: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="RAGPack - Portable Retrieval-Augmented Generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ragpack create docs/ --output my_pack.rag
  ragpack query my_pack.rag "What is this about?"
  ragpack ask my_pack.rag "How do I install this?" --llm-provider openai --llm-model gpt-4o
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new RAG pack')
    create_parser.add_argument('files', nargs='+', help='Files or directories to include')
    create_parser.add_argument('--output', '-o', help='Output .rag file path')
    create_parser.add_argument('--name', help='Pack name')
    create_parser.add_argument('--embed-model', default='openai:text-embedding-3-small',
                              help='Embedding model (default: openai:text-embedding-3-small)')
    create_parser.add_argument('--chunk-size', type=int, default=512, help='Chunk size (default: 512)')
    create_parser.add_argument('--chunk-overlap', type=int, default=50, help='Chunk overlap (default: 50)')
    create_parser.add_argument('--encrypt-key', help='Encryption password')
    create_parser.add_argument('--embedding-provider', help='Embedding provider (openai, huggingface, google)')
    create_parser.add_argument('--embedding-model', help='Embedding model name')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Query a RAG pack (retrieval only)')
    query_parser.add_argument('pack_path', help='Path to .rag file')
    query_parser.add_argument('question', help='Question to search for')
    query_parser.add_argument('--top-k', type=int, default=3, help='Number of results (default: 3)')
    query_parser.add_argument('--decrypt-key', help='Decryption password')
    query_parser.add_argument('--embedding-provider', help='Override embedding provider')
    query_parser.add_argument('--embedding-model', help='Override embedding model')
    
    # Ask command
    ask_parser = subparsers.add_parser('ask', help='Ask a question (retrieval + LLM)')
    ask_parser.add_argument('pack_path', help='Path to .rag file')
    ask_parser.add_argument('question', help='Question to ask')
    ask_parser.add_argument('--top-k', type=int, default=4, help='Number of chunks for context (default: 4)')
    ask_parser.add_argument('--temperature', type=float, help='LLM temperature')
    ask_parser.add_argument('--decrypt-key', help='Decryption password')
    ask_parser.add_argument('--show-sources', action='store_true', help='Show source documents')
    ask_parser.add_argument('--embedding-provider', help='Override embedding provider')
    ask_parser.add_argument('--embedding-model', help='Override embedding model')
    ask_parser.add_argument('--llm-provider', help='Override LLM provider')
    ask_parser.add_argument('--llm-model', help='Override LLM model')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show pack information')
    info_parser.add_argument('pack_path', help='Path to .rag file')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    if args.command == 'create':
        create_command(args)
    elif args.command == 'query':
        query_command(args)
    elif args.command == 'ask':
        ask_command(args)
    elif args.command == 'info':
        info_command(args)


if __name__ == '__main__':
    main()
