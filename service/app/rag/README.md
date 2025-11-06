# RAG System Quick Start

**Version**: 1.0
**Date**: 2025-11-05

---

## Quick Start

### 1. Install Dependencies
```bash
cd service
pip install -r requirements.txt
```

### 2. Build Knowledge Base
```bash
# Build from catalog only (no database needed)
python scripts/build_knowledge_base.py --full

# Expected output:
# Education Content:     15
# Partner Offers:         6
# Financial Strategies:  10
# TOTAL DOCUMENTS:       31
```

### 3. Test Search
```bash
# Query the knowledge base
python scripts/build_knowledge_base.py --query "high credit utilization" --top-k 5

# Query with filters
python -c "
from app.rag import VectorStore
vs = VectorStore()
results = vs.search(
    query='debt payoff strategies',
    top_k=3,
    filters={'type': 'financial_strategy'}
)
print(f'Found {len(results[\"ids\"][0])} results')
"
```

### 4. Get Statistics
```bash
python scripts/build_knowledge_base.py --stats
```

---

## Components

### 1. VectorStore (`vector_store.py`)
Vector database interface using ChromaDB.

```python
from app.rag import VectorStore

# Initialize
vector_store = VectorStore()

# Add documents
vector_store.add_documents([{
    "id": "doc_1",
    "content": "Financial advice about...",
    "type": "education",
    "tags": ["credit", "debt"]
}])

# Search
results = vector_store.search(
    query="credit card advice",
    top_k=5,
    filters={"type": "education"}
)
```

### 2. KnowledgeBaseBuilder (`knowledge_builder.py`)
Ingests data from multiple sources into vector store.

```python
from sqlalchemy.orm import Session
from app.rag import VectorStore
from app.rag.knowledge_builder import KnowledgeBaseBuilder

vector_store = VectorStore()
builder = KnowledgeBaseBuilder(db_session, vector_store)

# Build knowledge base
stats = await builder.build_full_knowledge_base()
print(f"Built {stats['total_documents']} documents")
```

### 3. Document Schemas (`document_schemas.py`)
Structured document types for knowledge base.

```python
from app.rag.document_schemas import (
    UserScenarioDocument,
    EducationContentDocument,
    FinancialStrategyDocument
)
```

### 4. Configuration (`config.py`)
Configuration management.

```python
from app.rag.config import RAGConfig

# From environment
config = RAGConfig.from_env()

# Custom config
config = RAGConfig(
    vector_db_path="./data/chroma",
    embedding_model="all-MiniLM-L6-v2",
    default_top_k=5
)
```

---

## Knowledge Base Contents

### Document Types
1. **User Scenarios** - Successful cases with feedback
2. **Education Content** - 15 education catalog items
3. **Partner Offers** - 6 partner offers
4. **Financial Strategies** - 10 curated best practices
5. **Operator Decisions** - Learning from overrides

### Financial Strategies Included
1. Debt Snowball Method
2. Debt Avalanche Method
3. Balance Transfer Strategy
4. Variable Income Buffer
5. 50/30/20 Budget Rule
6. Subscription Audit Process
7. Emergency Fund Building
8. High-Yield Savings Optimization
9. Automated Savings Strategy
10. Credit Utilization Management

---

## Configuration

### Environment Variables
```bash
# Vector database
export RAG_VECTOR_DB_PATH="./data/chroma"
export RAG_COLLECTION_NAME="financial_knowledge"

# Embeddings
export RAG_EMBEDDING_MODEL="all-MiniLM-L6-v2"

# Retrieval
export RAG_DEFAULT_TOP_K="5"
export RAG_SIMILARITY_THRESHOLD="0.5"

# OpenAI
export RAG_OPENAI_MODEL="gpt-4-turbo-preview"
export RAG_OPENAI_TEMPERATURE="0.7"

# Feature flags
export RAG_ENABLE="false"  # Enable RAG mode
export RAG_ENABLE_CACHING="true"
export RAG_ENABLE_LOGGING="true"
```

---

## Testing

### Test Vector Store
```bash
python -m app.rag.test_vector_store
```

### Test Knowledge Base Build
```bash
python scripts/build_knowledge_base.py --full --test-query "debt reduction"
```

### Manual Testing
```python
from app.rag import VectorStore

# Initialize
vs = VectorStore()

# Test search
results = vs.search("credit card utilization", top_k=3)
print(f"Found {len(results['ids'][0])} results")

# Test stats
stats = vs.get_stats()
print(f"Total documents: {stats['total_documents']}")
```

---

## Performance

### Benchmarks (Expected)
- **Retrieval Speed**: <100ms per query
- **Embedding Speed**: ~50ms per document
- **Build Time**: ~5-10 seconds for 100 documents
- **Storage**: ~1MB per 100 documents

### Scalability
- **Current**: 31+ documents (catalog + strategies)
- **Target**: 100+ documents (with user scenarios)
- **Max**: 10,000+ documents (ChromaDB limit)

---

## Next Steps

### Week 1 (Remaining)
- [ ] Build QueryEngine for smart retrieval
- [ ] Implement RAGRecommendationGenerator
- [ ] Integrate with existing system

### Week 2
- [ ] A/B testing framework
- [ ] Gradual rollout (10% → 50%)
- [ ] Performance optimization

### Week 3
- [ ] Production deployment
- [ ] Monitoring and alerting
- [ ] Documentation and training

---

## Troubleshooting

### Issue: "ChromaDB not installed"
```bash
pip install chromadb sentence-transformers
```

### Issue: "No documents in collection"
```bash
# Build knowledge base
python scripts/build_knowledge_base.py --full
```

### Issue: "Slow retrieval"
```bash
# Check embedding model size
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
print(f'Dimension: {model.get_sentence_embedding_dimension()}')
"

# Use smaller model if needed
export RAG_EMBEDDING_MODEL="all-MiniLM-L6-v2"
```

### Issue: "Out of memory"
```bash
# Reduce batch size
export RAG_BATCH_SIZE="16"
```

---

## Architecture

```
User Query
    ↓
Query Engine
    ↓
Vector Store (ChromaDB)
    ↓
Retrieved Context (top-5 documents)
    ↓
RAG Generator (LLM + Context)
    ↓
Personalized Recommendation
```

---

## Resources

- [ChromaDB Docs](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [RAG Implementation Plan](../../docs/RAG_IMPLEMENTATION_PLAN.md)
- [AI Enhancement Plan](../../docs/AI_ENHANCEMENT_PLAN.md)

---

## Support

- **Questions**: See [RAG_IMPLEMENTATION_PLAN.md](../../docs/RAG_IMPLEMENTATION_PLAN.md)
- **Issues**: Check [RAG_PROGRESS_REPORT.md](../../docs/RAG_PROGRESS_REPORT.md)
- **Architecture**: See [AI_ENHANCEMENT_PLAN.md](../../docs/AI_ENHANCEMENT_PLAN.md)

---

**Version**: 1.0 (Phase 1 Complete)  
**Last Updated**: 2025-11-05

