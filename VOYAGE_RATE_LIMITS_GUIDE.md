# Voyage AI Rate Limits Guide

## 📊 Understanding Voyage AI Rate Limits

### Current Configuration (Free Tier)

```json
{
  "embedder_voyage": {
    "client_class": "VoyageClient",
    "batch_size": 10,  ← Optimized for 10K TPM limit
    "model_kwargs": {
      "model": "voyage-3-large",
      "input_type": "document",
      "truncation": true
    }
  }
}
```

---

## 🚦 Rate Limit Tiers

### **Tier 0 (Free - No Payment Method)**

```
⚠️ Current Tier (Active)
├─ Requests: 3 per minute (RPM)
├─ Tokens: 10,000 per minute (TPM)
├─ Recommended batch_size: 10
└─ Processing speed: ~30 chunks/min
```

**Calculation:**
```
3 requests/min × 10 texts/request = 30 texts/min
30 texts × ~200 tokens/text = ~6,000 TPM ✅
```

---

### **Tier 1+ (With Payment Method)**

```
✅ After Adding Payment Method
├─ Requests: 300+ per minute (RPM)
├─ Tokens: 1,000,000+ per minute (TPM)
├─ Recommended batch_size: 128
└─ Processing speed: ~38,400 chunks/min
```

**Calculation:**
```
300 requests/min × 128 texts/request = 38,400 texts/min
38,400 texts × ~200 tokens/text = ~7.6M TPM ✅
```

---

## 🎯 Optimal batch_size by Tier

| Tier | RPM | TPM | batch_size | Throughput |
|------|-----|-----|------------|------------|
| **Tier 0 (Free)** | 3 | 10K | 10 | ~30 texts/min |
| **Tier 1** | 60 | 200K | 50 | ~3,000 texts/min |
| **Tier 2** | 300 | 1M | 128 | ~38,400 texts/min |
| **Tier 3** | 600 | 2M | 256 | ~153,600 texts/min |

---

## 📈 Repository Size Impact

### Example: E-Commerce Project (66 chunks)

**With Current Settings (Tier 0):**
```
66 chunks ÷ 10 per batch = 7 requests needed
7 requests ÷ 3 RPM = 2.33 minutes
Total time: ~2-3 minutes ⏱️
```

**With Payment Method (Tier 1+):**
```
66 chunks ÷ 128 per batch = 1 request needed
1 request at 300 RPM = instant
Total time: ~1-2 seconds ⚡
```

---

## ⚙️ Configuration for Different Tiers

### **For Tier 0 (Current - Free)**

```json
{
  "embedder_voyage": {
    "batch_size": 10,
    "model_kwargs": {
      "model": "voyage-3-large",
      "input_type": "document",
      "truncation": true
    }
  }
}
```

**When to use:**
- ✅ Testing the integration
- ✅ Small repositories (< 100 files)
- ✅ Not in a hurry
- ❌ Large repositories (slow)
- ❌ Production use (too slow)

---

### **For Tier 1+ (With Payment Method)**

```json
{
  "embedder_voyage": {
    "batch_size": 128,
    "model_kwargs": {
      "model": "voyage-3-large",
      "input_type": "document",
      "truncation": true
    }
  }
}
```

**When to use:**
- ✅ Production deployments
- ✅ Large repositories
- ✅ Fast processing needed
- ✅ Multiple concurrent wikis

---

## 🔄 How to Upgrade

### **Step 1: Add Payment Method**

1. Visit: https://dashboard.voyageai.com/billing
2. Click "Add Payment Method"
3. Enter credit card details
4. Click "Save"

### **Step 2: Wait for Rate Limit Update**

```
⏱️ Wait 5-10 minutes for rate limits to update
```

### **Step 3: Update Configuration**

Edit `api/config/embedder.json`:

```json
{
  "embedder_voyage": {
    "batch_size": 128,  ← Change from 10 to 128
    "model_kwargs": {
      "model": "voyage-3-large",
      "input_type": "document",
      "truncation": true
    }
  }
}
```

### **Step 4: Restart**

```bash
cd /Users/ishan.garg/Downloads/ONE_SHOP/deepwiki-open
bash restart-deepwiki.sh
```

---

## 💰 Cost Analysis

### **Free Tokens (All Tiers)**
```
🎁 200M tokens FREE per model
📊 ~400,000 document chunks
📈 ~6,000 average repositories
```

### **After Free Tier**
```
💵 Pay-as-you-go pricing
📊 Check: https://www.voyageai.com/pricing
```

---

## 🐛 Common Issues

### **Issue 1: "429 Too Many Requests"**

**Cause:** batch_size too high for current tier

**Solution:**
```bash
# For Tier 0 (Free)
batch_size: 10

# For Tier 1+
batch_size: 128
```

---

### **Issue 2: Slow Processing**

**Cause:** Free tier rate limits (3 RPM)

**Solution:**
1. Add payment method for Tier 1+ rates
2. Or switch to MapiGuru temporarily:
   ```bash
   DEEPWIKI_EMBEDDER_TYPE=mapiguru
   ```

---

### **Issue 3: "Token limit exceeded"**

**Cause:** Batch size × average tokens > TPM limit

**Solution:**
```
Tier 0: batch_size = 10 (max safe value)
Tier 1+: batch_size = 128 (recommended)
```

---

## 📊 Performance Comparison

### **Repository: 66 chunks**

| Config | Time | Notes |
|--------|------|-------|
| Voyage (Tier 0, batch=10) | 2-3 min | ⚠️ Rate limited |
| Voyage (Tier 1+, batch=128) | 1-2 sec | ⚡ Fast |
| MapiGuru (batch=100) | 5-10 sec | ✅ No rate limits |
| Google AI (batch=100) | 3-5 sec | ✅ Free tier |

---

## 🎯 Recommendations

### **For Development/Testing:**
```bash
# Use MapiGuru (no rate limits)
DEEPWIKI_EMBEDDER_TYPE=mapiguru
```

### **For Production (Best Quality):**
```bash
# Use Voyage AI with payment method
DEEPWIKI_EMBEDDER_TYPE=voyage
# Add payment method for Tier 1+ rates
```

### **For Cost-Conscious Production:**
```bash
# Use Google AI (free + good quality)
DEEPWIKI_EMBEDDER_TYPE=google
GOOGLE_API_KEY=your_key
```

---

## 📝 Summary

**Current Setup (Tier 0):**
```
✅ Voyage AI configured
✅ batch_size: 10 (optimal for free tier)
⚠️ 3 RPM limit (slow but works)
🎁 200M free tokens available
```

**To Upgrade:**
```
1. Add payment method → dashboard.voyageai.com/billing
2. Change batch_size to 128
3. Restart DeepWiki
4. Enjoy 100x faster processing! 🚀
```

---

**Last Updated:** November 21, 2025  
**Your API Key:** `pa-ySmYuKQdAQby_CVBou8T_dGPkCPZVkG2ZvlyJk0nPgh`  
**Current Tier:** 0 (Free - No Payment Method)

