"""Comprehensive test suite for RAG recommendation system."""

import pytest
import asyncio
import uuid
from typing import Dict, Any, List

# Import RAG components
from app.rag import VectorStore, RAGConfig, RAGRecommendationGenerator, KnowledgeBaseBuilder


class TestVectorStore:
    """Test suite for VectorStore functionality."""
    
    @pytest.fixture
    def vector_store(self):
        """Create a test vector store."""
        config = RAGConfig(
            vector_db_path="./data/chroma_test",
            collection_name="test_collection",
        )
        vs = VectorStore(config=config)
        yield vs
        # Cleanup
        vs.clear()
    
    def test_vector_store_initialization(self, vector_store):
        """Test that vector store initializes correctly."""
        assert vector_store is not None
        assert vector_store.count() >= 0
    
    def test_add_documents(self, vector_store):
        """Test adding documents to vector store."""
        docs = [
            {
                "id": "test_1",
                "content": "High credit card utilization requires debt paydown strategies.",
                "type": "test",
            },
            {
                "id": "test_2",
                "content": "Variable income requires cash flow buffer for stability.",
                "type": "test",
            }
        ]
        
        count = vector_store.add_documents(docs)
        assert count == 2
        assert vector_store.count() >= 2
    
    def test_search_documents(self, vector_store):
        """Test semantic search functionality."""
        # Add test documents
        docs = [
            {
                "id": "test_credit",
                "content": "High credit utilization debt strategies",
                "type": "education",
            },
            {
                "id": "test_savings",
                "content": "Emergency fund savings strategies",
                "type": "education",
            }
        ]
        vector_store.add_documents(docs)
        
        # Search for credit-related content
        results = vector_store.search("credit card debt", top_k=2)
        
        assert len(results["ids"][0]) > 0
        assert "test_credit" in results["ids"][0]
    
    def test_search_with_filters(self, vector_store):
        """Test search with metadata filters."""
        docs = [
            {"id": "edu_1", "content": "Education content", "type": "education"},
            {"id": "strat_1", "content": "Strategy content", "type": "strategy"},
        ]
        vector_store.add_documents(docs)
        
        results = vector_store.search(
            "content",
            top_k=5,
            filters={"type": "education"}
        )
        
        # Should only return education documents
        assert all(meta.get("type") == "education" for meta in results["metadatas"][0])
    
    def test_document_retrieval_by_id(self, vector_store):
        """Test retrieving document by ID."""
        doc = {
            "id": "retrieve_test",
            "content": "Test content for retrieval",
            "type": "test",
        }
        vector_store.add_documents([doc])
        
        retrieved = vector_store.search_by_id("retrieve_test")
        assert retrieved is not None
        assert retrieved["id"] == "retrieve_test"
        assert retrieved["content"] == doc["content"]
    
    def test_document_update(self, vector_store):
        """Test updating a document."""
        # Add initial document
        vector_store.add_documents([{
            "id": "update_test",
            "content": "Original content",
            "type": "test",
        }])
        
        # Update it
        success = vector_store.update_document(
            "update_test",
            "Updated content",
            {"type": "test", "updated": True}
        )
        
        assert success
        
        # Verify update
        retrieved = vector_store.search_by_id("update_test")
        assert retrieved["content"] == "Updated content"
        assert retrieved["metadata"]["updated"] is True
    
    def test_document_deletion(self, vector_store):
        """Test deleting documents."""
        vector_store.add_documents([{
            "id": "delete_test",
            "content": "To be deleted",
            "type": "test",
        }])
        
        initial_count = vector_store.count()
        deleted = vector_store.delete_documents(["delete_test"])
        
        assert deleted == 1
        assert vector_store.count() == initial_count - 1
    
    def test_get_stats(self, vector_store):
        """Test getting vector store statistics."""
        # Add some documents
        vector_store.add_documents([
            {"id": "stat_1", "content": "Test 1", "type": "education"},
            {"id": "stat_2", "content": "Test 2", "type": "strategy"},
        ])
        
        stats = vector_store.get_stats()
        
        assert "total_documents" in stats
        assert stats["total_documents"] >= 2
        assert "embedding_model" in stats
        assert "document_types" in stats


class TestKnowledgeBase:
    """Test suite for knowledge base building."""
    
    @pytest.fixture
    def knowledge_base(self):
        """Create test knowledge base."""
        config = RAGConfig(
            vector_db_path="./data/chroma_test_kb",
            collection_name="test_kb",
        )
        vs = VectorStore(config=config)
        builder = KnowledgeBaseBuilder(None, vs)
        yield vs, builder
        # Cleanup
        vs.clear()
    
    @pytest.mark.asyncio
    async def test_build_education_catalog(self, knowledge_base):
        """Test building education catalog."""
        vs, builder = knowledge_base
        
        count = await builder.ingest_education_content()
        
        assert count > 0  # Should have education items
        assert vs.count() >= count
    
    @pytest.mark.asyncio
    async def test_build_partner_offers(self, knowledge_base):
        """Test building partner offer catalog."""
        vs, builder = knowledge_base
        
        count = await builder.ingest_partner_offers()
        
        assert count > 0  # Should have partner offers
        assert vs.count() >= count
    
    @pytest.mark.asyncio
    async def test_build_financial_strategies(self, knowledge_base):
        """Test building financial strategies."""
        vs, builder = knowledge_base
        
        count = await builder.ingest_financial_strategies()
        
        assert count == 10  # Should have 10 strategies
        assert vs.count() >= 10
    
    @pytest.mark.asyncio
    async def test_build_full_knowledge_base(self, knowledge_base):
        """Test building complete knowledge base."""
        vs, builder = knowledge_base
        
        stats = await builder.build_full_knowledge_base(clear_existing=True)
        
        assert stats["total_documents"] > 0
        assert stats["education_content"] > 0
        assert stats["partner_offers"] > 0
        assert stats["financial_strategies"] == 10


class TestRAGGeneration:
    """Test suite for RAG recommendation generation."""
    
    @pytest.fixture
    async def setup_rag(self):
        """Set up RAG system for testing."""
        config = RAGConfig(
            vector_db_path="./data/chroma_test_rag",
            collection_name="test_rag",
        )
        vs = VectorStore(config=config)
        
        # Build knowledge base
        builder = KnowledgeBaseBuilder(None, vs)
        await builder.build_full_knowledge_base(clear_existing=True)
        
        # Create generator (without OpenAI for most tests)
        generator = RAGRecommendationGenerator(vs, use_openai=False)
        
        yield vs, generator
        
        # Cleanup
        vs.clear()
    
    @pytest.mark.asyncio
    async def test_query_generation(self, setup_rag):
        """Test query generation from user profile."""
        vs, generator = await setup_rag
        
        query = generator.query_engine.generate_query_from_profile(
            personas=["HIGH_UTILIZATION"],
            signals_30d={
                "credit": {
                    "avg_utilization": 0.68,
                    "cards_with_interest": ["card_1"],
                }
            }
        )
        
        assert query is not None
        assert len(query) > 0
        assert "utilization" in query.lower() or "credit" in query.lower()
    
    @pytest.mark.asyncio
    async def test_context_retrieval(self, setup_rag):
        """Test retrieving relevant context."""
        vs, generator = await setup_rag
        
        context = generator.query_engine.retrieve_context(
            query="high credit card utilization debt strategies",
            personas=["HIGH_UTILIZATION"],
            top_k=5
        )
        
        assert context["retrieved_count"] > 0
        assert len(context["documents"]) > 0
        
        # Check that documents have required fields
        for doc in context["documents"]:
            assert "id" in doc
            assert "content" in doc
            assert "similarity" in doc
    
    @pytest.mark.asyncio
    async def test_similar_scenario_retrieval(self, setup_rag):
        """Test finding similar user scenarios."""
        vs, generator = await setup_rag
        
        # Add a test scenario
        vs.add_documents([{
            "id": "scenario_test",
            "content": "User with 70% credit utilization successfully reduced debt",
            "type": "user_scenario",
            "persona": "HIGH_UTILIZATION",
        }])
        
        scenarios = generator.query_engine.retrieve_similar_scenarios(
            signals_30d={"credit": {"avg_utilization": 0.68}},
            personas=["HIGH_UTILIZATION"],
            top_k=3
        )
        
        # Should find our test scenario
        assert len(scenarios) > 0
    
    @pytest.mark.asyncio
    async def test_category_retrieval(self, setup_rag):
        """Test retrieving by category."""
        vs, generator = await setup_rag
        
        docs = generator.query_engine.retrieve_by_category(
            category="debt",
            personas=["HIGH_UTILIZATION"],
            top_k=5
        )
        
        assert len(docs) > 0
        # Should retrieve debt-related content
        assert any("debt" in doc["content"].lower() for doc in docs)


class TestRAGQuality:
    """Test suite for RAG output quality."""
    
    def test_query_contains_user_data(self):
        """Test that queries cite specific user data."""
        from app.rag import QueryEngine, VectorStore
        
        config = RAGConfig(
            vector_db_path="./data/chroma_test_quality",
            collection_name="test_quality",
        )
        vs = VectorStore(config=config)
        query_engine = QueryEngine(vs)
        
        query = query_engine.generate_query_from_profile(
            personas=["HIGH_UTILIZATION"],
            signals_30d={
                "credit": {
                    "avg_utilization": 0.68,
                    "total_credit_balance": 5200,
                }
            }
        )
        
        # Query should mention utilization
        assert any(term in query.lower() for term in ["utilization", "credit", "68"])
    
    def test_retrieval_relevance(self):
        """Test that retrieved documents are relevant to query."""
        from app.rag import VectorStore, QueryEngine
        
        config = RAGConfig(
            vector_db_path="./data/chroma_test_relevance",
            collection_name="test_relevance",
        )
        vs = VectorStore(config=config)
        
        # Add test documents
        vs.add_documents([
            {
                "id": "debt_doc",
                "content": "Strategies for reducing credit card debt and high utilization",
                "type": "education",
            },
            {
                "id": "savings_doc",
                "content": "How to build emergency fund savings",
                "type": "education",
            }
        ])
        
        query_engine = QueryEngine(vs)
        results = query_engine.retrieve_context(
            query="credit card debt reduction strategies",
            top_k=2
        )
        
        # First result should be the debt document
        assert results["documents"][0]["id"] == "debt_doc"
        assert results["documents"][0]["similarity"] > 0.5
        
        vs.clear()


class TestPerformance:
    """Test suite for performance benchmarks."""
    
    @pytest.mark.asyncio
    async def test_retrieval_speed(self):
        """Test that retrieval is fast (<100ms)."""
        import time
        from app.rag import VectorStore
        
        config = RAGConfig(
            vector_db_path="./data/chroma_test_perf",
            collection_name="test_perf",
        )
        vs = VectorStore(config=config)
        
        # Add test documents
        docs = [
            {"id": f"perf_{i}", "content": f"Test content {i}", "type": "test"}
            for i in range(50)
        ]
        vs.add_documents(docs)
        
        # Measure search time
        start = time.time()
        results = vs.search("test content", top_k=5)
        elapsed = (time.time() - start) * 1000  # ms
        
        assert elapsed < 100, f"Search took {elapsed:.2f}ms, expected <100ms"
        assert len(results["ids"][0]) > 0
        
        vs.clear()
    
    @pytest.mark.asyncio
    async def test_knowledge_base_build_time(self):
        """Test that knowledge base builds in reasonable time."""
        import time
        from app.rag import VectorStore, KnowledgeBaseBuilder
        
        config = RAGConfig(
            vector_db_path="./data/chroma_test_build",
            collection_name="test_build",
        )
        vs = VectorStore(config=config)
        builder = KnowledgeBaseBuilder(None, vs)
        
        # Measure build time
        start = time.time()
        stats = await builder.build_full_knowledge_base(clear_existing=True)
        elapsed = time.time() - start
        
        assert elapsed < 30, f"Build took {elapsed:.2f}s, expected <30s"
        assert stats["total_documents"] > 0
        
        vs.clear()


class TestIntegration:
    """Integration tests for the complete RAG system."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete RAG workflow from profile to recommendations."""
        from app.rag import VectorStore, RAGRecommendationGenerator, KnowledgeBaseBuilder
        
        config = RAGConfig(
            vector_db_path="./data/chroma_test_e2e",
            collection_name="test_e2e",
        )
        vs = VectorStore(config=config)
        
        # Build knowledge base
        builder = KnowledgeBaseBuilder(None, vs)
        stats = await builder.build_full_knowledge_base(clear_existing=True)
        assert stats["total_documents"] > 0
        
        # Create generator (without OpenAI for testing)
        generator = RAGRecommendationGenerator(vs, use_openai=False)
        
        # Test query generation
        query = generator.query_engine.generate_query_from_profile(
            personas=["HIGH_UTILIZATION"],
            signals_30d={"credit": {"avg_utilization": 0.68}}
        )
        assert len(query) > 0
        
        # Test retrieval
        context = generator.query_engine.retrieve_context(
            query=query,
            top_k=5
        )
        assert context["retrieved_count"] > 0
        
        # Cleanup
        vs.clear()


# Fixtures for all tests
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment."""
    import os
    os.makedirs("./data", exist_ok=True)
    yield
    # Cleanup handled by individual tests


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

