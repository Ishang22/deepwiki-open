#!/usr/bin/env python3
"""
Test script for Voyage AI embedder integration.
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Set up environment
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_voyage_embedder_client():
    """Test the Voyage AI embedder client directly."""
    logger.info("Testing Voyage AI embedder client...")
    
    try:
        from api.voyage_client import VoyageClient
        from adalflow.core.types import ModelType
        
        # Check if API key is set
        if not os.environ.get('VOYAGE_API_KEY'):
            logger.warning("VOYAGE_API_KEY not set, skipping test")
            return True
        
        # Initialize the client
        client = VoyageClient()
        
        # Test single embedding
        logger.info("Testing single embedding...")
        api_kwargs = client.convert_inputs_to_api_kwargs(
            input="Hello world",
            model_kwargs={"model": "voyage-3-large"},
            model_type=ModelType.EMBEDDER
        )
        
        response = client.call(api_kwargs, ModelType.EMBEDDER)
        logger.info(f"Single embedding response type: {type(response)}")
        
        if response.error:
            logger.error(f"Single embedding error: {response.error}")
            return False
        
        logger.info(f"Single embedding data length: {len(response.data) if response.data else 0}")
        if response.data and len(response.data) > 0:
            logger.info(f"Embedding vector length: {len(response.data[0].embedding)}")
        
        # Test batch embedding
        logger.info("Testing batch embedding...")
        api_kwargs = client.convert_inputs_to_api_kwargs(
            input=["Hello world", "Test embedding", "Voyage AI is great"],
            model_kwargs={"model": "voyage-3-large"},
            model_type=ModelType.EMBEDDER
        )
        
        response = client.call(api_kwargs, ModelType.EMBEDDER)
        logger.info(f"Batch embedding response type: {type(response)}")
        
        if response.error:
            logger.error(f"Batch embedding error: {response.error}")
            return False
        
        logger.info(f"Batch embedding data length: {len(response.data) if response.data else 0}")
        
        # Verify we got the right number of embeddings
        if response.data and len(response.data) == 3:
            logger.info(f"✓ Received expected number of embeddings (3)")
            for i, emb_obj in enumerate(response.data):
                logger.info(f"  Embedding {i+1}: {len(emb_obj.embedding)} dimensions")
        else:
            logger.error(f"Expected 3 embeddings, got {len(response.data) if response.data else 0}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing Voyage embedder client: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_voyage_code_model():
    """Test the Voyage code-specific model."""
    logger.info("Testing Voyage code model...")
    
    try:
        from api.voyage_client import VoyageClient
        from adalflow.core.types import ModelType
        
        # Check if API key is set
        if not os.environ.get('VOYAGE_API_KEY'):
            logger.warning("VOYAGE_API_KEY not set, skipping test")
            return True
        
        # Initialize the client
        client = VoyageClient()
        
        # Test with code snippet
        code_snippet = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
        
        logger.info("Testing code embedding with voyage-code-3...")
        api_kwargs = client.convert_inputs_to_api_kwargs(
            input=code_snippet,
            model_kwargs={"model": "voyage-code-3"},
            model_type=ModelType.EMBEDDER
        )
        
        response = client.call(api_kwargs, ModelType.EMBEDDER)
        
        if response.error:
            logger.warning(f"Code model test failed (this is OK if you don't have access): {response.error}")
            return True  # Don't fail the test if model not available
        
        logger.info(f"Code embedding data length: {len(response.data) if response.data else 0}")
        if response.data and len(response.data) > 0:
            logger.info(f"✓ Code embedding vector length: {len(response.data[0].embedding)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing Voyage code model: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_adalflow_embedder():
    """Test the AdalFlow embedder with Voyage client."""
    logger.info("Testing AdalFlow embedder with Voyage client...")
    
    try:
        # Check if API key is set
        if not os.environ.get('VOYAGE_API_KEY'):
            logger.warning("VOYAGE_API_KEY not set, skipping test")
            return True
        
        import adalflow as adal
        from api.voyage_client import VoyageClient
        
        # Create embedder
        client = VoyageClient()
        embedder = adal.Embedder(
            model_client=client,
            model_kwargs={
                "model": "voyage-3-large"
            }
        )
        
        # Test embedding
        logger.info("Testing embedder with single input...")
        result = embedder("Hello world")
        logger.info(f"Embedder result type: {type(result)}")
        
        if hasattr(result, 'data'):
            logger.info(f"Result data length: {len(result.data) if result.data else 0}")
            if result.data and len(result.data) > 0:
                logger.info(f"✓ Embedding vector length: {len(result.data[0].embedding)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing AdalFlow embedder: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_document_processing():
    """Test document processing with Voyage embedder."""
    logger.info("Testing document processing with Voyage embedder...")
    
    try:
        # Check if API key is set
        if not os.environ.get('VOYAGE_API_KEY'):
            logger.warning("VOYAGE_API_KEY not set, skipping test")
            return True
        
        from adalflow.core.types import Document
        from adalflow.components.data_process import ToEmbeddings
        from api.tools.embedder import get_embedder
        
        # Create some test documents
        docs = [
            Document(text="This is a test document about artificial intelligence.", meta_data={"file_path": "test1.txt"}),
            Document(text="Machine learning is a subset of AI.", meta_data={"file_path": "test2.txt"}),
            Document(text="Deep learning uses neural networks.", meta_data={"file_path": "test3.txt"})
        ]
        
        # Get the Voyage embedder
        embedder = get_embedder(embedder_type='voyage')
        logger.info(f"Embedder type: {type(embedder)}")
        
        # Process documents
        embedder_transformer = ToEmbeddings(embedder=embedder, batch_size=128)
        
        # Transform documents
        logger.info("Transforming documents...")
        transformed_docs = embedder_transformer(docs)
        
        logger.info(f"Transformed docs type: {type(transformed_docs)}")
        logger.info(f"Number of transformed docs: {len(transformed_docs)}")
        
        # Check the structure
        for i, doc in enumerate(transformed_docs):
            if hasattr(doc, 'vector'):
                logger.info(f"✓ Doc {i} has vector of length: {len(doc.vector) if doc.vector else 0}")
            else:
                logger.warning(f"Doc {i} has no vector attribute")
        
        return transformed_docs
        
    except Exception as e:
        logger.error(f"Error testing document processing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_different_input_types():
    """Test different input_type parameter values."""
    logger.info("Testing different input_type parameters...")
    
    try:
        # Check if API key is set
        if not os.environ.get('VOYAGE_API_KEY'):
            logger.warning("VOYAGE_API_KEY not set, skipping test")
            return True
        
        from api.voyage_client import VoyageClient
        from adalflow.core.types import ModelType
        
        client = VoyageClient()
        
        # Test with document input type
        logger.info("Testing with input_type='document'...")
        api_kwargs = {
            "input": "This is a document to be indexed",
            "model": "voyage-3-large",
            "input_type": "document"
        }
        response = client.call(api_kwargs, ModelType.EMBEDDER)
        
        if response.error:
            logger.error(f"Document input type error: {response.error}")
            return False
        
        logger.info(f"✓ Document input type successful")
        
        # Test with query input type
        logger.info("Testing with input_type='query'...")
        api_kwargs = {
            "input": "What is artificial intelligence?",
            "model": "voyage-3-large",
            "input_type": "query"
        }
        response = client.call(api_kwargs, ModelType.EMBEDDER)
        
        if response.error:
            logger.error(f"Query input type error: {response.error}")
            return False
        
        logger.info(f"✓ Query input type successful")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing input types: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    logger.info("Starting Voyage AI embedder tests...")
    
    # Check if API key is set
    if not os.environ.get('VOYAGE_API_KEY'):
        logger.warning("=" * 60)
        logger.warning("VOYAGE_API_KEY not set - skipping all tests")
        logger.warning("To run these tests, set: export VOYAGE_API_KEY='your-key'")
        logger.warning("=" * 60)
        return True
    
    # Test 1: Direct client test
    if not test_voyage_embedder_client():
        logger.error("Voyage embedder client test failed")
        return False
    
    # Test 2: Voyage code model test
    if not test_voyage_code_model():
        logger.error("Voyage code model test failed")
        return False
    
    # Test 3: AdalFlow embedder test
    if not test_adalflow_embedder():
        logger.error("AdalFlow embedder test failed")
        return False
    
    # Test 4: Document processing test
    result = test_document_processing()
    if result is False:
        logger.error("Document processing test failed")
        return False
    
    # Test 5: Different input types
    if not test_different_input_types():
        logger.error("Input types test failed")
        return False
    
    logger.info("=" * 60)
    logger.info("✅ All Voyage AI embedder tests completed successfully!")
    logger.info("=" * 60)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

