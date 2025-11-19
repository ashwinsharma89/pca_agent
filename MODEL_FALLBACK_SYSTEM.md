# 5-Tier AI Model Fallback System

## Overview
The PCA Agent now has a robust 5-tier fallback system that ensures queries ALWAYS work, even if some AI providers fail or run out of quota.

## Tier Priority

### **Tier 1: Gemini 2.5 Flash** 🆓
- **Provider**: Google
- **Cost**: FREE
- **Limits**: 15 requests/min, 1M tokens/day
- **Speed**: Fast
- **Quality**: Excellent for SQL generation
- **Get API Key**: https://aistudio.google.com/app/apikey

### **Tier 2: DeepSeek Chat** 🆓
- **Provider**: DeepSeek
- **Cost**: FREE
- **Limits**: Very generous free tier
- **Speed**: Fast
- **Quality**: **EXCELLENT for coding/SQL** (specialized model)
- **Get API Key**: https://platform.deepseek.com/api_keys

### **Tier 3: OpenAI GPT-4o** 💰
- **Provider**: OpenAI
- **Cost**: Pay per use
- **Quality**: Very high
- **Speed**: Fast
- **Get API Key**: https://platform.openai.com/api-keys

### **Tier 4: Claude Sonnet 4.5** 💰
- **Provider**: Anthropic
- **Cost**: Pay per use
- **Quality**: Premium
- **Speed**: Fast
- **Get API Key**: https://console.anthropic.com/

### **Tier 5: Groq Llama 3.3 70B** 🆓
- **Provider**: Groq
- **Cost**: FREE
- **Limits**: Very generous (30 req/min, 14,400/day)
- **Speed**: SUPER FAST (500+ tokens/sec)
- **Quality**: Good for SQL
- **Get API Key**: https://console.groq.com/keys

## How It Works

1. **System tries Tier 1 (Gemini)** first
2. If Gemini fails → automatically tries **Tier 2 (DeepSeek)**
3. If DeepSeek fails → automatically tries **Tier 3 (OpenAI)**
4. If OpenAI fails → automatically tries **Tier 4 (Claude)**
5. If Claude fails → automatically tries **Tier 5 (Groq)**
6. If all fail → shows clear error message

## Benefits

✅ **Cost Optimization**: Uses 3 FREE models first (Gemini, DeepSeek, Groq)
✅ **Reliability**: 5 providers = system never stops working
✅ **Speed**: Groq is fastest (500+ tokens/sec)
✅ **Quality**: DeepSeek specialized for SQL/coding
✅ **Transparency**: UI shows which model was used

## Setup Instructions

### 1. Install Required Packages
```bash
pip install google-generativeai groq
```

### 2. Get API Keys
- **Gemini** (FREE): https://aistudio.google.com/app/apikey
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/
- **Groq** (FREE): https://console.groq.com/keys

### 3. Add to .env File
```env
GOOGLE_API_KEY=your_gemini_key_here
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GROQ_API_KEY=your_groq_key_here
```

## Model Display in UI

The Streamlit UI now shows which model was used for each query:
- 🤖 **Model Used:** gemini (gemini-2.5-flash) (FREE)
- 🤖 **Model Used:** openai (gpt-4o)
- 🤖 **Model Used:** claude (claude-sonnet-4-5-20250929)
- 🤖 **Model Used:** groq (llama-3.3-70b-versatile) (FREE)

## Cost Comparison

| Provider | Model | Cost | Free Tier |
|----------|-------|------|-----------|
| Gemini | 2.5 Flash | FREE | 1M tokens/day |
| Groq | Llama 3.3 70B | FREE | 14,400 req/day |
| OpenAI | GPT-4o | ~$2.50/1M input tokens | $5 free credit |
| Claude | Sonnet 4.5 | ~$3/1M input tokens | $5 free credit |

## Recommended Setup

**For maximum cost savings:**
1. Use Gemini (Tier 1) - FREE
2. Use Groq (Tier 4) - FREE
3. Keep OpenAI/Claude as paid backups

**For maximum quality:**
1. Use Claude (Tier 1)
2. Use OpenAI (Tier 2)
3. Keep Gemini/Groq as free backups

## Current Configuration

✅ **Tier 1**: Gemini 2.5 Flash (FREE)
✅ **Tier 2**: DeepSeek Chat (FREE - SQL SPECIALIST)
✅ **Tier 3**: OpenAI GPT-4o
✅ **Tier 4**: Claude Sonnet 4.5
✅ **Tier 5**: Groq Llama 3.3 70B (FREE & SUPER FAST)

This ensures:
- **First 2 tiers are FREE** (Gemini → DeepSeek)
- DeepSeek is specialized for SQL/coding
- If both free tiers fail → uses paid OpenAI
- If OpenAI fails → uses premium Claude
- **Ultimate fallback: Groq (FREE & fastest)**

**Your system will NEVER stop working with 3 FREE models!** 🎉
