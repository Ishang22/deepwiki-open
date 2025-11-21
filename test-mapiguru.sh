#!/bin/bash
# Quick test script for MapiGuru embeddings

echo "🧪 Testing MapiGuru API Connection..."
echo ""

# Test 1: Check if MapiGuru API is accessible
echo "1️⃣ Testing API accessibility..."
if curl -s --connect-timeout 5 "https://chat.mapiguru.yo-digital.com/embeddings/getEmbeddingModels" > /dev/null; then
    echo "   ✅ MapiGuru API is accessible!"
else
    echo "   ❌ Cannot reach MapiGuru API"
    echo "   💡 Check your VPN/network connection"
    exit 1
fi

echo ""

# Test 2: Try to get embedding models
echo "2️⃣ Fetching available models..."
MODELS=$(curl -s "https://chat.mapiguru.yo-digital.com/embeddings/getEmbeddingModels")
echo "   Response: $MODELS"
echo ""

# Test 3: Try to generate an embedding
echo "3️⃣ Testing embedding generation..."
RESPONSE=$(curl -s -X POST "https://chat.mapiguru.yo-digital.com/embeddings/extract" \
  -H "Content-Type: application/json" \
  -d '{"text": "Test embedding", "model": "sentence-transformers/all-MiniLM-L6-v2"}')

if echo "$RESPONSE" | grep -q "embedding\|embeddings\|data"; then
    echo "   ✅ Embedding generation works!"
    echo "   Response preview: ${RESPONSE:0:100}..."
else
    echo "   ⚠️  Unexpected response format"
    echo "   Response: $RESPONSE"
    echo "   💡 May need to update mapiguru_client.py"
fi

echo ""
echo "════════════════════════════════════════════════"
echo "✅ API Tests Complete!"
echo ""
echo "📋 Next Steps:"
echo "   1. Update .env with:"
echo "      MAPIGURU_BASE_URL=https://chat.mapiguru.yo-digital.com"
echo "      DEEPWIKI_EMBEDDER_TYPE=mapiguru"
echo ""
echo "   2. Restart DeepWiki:"
echo "      ./restart-deepwiki.sh"
echo ""
echo "   3. Test on small repo:"
echo "      /Users/ishan.garg/Downloads/ONE_SHOP/infra/com.dt.configserver"
echo "════════════════════════════════════════════════"



