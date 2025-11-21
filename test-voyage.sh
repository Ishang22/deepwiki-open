#!/bin/bash

# Test script for Voyage AI embedder integration
# This script tests the Voyage AI client to ensure it's properly configured

set -e

echo "=========================================="
echo "Voyage AI Integration Test for DeepWiki"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if VOYAGE_API_KEY is set
if [ -z "$VOYAGE_API_KEY" ]; then
    echo -e "${RED}ERROR: VOYAGE_API_KEY environment variable is not set${NC}"
    echo "Please set it with: export VOYAGE_API_KEY='your-api-key-here'"
    exit 1
fi

echo -e "${GREEN}✓ VOYAGE_API_KEY is set${NC}"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: python3 is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python 3 is available${NC}"
echo ""

# Create a temporary test script
cat > /tmp/test_voyage.py << 'EOF'
#!/usr/bin/env python3
"""
Test script for Voyage AI embedder integration
"""

import os
import sys

# Add the api directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

try:
    from api.voyage_client import VoyageClient
    from api.config import configs
    import logging
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    print("=" * 50)
    print("Testing Voyage AI Client")
    print("=" * 50)
    print()
    
    # Check if API key is set
    api_key = os.environ.get('VOYAGE_API_KEY')
    if not api_key:
        print("❌ ERROR: VOYAGE_API_KEY not found in environment")
        sys.exit(1)
    
    print("✓ API Key found (length: {})".format(len(api_key)))
    print()
    
    # Initialize client
    print("Initializing Voyage AI client...")
    client = VoyageClient()
    print("✓ Client initialized successfully")
    print()
    
    # Test single text embedding
    print("Testing single text embedding...")
    test_text = "Hello, this is a test of Voyage AI embeddings"
    
    api_kwargs = {
        "input": test_text,
        "model": "voyage-3-large"
    }
    
    result = client.call(api_kwargs)
    
    if result.error:
        print(f"❌ ERROR: {result.error}")
        sys.exit(1)
    
    if result.data and len(result.data) > 0:
        embedding = result.data[0].embedding
        print(f"✓ Embedding generated successfully")
        print(f"  - Embedding dimensions: {len(embedding)}")
        print(f"  - First 5 values: {embedding[:5]}")
        print()
    else:
        print("❌ ERROR: No embedding data returned")
        sys.exit(1)
    
    # Test batch embedding
    print("Testing batch text embedding...")
    test_texts = [
        "First test sentence",
        "Second test sentence",
        "Third test sentence"
    ]
    
    api_kwargs = {
        "input": test_texts,
        "model": "voyage-3-large"
    }
    
    result = client.call(api_kwargs)
    
    if result.error:
        print(f"❌ ERROR: {result.error}")
        sys.exit(1)
    
    if result.data and len(result.data) == len(test_texts):
        print(f"✓ Batch embeddings generated successfully")
        print(f"  - Number of embeddings: {len(result.data)}")
        for i, emb_obj in enumerate(result.data):
            print(f"  - Text {i+1}: {len(emb_obj.embedding)} dimensions")
        print()
    else:
        print(f"❌ ERROR: Expected {len(test_texts)} embeddings, got {len(result.data) if result.data else 0}")
        sys.exit(1)
    
    # Test with different model (voyage-code-3 for code)
    print("Testing with voyage-code-3 model...")
    code_text = "def hello_world():\n    print('Hello, World!')"
    
    api_kwargs = {
        "input": code_text,
        "model": "voyage-code-3"
    }
    
    result = client.call(api_kwargs)
    
    if result.error:
        print(f"⚠️  Warning: voyage-code-3 test failed: {result.error}")
        print(f"   (This is OK if you don't have access to this model)")
    elif result.data and len(result.data) > 0:
        print(f"✓ voyage-code-3 model working")
        print(f"  - Embedding dimensions: {len(result.data[0].embedding)}")
    print()
    
    # Summary
    print("=" * 50)
    print("✅ All core tests passed!")
    print("=" * 50)
    print()
    print("Voyage AI integration is working correctly.")
    print("You can now use Voyage AI embeddings in DeepWiki.")
    print()
    print("To use Voyage AI as your embedder, set:")
    print("  export DEEPWIKI_EMBEDDER_TYPE='voyage'")
    print()
    
except ImportError as e:
    print(f"❌ ERROR: Failed to import required modules: {e}")
    print("Make sure you're running this from the DeepWiki root directory")
    sys.exit(1)
except Exception as e:
    print(f"❌ ERROR: Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

# Change to the api directory and run the test
cd "$(dirname "$0")"

echo "Running Voyage AI integration tests..."
echo ""

python3 /tmp/test_voyage.py

# Cleanup
rm -f /tmp/test_voyage.py

echo ""
echo -e "${GREEN}Test completed successfully!${NC}"
echo ""
echo "Next steps:"
echo "1. Set DEEPWIKI_EMBEDDER_TYPE to use Voyage AI:"
echo "   export DEEPWIKI_EMBEDDER_TYPE='voyage'"
echo ""
echo "2. Restart DeepWiki:"
echo "   ./restart-deepwiki.sh"
echo ""
echo "3. Check the logs to confirm Voyage AI is being used"
echo ""

