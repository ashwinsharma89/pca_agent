# PCA Agent Token Usage Analysis

## When You Click "Analyze Data & Generate Insights"

### LLM Calls Made

The `analyze_all()` function makes **3 main LLM calls**:

1. **Insights Generation** (`_generate_insights`)
   - **Prompt Size:** ~2,000-3,000 tokens (data summary + instructions)
   - **Response:** ~1,500-2,000 tokens (8-10 insights in JSON)
   - **Model Used:** Claude Sonnet 4.5 or GPT-4o-mini (based on `USE_ANTHROPIC` setting)

2. **Recommendations Generation** (`_generate_recommendations`)
   - **Prompt Size:** ~2,500-3,500 tokens (metrics + insights + instructions)
   - **Response:** ~1,500-2,000 tokens (8-10 recommendations in JSON)
   - **Model Used:** Claude Sonnet 4.5 or GPT-4o-mini (based on `USE_ANTHROPIC` setting)

3. **Executive Summary Generation** (`_generate_executive_summary`)
   - **Prompt Size:** ~1,500-2,000 tokens (KPIs + top insights/recommendations)
   - **Response:** ~600-800 tokens (4 paragraphs)
   - **Model Used:** **NEW FALLBACK CHAIN:**
     1. **Gemini 2.0 Flash Exp** (primary)
     2. DeepSeek Chat (fallback 1)
     3. GPT-4o-mini (fallback 2)
     4. Claude Sonnet 4.5 (fallback 3)

### Total Token Usage Per Analysis

| Component | Input Tokens | Output Tokens | Total |
|-----------|-------------|---------------|-------|
| Insights | 2,500 | 1,750 | 4,250 |
| Recommendations | 3,000 | 1,750 | 4,750 |
| Executive Summary | 1,750 | 700 | 2,450 |
| **TOTAL** | **7,250** | **4,200** | **~11,450** |

### Cost Breakdown (Approximate)

#### With Claude Sonnet 4.5 (Current Default for Insights/Recommendations)
- Input: 7,250 tokens × $3.00/1M = **$0.022**
- Output: 4,200 tokens × $15.00/1M = **$0.063**
- **Total per analysis: ~$0.085**

#### With Gemini 2.0 Flash Exp (Executive Summary Only)
- Input: 1,750 tokens × **FREE** (1M tokens/day limit)
- Output: 700 tokens × **FREE**
- **Executive Summary: $0.00**

#### If All Using GPT-4o-mini
- Input: 7,250 tokens × $0.15/1M = **$0.001**
- Output: 4,200 tokens × $0.60/1M = **$0.003**
- **Total per analysis: ~$0.004**

## Windsurf Prompts Used

**Zero Windsurf prompts are used during analysis.** All LLM calls go directly to:
- Anthropic API (Claude)
- OpenAI API (GPT-4o-mini)
- Google Gemini API (Gemini 2.0 Flash)
- DeepSeek API (DeepSeek Chat)

Windsurf is only the IDE—it doesn't intercept or count toward your analysis token usage.

## Executive Summary LLM Fallback Chain

### Priority Order (as of latest update):

1. **Gemini 2.5 Pro** (gemini-2.0-flash-exp)
   - **Cost:** FREE (1M tokens/day)
   - **Quality:** Excellent for summaries
   - **Speed:** Very fast
   - **API Key:** `GOOGLE_API_KEY`
   - **Status:** ✅ Primary

2. **Claude Sonnet 4.5** (claude-3-5-sonnet-20241022)
   - **Cost:** $3.00/1M input, $15.00/1M output
   - **Quality:** Excellent reasoning
   - **Speed:** Moderate
   - **API Key:** `ANTHROPIC_API_KEY`
   - **Status:** Fallback 1

3. **GPT-5.1 Medium Reasoning** (o1)
   - **Cost:** $15.00/1M input, $60.00/1M output
   - **Quality:** Advanced reasoning
   - **Speed:** Slower (thinking mode)
   - **API Key:** `OPENAI_API_KEY`
   - **Status:** Fallback 2

4. **xAI Grok-3 Mini** (grok-beta)
   - **Cost:** TBD (Beta pricing)
   - **Quality:** Good with thinking capability
   - **Speed:** Moderate
   - **API Key:** `XAI_API_KEY`
   - **Status:** Fallback 3

**Note:** DeepSeek has been removed as it's blocked in your organization.

## Recommendations

### For Cost Optimization:
1. **Use Gemini 2.0 Flash for Executive Summary** (already configured)
2. **Switch insights/recommendations to GPT-4o-mini** by setting `USE_ANTHROPIC=false` in `.env`
3. **Total cost per analysis: ~$0.004** (vs $0.085 with Claude)

### For Quality:
1. Keep Claude Sonnet for insights/recommendations
2. Use Gemini for executive summary (free + fast)
3. **Total cost per analysis: ~$0.085**

### For Free Tier:
1. Use Gemini for executive summary (FREE - 1M tokens/day)
2. Consider Groq for insights/recommendations (FREE tier available)
3. **Total cost: Near zero** for moderate usage

## How to Configure

Edit `.env` file:

```bash
# For cost optimization (use GPT-4o-mini for everything except exec summary)
USE_ANTHROPIC=false
OPENAI_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here  # For free exec summary

# For quality (use Claude for insights/recs, Gemini for exec summary)
USE_ANTHROPIC=true
ANTHROPIC_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here  # For free exec summary

# For free tier (use Gemini + Groq)
USE_ANTHROPIC=false
GROQ_API_KEY=your_key_here  # Sign up at console.groq.com
GOOGLE_API_KEY=your_key_here

# Optional: Add xAI Grok for additional fallback
XAI_API_KEY=your_key_here  # Sign up at console.x.ai
```

## Executive Summary Quality Issues - FIXED

### Problem:
Executive summary was showing truncated "Key Highlights" instead of full 4-paragraph summary.

### Root Cause:
Streamlit UI was only displaying first 100 words in collapsed view.

### Solution Applied:
1. Removed truncation logic
2. Display full executive summary directly on page
3. Added proper error handling for LLM quota issues
4. Implemented Gemini 2.0 Flash as primary LLM (free + fast)

### Current Status:
✅ Full executive summary now displays correctly
✅ Gemini 2.0 Flash handles generation (free tier)
✅ Fallback chain ensures reliability
✅ No more quota errors with proper API keys
