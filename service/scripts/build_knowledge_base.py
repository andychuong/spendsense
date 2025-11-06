#!/usr/bin/env python
"""
Script to build the RAG knowledge base.

This script initializes the vector database and ingests data from various sources:
- Education catalog
- Partner offers
- Financial strategies
- User scenarios (from database)
- Operator decisions (from database)

Usage:
    # Build full knowledge base
    python scripts/build_knowledge_base.py --full

    # Build with database connection (requires DATABASE_URL env var)
    python scripts/build_knowledge_base.py --full --with-db

    # Clear existing and rebuild
    python scripts/build_knowledge_base.py --full --clear

    # Build only catalog content (no database)
    python scripts/build_knowledge_base.py --catalog-only

    # Test query after building
    python scripts/build_knowledge_base.py --full --test-query "high credit utilization"
"""

import sys
import os
import asyncio
import logging
import argparse

# Add service directory to path
service_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if service_dir not in sys.path:
    sys.path.insert(0, service_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_db_session():
    """Get database session (if available)."""
    try:
        # Try to import backend database
        backend_path = os.path.join(service_dir, "../backend")
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        from app.database import SessionLocal
        return SessionLocal()
    except Exception as e:
        logger.warning(f"Could not create database session: {e}")
        return None


async def build_knowledge_base(
    clear_existing: bool = False,
    with_db: bool = False,
    catalog_only: bool = False,
    test_query: str = None,
):
    """
    Build the RAG knowledge base.
    
    Args:
        clear_existing: Clear existing knowledge base before building
        with_db: Include database sources (user scenarios, operator decisions)
        catalog_only: Only build catalog content (education, partners, strategies)
        test_query: Optional test query to run after building
    """
    from app.rag.vector_store import VectorStore
    from app.rag.knowledge_builder import KnowledgeBaseBuilder
    from app.rag.config import RAGConfig
    
    logger.info("Starting knowledge base build process...")
    
    # Initialize vector store
    config = RAGConfig.from_env()
    vector_store = VectorStore(config=config)
    
    # Get database session if needed
    db_session = None
    if with_db and not catalog_only:
        db_session = get_db_session()
        if not db_session:
            logger.warning("Database session not available - skipping database sources")
    
    # Initialize builder
    builder = KnowledgeBaseBuilder(db_session, vector_store)
    
    # Build knowledge base
    stats = await builder.build_full_knowledge_base(
        clear_existing=clear_existing,
        include_strategies=True,
    )
    
    logger.info(f"\n✅ Knowledge base built with {stats['total_documents']} total documents")
    
    # Test query if provided
    if test_query:
        logger.info(f"\n{'='*80}")
        logger.info(f"Testing query: '{test_query}'")
        logger.info(f"{'='*80}")
        
        results = vector_store.search(query=test_query, top_k=5)
        
        logger.info(f"\nFound {len(results['ids'][0])} results:")
        for i, (doc_id, content, metadata, distance) in enumerate(zip(
            results['ids'][0],
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ), 1):
            similarity = 1 / (1 + distance)
            logger.info(f"\n{i}. [{doc_id}] (similarity: {similarity:.3f})")
            logger.info(f"   Type: {metadata.get('type')}")
            logger.info(f"   Content: {content[:200]}...")
    
    # Close database session
    if db_session:
        db_session.close()
    
    logger.info("\n✅ Knowledge base build complete!")
    return stats


async def query_knowledge_base(query: str, top_k: int = 5, filters: dict = None):
    """Query the knowledge base."""
    from app.rag.vector_store import VectorStore
    from app.rag.config import RAGConfig
    
    logger.info(f"Querying knowledge base: '{query}'")
    
    config = RAGConfig.from_env()
    vector_store = VectorStore(config=config)
    
    results = vector_store.search(query=query, top_k=top_k, filters=filters)
    
    logger.info(f"\nFound {len(results['ids'][0])} results:")
    for i, (doc_id, content, metadata, distance) in enumerate(zip(
        results['ids'][0],
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    ), 1):
        similarity = 1 / (1 + distance)
        print(f"\n{'='*80}")
        print(f"Result {i}: {doc_id}")
        print(f"Similarity: {similarity:.3f}")
        print(f"Type: {metadata.get('type')}")
        print(f"Metadata: {metadata}")
        print(f"\nContent:")
        print(content)
    
    return results


async def get_knowledge_base_stats():
    """Get knowledge base statistics."""
    from app.rag.vector_store import VectorStore
    from app.rag.config import RAGConfig
    
    config = RAGConfig.from_env()
    vector_store = VectorStore(config=config)
    
    stats = vector_store.get_stats()
    
    print(f"\n{'='*80}")
    print("Knowledge Base Statistics")
    print(f"{'='*80}")
    print(f"Total Documents:      {stats['total_documents']}")
    print(f"Collection Name:      {stats['collection_name']}")
    print(f"Embedding Model:      {stats['embedding_model']}")
    print(f"Embedding Dimension:  {stats['embedding_dimension']}")
    print(f"Document Types:       {', '.join(stats.get('document_types', []))}")
    print(f"Personas:             {', '.join(str(p) for p in stats.get('personas', []))}")
    print(f"{'='*80}\n")
    
    return stats


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build and manage the RAG knowledge base",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Build options
    parser.add_argument(
        "--full",
        action="store_true",
        help="Build full knowledge base from all sources"
    )
    parser.add_argument(
        "--catalog-only",
        action="store_true",
        help="Only build catalog content (no database sources)"
    )
    parser.add_argument(
        "--with-db",
        action="store_true",
        help="Include database sources (requires DATABASE_URL env var)"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing knowledge base before building"
    )
    
    # Query options
    parser.add_argument(
        "--query",
        type=str,
        help="Query the knowledge base"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of results to return (default: 5)"
    )
    parser.add_argument(
        "--test-query",
        type=str,
        help="Test query to run after building"
    )
    
    # Stats
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show knowledge base statistics"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not any([args.full, args.catalog_only, args.query, args.stats]):
        parser.error("Must specify one of: --full, --catalog-only, --query, or --stats")
    
    try:
        if args.full or args.catalog_only:
            # Build knowledge base
            stats = asyncio.run(build_knowledge_base(
                clear_existing=args.clear,
                with_db=args.with_db,
                catalog_only=args.catalog_only,
                test_query=args.test_query,
            ))
            return 0
        
        elif args.query:
            # Query knowledge base
            asyncio.run(query_knowledge_base(
                query=args.query,
                top_k=args.top_k,
            ))
            return 0
        
        elif args.stats:
            # Show stats
            asyncio.run(get_knowledge_base_stats())
            return 0
    
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        return 1
    
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

