# Voyage AI Setup Guide for DeepWiki

This guide will help you integrate Voyage AI's embedding service with DeepWiki.

## Overview

Voyage AI provides state-of-the-art embedding models that can be used with DeepWiki for semantic search and document understanding. The integration supports all Voyage AI models including:

- **voyage-3-large** (default) - State-of-the-art general-purpose embedding model with Matryoshka learning
- **voyage-3.5** - Latest model with improved performance
- **voyage-code-3** - Optimized for code understanding
- **voyage-law-2** - Specialized for legal documents
- **voyage-finance-2** - Optimized for financial documents

## Prerequisites

1. **Voyage AI Account & API Key**
   - Sign up at [https://www.voyageai.com](https://www.voyageai.com)
   - Generate your API key from the [Voyage AI dashboard](https://dash.voyageai.com)
   - All accounts receive 200M free tokens per model

## Setup Instructions

### Step 1: Set Environment Variables

Add your Voyage AI API key to your environment:

```bash
export VOYAGE_API_KEY="your-voyage-api-key-here"
```

To use Voyage AI as your embedder, set the embedder type:

```bash
export DEEPWIKI_EMBEDDER_TYPE="voyage"
```

### Step 2: Configure the Embedder (Optional)

The default configuration uses `voyage-3-large` model. To customize, edit `api/config/embedder.json`:

```json
{
  "embedder_voyage": {
    "client_class": "VoyageClient",
    "batch_size": 128,
    "model_kwargs": {
      "model": "voyage-3-large",
      "input_type": "document",
      "truncation": true
    }
  }
}
```

#### Available Configuration Options:

- **model**: Choose from available models
  - `voyage-3-large` (recommended for general use)
  - `voyage-3.5` (latest model)
  - `voyage-code-3` (for code repositories)
  - `voyage-law-2` (for legal documents)
  - `voyage-finance-2` (for financial documents)

- **input_type**: Specify the type of input
  - `document` (default) - For documents to be retrieved
  - `query` - For search queries

- **truncation**: Whether to truncate inputs that exceed the model's context length
  - `true` (default) - Automatically truncate
  - `false` - Return error if input too long

- **batch_size**: Number of texts to embed in a single request (default: 128)

### Step 3: Restart DeepWiki

After setting the environment variables, restart DeepWiki:

```bash
./restart-deepwiki.sh
```

Or if using Docker:

```bash
docker-compose down
docker-compose up -d
```

## Verification

To verify the Voyage AI integration is working:

1. Check the application logs for the initialization message:
   ```
   Voyage AI client initialized with base URL: https://api.voyageai.com/v1
   ```

2. Test with a simple query:
   ```bash
   # The embedder will automatically use Voyage AI
   curl http://localhost:8000/api/embed -d '{"text": "hello world"}'
   ```

## Model Selection Guide

Choose the right model for your use case:

| Model | Use Case | Dimensions | Context Length |
|-------|----------|------------|----------------|
| voyage-3-large | General-purpose, best overall performance | 1024 | 32K tokens |
| voyage-3.5 | Latest improvements, balanced performance | 1024 | 32K tokens |
| voyage-code-3 | Code repositories, technical documentation | 1024 | 16K tokens |
| voyage-law-2 | Legal documents, contracts | 1024 | 16K tokens |
| voyage-finance-2 | Financial reports, analysis | 1024 | 16K tokens |

## Cost & Rate Limits

- **Free Tier**: 200M tokens per model (no credit card required)
- **Rate Limits**: 
  - Tier 0 (free): 300 requests/min
  - Tier 1+: Higher limits with payment method
- **Pricing**: Pay-as-you-go after free tier (check [Voyage AI pricing](https://www.voyageai.com/pricing))

## Advanced Configuration

### Using Different Models for Different Repositories

You can specify the embedder type per repository by setting it in your environment or configuration.

### Custom API Base URL (Self-hosted)

If you're using a self-hosted Voyage AI instance:

```bash
export VOYAGE_BASE_URL="https://your-voyage-instance.com/v1"
```

### Troubleshooting

#### Issue: "VOYAGE_API_KEY is required but not set"

**Solution**: Ensure you've exported the VOYAGE_API_KEY environment variable:
```bash
export VOYAGE_API_KEY="your-key-here"
```

#### Issue: Rate limit errors

**Solution**: 
1. Add a payment method to your Voyage AI account for higher rate limits
2. Reduce the `batch_size` in the configuration
3. Implement request throttling in your application

#### Issue: Model not found

**Solution**: Verify you're using a valid model name from the supported models list above.

## API Reference

The Voyage AI client supports the following parameters in API calls:

```python
{
    "input": "text to embed" | ["text1", "text2", ...],
    "model": "voyage-3-large",
    "input_type": "document" | "query",
    "truncation": true | false,
    "encoding_format": "float" | "base64"  # optional
}
```

## Resources

- [Voyage AI Documentation](https://docs.voyageai.com)
- [Voyage AI Dashboard](https://dash.voyageai.com)
- [API Reference](https://docs.voyageai.com/reference/embeddings-api)
- [Model Comparison](https://docs.voyageai.com/docs/embeddings)

## Support

For issues specific to the DeepWiki integration:
- Open an issue on the DeepWiki repository

For Voyage AI service issues:
- Email: contact@voyageai.com
- Check the [FAQ page](https://www.voyageai.com/faq)

