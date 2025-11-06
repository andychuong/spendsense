"""Example usage of RAG recommendation system."""

import asyncio
import logging
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def example_1_build_knowledge_base():
    """Example 1: Build the knowledge base."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Build Knowledge Base")
    print("="*80 + "\n")
    
    from app.rag import VectorStore, KnowledgeBaseBuilder
    
    # Initialize vector store
    vector_store = VectorStore()
    
    # Initialize builder (without database for this example)
    builder = KnowledgeBaseBuilder(None, vector_store)
    
    # Build knowledge base
    stats = await builder.build_full_knowledge_base(
        clear_existing=True,
        include_strategies=True,
    )
    
    print(f"\n✅ Knowledge base built: {stats['total_documents']} documents")
    print(f"   - Education: {stats['education_content']}")
    print(f"   - Partners: {stats['partner_offers']}")
    print(f"   - Strategies: {stats['financial_strategies']}")


async def example_2_search_knowledge_base():
    """Example 2: Search the knowledge base."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Search Knowledge Base")
    print("="*80 + "\n")
    
    from app.rag import VectorStore
    
    vector_store = VectorStore()
    
    # Search for debt reduction strategies
    print("Searching for: 'strategies to reduce credit card debt'\n")
    
    results = vector_store.search(
        query="strategies to reduce credit card debt",
        top_k=3,
    )
    
    print(f"Found {len(results['ids'][0])} results:\n")
    
    for i, (doc_id, content, metadata, distance) in enumerate(zip(
        results['ids'][0],
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    ), 1):
        similarity = 1 / (1 + distance)
        print(f"{i}. [{doc_id}] (similarity: {similarity:.3f})")
        print(f"   Type: {metadata.get('type')}")
        print(f"   Content: {content[:150]}...")
        print()


async def example_3_generate_rag_recommendations():
    """Example 3: Generate RAG recommendations."""
    print("\n" + "="*80)
    print("EXAMPLE 3: Generate RAG Recommendations")
    print("="*80 + "\n")
    
    from app.rag import VectorStore, RAGRecommendationGenerator
    import uuid
    
    # Initialize
    vector_store = VectorStore()
    generator = RAGRecommendationGenerator(vector_store, use_openai=True)
    
    # Sample user data
    sample_user_id = uuid.uuid4()
    sample_personas = ["HIGH_UTILIZATION"]
    sample_signals_30d = {
        "credit": {
            "avg_utilization": 0.68,
            "total_credit_balance": 5200.00,
            "cards_with_interest": ["card_1"],
            "high_utilization_cards": ["card_1"],
        }
    }
    
    print(f"User ID: {sample_user_id}")
    print(f"Personas: {sample_personas}")
    print(f"Credit Utilization: 68%")
    print(f"Credit Card Balance: $5,200\n")
    
    # Generate recommendations
    print("Generating recommendations with RAG...\n")
    
    try:
        result = generator.generate_recommendations(
            user_id=sample_user_id,
            personas=sample_personas,
            signals_30d=sample_signals_30d,
            signals_180d={},
            education_count=3,
            partner_offer_count=2,
        )
        
        if result.get("success"):
            print(f"✅ Generated {result['total_recommendations']} recommendations in {result['generation_time_ms']:.0f}ms")
            print(f"   - Education: {len(result.get('education_recommendations', []))}")
            print(f"   - Partners: {len(result.get('partner_offers', []))}")
            print(f"   - Context used: {result['context_used']['documents_retrieved']} documents\n")
            
            # Show first education recommendation
            if result.get('education_recommendations'):
                rec = result['education_recommendations'][0]
                print("Sample Education Recommendation:")
                print(f"  Title: {rec.get('title')}")
                print(f"  Priority: {rec.get('priority')}")
                print(f"  Rationale: {rec.get('rationale', '')[:200]}...")
                print()
        else:
            print(f"❌ Generation failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Note: OpenAI API key required for generation. Set OPENAI_API_KEY environment variable.")


async def example_4_integrated_generator():
    """Example 4: Use integrated generator with fallback."""
    print("\n" + "="*80)
    print("EXAMPLE 4: Integrated Generator with Fallback")
    print("="*80 + "\n")
    
    from app.recommendations.rag_integration import EnhancedRecommendationGenerator
    import uuid
    
    # Note: This requires database session
    print("This example requires database connection.")
    print("It demonstrates how to use the integrated generator that supports:")
    print("  - RAG generation (when enabled)")
    print("  - Automatic fallback to catalog")
    print("  - A/B testing support")
    print()
    
    print("Example usage:")
    print("""
    from sqlalchemy.orm import Session
    from app.recommendations.rag_integration import EnhancedRecommendationGenerator
    
    # Create generator
    generator = EnhancedRecommendationGenerator(
        db_session=db,
        use_rag=True,  # Enable RAG
        use_openai=True
    )
    
    # Generate recommendations
    result = generator.generate_recommendations(
        user_id=user_id,
        # Personas and signals fetched automatically if not provided
    )
    
    # Result includes generation method
    print(f"Generated with: {result.get('generation_method')}")  # "rag" or "catalog"
    """)


async def example_5_query_engine():
    """Example 5: Use query engine for smart retrieval."""
    print("\n" + "="*80)
    print("EXAMPLE 5: Query Engine for Smart Retrieval")
    print("="*80 + "\n")
    
    from app.rag import VectorStore, QueryEngine
    
    vector_store = VectorStore()
    query_engine = QueryEngine(vector_store)
    
    # Sample user profile
    personas = ["HIGH_UTILIZATION"]
    signals_30d = {
        "credit": {
            "avg_utilization": 0.72,
            "cards_with_interest": ["card_1", "card_2"],
            "minimum_payment_only_cards": ["card_1"],
        }
    }
    
    print("User Profile:")
    print(f"  Personas: {personas}")
    print(f"  Credit Utilization: 72%")
    print(f"  Paying interest on 2 cards")
    print(f"  Making minimum payments only on 1 card\n")
    
    # Generate query
    query = query_engine.generate_query_from_profile(
        personas=personas,
        signals_30d=signals_30d,
    )
    
    print(f"Generated Query:\n  '{query}'\n")
    
    # Retrieve context
    context = query_engine.retrieve_context(
        query=query,
        personas=personas,
        top_k=5,
    )
    
    print(f"Retrieved {context['retrieved_count']} relevant documents:\n")
    
    for doc in context['documents'][:3]:
        print(f"  - [{doc['id']}] (similarity: {doc['similarity']:.3f})")
        print(f"    Type: {doc['metadata'].get('type')}")
        print(f"    {doc['content'][:100]}...")
        print()


async def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("RAG SYSTEM EXAMPLES")
    print("="*80)
    
    try:
        # Example 1: Build knowledge base
        await example_1_build_knowledge_base()
        
        # Example 2: Search knowledge base
        await example_2_search_knowledge_base()
        
        # Example 3: Generate recommendations (requires OpenAI)
        # Uncomment if you have OpenAI API key set
        # await example_3_generate_rag_recommendations()
        
        # Example 4: Integrated generator
        await example_4_integrated_generator()
        
        # Example 5: Query engine
        await example_5_query_engine()
        
        print("\n" + "="*80)
        print("✅ Examples complete!")
        print("="*80 + "\n")
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Please install dependencies: pip install -r requirements.txt")
    except Exception as e:
        logger.error(f"Error running examples: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())

