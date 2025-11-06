"""Test script for VectorStore functionality."""

import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_vector_store():
    """Test VectorStore basic functionality."""
    
    try:
        from app.rag.vector_store import VectorStore
        from app.rag.config import RAGConfig
        
        logger.info("=" * 80)
        logger.info("Testing VectorStore Implementation")
        logger.info("=" * 80)
        
        # Create test config with temporary database
        test_config = RAGConfig(
            vector_db_path="./data/chroma_test",
            collection_name="test_collection",
            default_top_k=3,
        )
        
        # Test 1: Initialize VectorStore
        logger.info("\n[Test 1] Initializing VectorStore...")
        vector_store = VectorStore(config=test_config)
        logger.info(f"✓ VectorStore initialized: {vector_store.count()} documents")
        
        # Test 2: Add sample documents
        logger.info("\n[Test 2] Adding sample documents...")
        sample_docs = [
            {
                "id": "scenario_1",
                "content": "User with high credit card utilization (68%) on Visa ending in 4523. Balance $5,200, paying $87/month in interest charges. Making minimum payments only.",
                "type": "user_scenario",
                "persona": "HIGH_UTILIZATION",
                "feedback_rating": 5,
            },
            {
                "id": "scenario_2",
                "content": "Freelancer with variable income, receives payments every 45-60 days. Has low cash flow buffer (0.8 months). Needs help smoothing income.",
                "type": "user_scenario",
                "persona": "VARIABLE_INCOME_BUDGETER",
                "feedback_rating": 4,
            },
            {
                "id": "scenario_3",
                "content": "User with 8 active subscriptions totaling $127/month. Several subscriptions unused in last 30 days. Subscription spend is 15% of total spending.",
                "type": "user_scenario",
                "persona": "SUBSCRIPTION_HEAVY",
                "feedback_rating": 5,
            },
            {
                "id": "education_1",
                "content": "Credit utilization is the percentage of available credit you're using. Keeping utilization below 30% is ideal for credit score. Calculate: (balance / credit limit) × 100.",
                "type": "education_content",
                "topic": "credit_utilization",
                "persona_ids": [1, 5],
            },
            {
                "id": "education_2",
                "content": "Variable income budgeting requires a cash flow buffer. Aim for 1-2 months of essential expenses in a separate smoothing account. Build during high-income months.",
                "type": "education_content",
                "topic": "variable_income",
                "persona_ids": [2],
            },
            {
                "id": "operator_1",
                "content": "Rejected generic subscription advice for user with only 2 subscriptions. User needed debt paydown guidance instead. Approved debt consolidation recommendation.",
                "type": "operator_decision",
                "reasoning": "Prioritize high-interest debt over minor subscription optimization",
            },
        ]
        
        added_count = vector_store.add_documents(sample_docs)
        logger.info(f"✓ Added {added_count} documents")
        logger.info(f"  Total documents in store: {vector_store.count()}")
        
        # Test 3: Search for relevant documents
        logger.info("\n[Test 3] Searching for relevant documents...")
        
        # Test query 1: High credit utilization
        query1 = "high credit card usage and interest charges"
        logger.info(f"\nQuery: '{query1}'")
        results1 = vector_store.search(query=query1, top_k=3)
        
        logger.info(f"Found {len(results1['ids'][0])} results:")
        for i, (doc_id, content, metadata, distance) in enumerate(zip(
            results1['ids'][0],
            results1['documents'][0],
            results1['metadatas'][0],
            results1['distances'][0]
        ), 1):
            similarity = 1 / (1 + distance)
            logger.info(f"  {i}. [{doc_id}] (similarity: {similarity:.3f})")
            logger.info(f"     Type: {metadata.get('type')}")
            logger.info(f"     Content: {content[:100]}...")
        
        # Test query 2: Variable income
        query2 = "irregular income and budgeting challenges"
        logger.info(f"\nQuery: '{query2}'")
        results2 = vector_store.search(query=query2, top_k=3)
        
        logger.info(f"Found {len(results2['ids'][0])} results:")
        for i, (doc_id, content, metadata, distance) in enumerate(zip(
            results2['ids'][0],
            results2['documents'][0],
            results2['metadatas'][0],
            results2['distances'][0]
        ), 1):
            similarity = 1 / (1 + distance)
            logger.info(f"  {i}. [{doc_id}] (similarity: {similarity:.3f})")
            logger.info(f"     Type: {metadata.get('type')}")
            logger.info(f"     Content: {content[:100]}...")
        
        # Test 4: Search with filters
        logger.info("\n[Test 4] Searching with metadata filters...")
        query3 = "financial education"
        filters = {"type": "education_content"}
        logger.info(f"Query: '{query3}' with filter: {filters}")
        results3 = vector_store.search(query=query3, top_k=3, filters=filters)
        
        logger.info(f"Found {len(results3['ids'][0])} results (filtered by type):")
        for i, (doc_id, content, metadata) in enumerate(zip(
            results3['ids'][0],
            results3['documents'][0],
            results3['metadatas'][0]
        ), 1):
            logger.info(f"  {i}. [{doc_id}]")
            logger.info(f"     Topic: {metadata.get('topic')}")
            logger.info(f"     Content: {content[:100]}...")
        
        # Test 5: Get document by ID
        logger.info("\n[Test 5] Retrieving document by ID...")
        doc = vector_store.search_by_id("scenario_1")
        if doc:
            logger.info(f"✓ Retrieved document: {doc['id']}")
            logger.info(f"  Content: {doc['content'][:100]}...")
        
        # Test 6: Update document
        logger.info("\n[Test 6] Updating document...")
        success = vector_store.update_document(
            doc_id="scenario_1",
            content="UPDATED: User with high credit card utilization, now at 72% after additional charges.",
            metadata={"type": "user_scenario", "persona": "HIGH_UTILIZATION", "feedback_rating": 5, "updated": True}
        )
        if success:
            updated_doc = vector_store.search_by_id("scenario_1")
            logger.info(f"✓ Document updated: {updated_doc['content'][:80]}...")
        
        # Test 7: Get statistics
        logger.info("\n[Test 7] Getting vector store statistics...")
        stats = vector_store.get_stats()
        logger.info("✓ Vector store statistics:")
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")
        
        # Test 8: Delete documents
        logger.info("\n[Test 8] Deleting test document...")
        deleted_count = vector_store.delete_documents(["operator_1"])
        logger.info(f"✓ Deleted {deleted_count} documents")
        logger.info(f"  Remaining documents: {vector_store.count()}")
        
        # Test 9: Clear collection (cleanup)
        logger.info("\n[Test 9] Clearing test collection...")
        vector_store.clear()
        logger.info(f"✓ Collection cleared: {vector_store.count()} documents remaining")
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ All tests passed!")
        logger.info("=" * 80)
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("Please install dependencies: pip install chromadb sentence-transformers")
        return False
    
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = test_vector_store()
    sys.exit(0 if success else 1)

