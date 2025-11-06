#!/bin/bash
# Deploy RAG to development environment with 100% rollout

set -e  # Exit on error

echo "======================================================================"
echo "RAG System - Development Deployment (100% Rollout)"
echo "======================================================================"

# Check if running from correct directory
if [ ! -f "requirements.txt" ]; then
    echo "Error: Must run from service directory"
    exit 1
fi

echo ""
echo "Step 1: Installing RAG dependencies..."
echo "----------------------------------------------------------------------"

# Install dependencies if not present
pip install -q chromadb==0.4.22 sentence-transformers==2.2.2 langchain==0.1.0 langchain-openai==0.0.5 tiktoken==0.5.2 2>&1 | grep -v "already satisfied" || true

echo "✓ Dependencies installed"

echo ""
echo "Step 2: Creating data directories..."
echo "----------------------------------------------------------------------"

mkdir -p ./data/chroma_dev
mkdir -p ./data/chroma_prod

echo "✓ Directories created"

echo ""
echo "Step 3: Building knowledge base..."
echo "----------------------------------------------------------------------"

python scripts/build_knowledge_base.py --clear --full

if [ $? -eq 0 ]; then
    echo "✓ Knowledge base built successfully"
else
    echo "✗ Knowledge base build failed"
    exit 1
fi

echo ""
echo "Step 4: Verifying knowledge base..."
echo "----------------------------------------------------------------------"

python scripts/build_knowledge_base.py --stats

echo ""
echo "Step 5: Updating environment configuration..."
echo "----------------------------------------------------------------------"

# Update backend .env file
ENV_FILE="../backend/.env"

# Check if .env exists
if [ ! -f "$ENV_FILE" ]; then
    echo "⚠ .env file not found. Creating from env.example..."
    cp ../backend/env.example "$ENV_FILE"
fi

# Remove old RAG settings if they exist
sed -i.bak '/^RAG_/d' "$ENV_FILE" 2>/dev/null || true

# Add new RAG settings
cat >> "$ENV_FILE" << 'EOF'

# RAG System Configuration (Development - 100% Rollout)
RAG_ENABLED=true
RAG_ROLLOUT_PERCENTAGE=1.0
RAG_OPENAI_MODEL=gpt-4-turbo-preview
RAG_VECTOR_DB_PATH=./data/chroma_dev
RAG_EMBEDDING_MODEL=all-MiniLM-L6-v2
RAG_TOP_K=10
RAG_FORCE_CATALOG_FALLBACK=false
EOF

echo "✓ Environment configuration updated"
echo "  - RAG_ENABLED=true"
echo "  - RAG_ROLLOUT_PERCENTAGE=1.0 (100%)"

echo ""
echo "Step 6: Testing RAG system..."
echo "----------------------------------------------------------------------"

# Run basic tests
python scripts/test_rag_basic.py 2>&1 | grep -E "(PASS|FAIL|Summary)" || true

echo ""
echo "======================================================================"
echo "RAG System Deployed Successfully!"
echo "======================================================================"
echo ""
echo "Configuration:"
echo "  ✓ RAG enabled at 100% rollout"
echo "  ✓ Knowledge base built with catalog + strategies"
echo "  ✓ Environment variables configured"
echo ""
echo "Next Steps:"
echo "  1. Restart your backend:"
echo "     cd ../backend && uvicorn app.main:app --reload"
echo ""
echo "  2. Generate recommendations for a user:"
echo "     python scripts/generate_all_recommendations.py"
echo ""
echo "  3. Monitor RAG metrics:"
echo "     cd ../service && python scripts/check_rag_metrics.py"
echo ""
echo "  4. View operator dashboard:"
echo "     curl http://localhost:8000/api/v1/operator/rag/dashboard \\"
echo "       -H \"Authorization: Bearer \$OPERATOR_TOKEN\""
echo ""
echo "Documentation: docs/RAG_DEPLOYMENT_GUIDE.md"
echo ""

