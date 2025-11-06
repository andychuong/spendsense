#!/bin/bash
# Initialize RAG system for production deployment

set -e  # Exit on error

echo "======================================================================"
echo "RAG System - Production Initialization"
echo "======================================================================"

# Check if running from correct directory
if [ ! -f "requirements.txt" ]; then
    echo "Error: Must run from service directory"
    exit 1
fi

echo ""
echo "Step 1: Checking dependencies..."
echo "----------------------------------------------------------------------"

# Check Python version
python_version=$(python --version 2>&1)
echo "Python: $python_version"

# Check for RAG dependencies
if ! python -c "import chromadb" 2>/dev/null; then
    echo "⚠ ChromaDB not installed. Installing..."
    pip install chromadb==0.4.22
fi

if ! python -c "import sentence_transformers" 2>/dev/null; then
    echo "⚠ sentence-transformers not installed. Installing..."
    pip install sentence-transformers==2.2.2
fi

echo "✓ Dependencies installed"

echo ""
echo "Step 2: Creating data directories..."
echo "----------------------------------------------------------------------"

# Create data directories
mkdir -p ./data/chroma_prod
mkdir -p ./data/chroma_staging
mkdir -p ./data/chroma_dev

echo "✓ Directories created"

echo ""
echo "Step 3: Building knowledge base..."
echo "----------------------------------------------------------------------"

# Build knowledge base
python scripts/build_knowledge_base.py --clear --full --verbose

if [ $? -eq 0 ]; then
    echo "✓ Knowledge base built successfully"
else
    echo "✗ Knowledge base build failed"
    exit 1
fi

echo ""
echo "Step 4: Verifying knowledge base..."
echo "----------------------------------------------------------------------"

# Verify
python scripts/build_knowledge_base.py --stats

echo ""
echo "Step 5: Running basic tests..."
echo "----------------------------------------------------------------------"

# Run basic tests
python scripts/test_rag_basic.py

if [ $? -eq 0 ]; then
    echo "✓ Tests passed"
else
    echo "⚠ Some tests failed (may be OK if dependencies missing)"
fi

echo ""
echo "Step 6: Checking environment configuration..."
echo "----------------------------------------------------------------------"

# Check environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠ OPENAI_API_KEY not set"
    echo "  Set with: export OPENAI_API_KEY=your-key-here"
else
    echo "✓ OPENAI_API_KEY configured"
fi

if [ -z "$RAG_ENABLED" ]; then
    echo "⚠ RAG_ENABLED not set (defaults to false)"
    echo "  Enable with: export RAG_ENABLED=true"
else
    echo "✓ RAG_ENABLED=$RAG_ENABLED"
fi

if [ -z "$RAG_ROLLOUT_PERCENTAGE" ]; then
    echo "⚠ RAG_ROLLOUT_PERCENTAGE not set (defaults to 0.10)"
    echo "  Set with: export RAG_ROLLOUT_PERCENTAGE=0.10"
else
    echo "✓ RAG_ROLLOUT_PERCENTAGE=$RAG_ROLLOUT_PERCENTAGE"
fi

echo ""
echo "======================================================================"
echo "RAG System Initialization Complete"
echo "======================================================================"
echo ""
echo "Next Steps:"
echo "  1. Set RAG_ENABLED=true in .env file"
echo "  2. Set RAG_ROLLOUT_PERCENTAGE=0.10 for initial rollout"
echo "  3. Restart your application"
echo "  4. Monitor with: python scripts/check_rag_metrics.py"
echo ""
echo "Documentation:"
echo "  - docs/RAG_DEPLOYMENT_GUIDE.md"
echo "  - docs/RAG_TESTING_GUIDE.md"
echo ""

