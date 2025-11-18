# Human-in-the-Loop & Traceability Implementation Guide

## 🎯 Overview

This guide explains how to implement and use the new Human-in-the-Loop (HITL) query clarification and evaluation/traceability features in PCA Agent.

---

## 📦 What's Been Added

### 1. New Files Created

```
src/
├── query_engine/
│   └── query_clarification.py          # Query interpretation generator
├── evaluation/
│   ├── __init__.py
│   └── query_tracker.py                # Logging & metrics tracker
└── ...

streamlit_app_hitl.py                   # Enhanced Streamlit app
ENHANCED_ARCHITECTURE.md                # Architecture documentation
HITL_IMPLEMENTATION_GUIDE.md            # This file
```

### 2. New Database

**Location:** `logs/query_tracker.db` (SQLite)

**Tables:**
- `query_logs` - All query details
- `query_metrics` - Performance metrics

---

## 🚀 Quick Start

### Step 1: Install Dependencies

No new dependencies needed! Uses existing OpenAI/Anthropic setup.

### Step 2: Run the Enhanced App

```bash
streamlit run streamlit_app_hitl.py
```

### Step 3: Try It Out

1. Upload your campaign CSV
2. Ask a question: "Show me campaigns with high spend"
3. See 5 interpretations
4. Select the one that matches your intent
5. Execute and see results
6. Provide feedback (thumbs up/down)

---

## 🎨 User Experience Flow

### Before (Old Flow)
```
User Query → SQL Generated → Results Shown
```

**Problem:** User doesn't know if the system understood correctly.

### After (New Flow)
```
User Query 
    ↓
Understanding Phase (3-5 interpretations shown)
    ↓
User Selects Best Match
    ↓
SQL Generated & Shown
    ↓
Results Displayed
    ↓
User Provides Feedback
    ↓
Everything Logged for Analysis
```

**Benefits:** 
- ✅ User confirms understanding
- ✅ Higher accuracy
- ✅ Full traceability
- ✅ Continuous improvement

---

## 💡 Example Usage

### Example 1: Ambiguous Query

**User asks:** "Show me high performing campaigns"

**System generates 5 interpretations:**

1. **Campaigns with ROAS > 3.0** (85% confidence)
   - *Reasoning:* High performance typically means good return on ad spend
   - *SQL Focus:* Filter on ROAS > 3.0

2. **Campaigns in top 20% by conversions** (75% confidence)
   - *Reasoning:* Performance could mean conversion volume
   - *SQL Focus:* Rank by conversions, take top 20%

3. **Campaigns with CTR > 2%** (65% confidence)
   - *Reasoning:* High performance could mean engagement
   - *SQL Focus:* Filter on CTR > 0.02

4. **Campaigns with spend efficiency (low CPA)** (60% confidence)
   - *Reasoning:* Performance could mean cost efficiency
   - *SQL Focus:* Order by CPA ascending

5. **Campaigns with positive ROI** (55% confidence)
   - *Reasoning:* Basic performance metric
   - *SQL Focus:* Filter on Revenue > Spend

**User selects:** Option 1 (ROAS > 3.0)

**System:** Generates SQL, executes, shows results

**User:** Gives thumbs up

**System:** Logs everything for future improvement

---

## 📊 Evaluation Metrics Tracked

### Query-Level Metrics

| Metric | Description | Use Case |
|--------|-------------|----------|
| `query_id` | Unique identifier | Traceability |
| `timestamp` | When query was asked | Time analysis |
| `original_query` | Raw user input | Understanding patterns |
| `interpretations` | All generated options | Accuracy analysis |
| `selected_interpretation_index` | Which option user chose | Interpretation accuracy |
| `generated_sql` | The SQL executed | Debugging |
| `execution_time_ms` | Query performance | Optimization |
| `result_count` | Number of rows returned | Result quality |
| `user_feedback` | Thumbs up/down | Satisfaction |
| `error_message` | If query failed | Error analysis |

### System-Level Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| **Interpretation Accuracy** | % of times first interpretation selected | >70% |
| **Success Rate** | % of queries without errors | >95% |
| **Avg Response Time** | Mean execution time | <2000ms |
| **User Satisfaction** | Average feedback score | >0.5 |
| **Query Refinement Rate** | % of queries with additional feedback | <20% |

---

## 🔍 Accessing the Data

### Via Streamlit UI

1. **Sidebar Metrics** - Real-time summary
2. **Query History Tab** - See all past queries
3. **Analytics Tab** - Visualizations and trends

### Via Python API

```python
from src.evaluation.query_tracker import QueryTracker

tracker = QueryTracker()

# Get summary metrics
metrics = tracker.get_metrics_summary()
print(f"Total queries: {metrics['total_queries']}")
print(f"Success rate: {metrics['success_rate']}%")

# Get all queries as DataFrame
df = tracker.get_all_queries(limit=100)
print(df.head())

# Export to CSV
tracker.export_to_csv("my_query_logs.csv")
```

### Via SQL (Direct Database Access)

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect("logs/query_tracker.db")

# Get queries with positive feedback
df = pd.read_sql_query("""
    SELECT 
        timestamp,
        original_query,
        selected_interpretation,
        execution_time_ms,
        user_feedback
    FROM query_logs
    WHERE user_feedback = 1
    ORDER BY timestamp DESC
""", conn)

print(df)
conn.close()
```

---

## 📈 Analytics & Reporting

### Built-in Analytics

The enhanced Streamlit app includes:

1. **Real-time Metrics Dashboard**
   - Total queries
   - Success rate
   - Average feedback
   - Interpretation accuracy

2. **Query History View**
   - All past queries
   - Execution times
   - User feedback

3. **Analytics Dashboard**
   - Interpretation accuracy trends
   - Feedback distribution
   - Most common queries
   - Performance over time

### Custom Analytics

Create custom reports using the query logs:

```python
import pandas as pd
from src.evaluation.query_tracker import QueryTracker

tracker = QueryTracker()
df = tracker.get_all_queries(limit=999999)

# Most common query patterns
print("Top 10 queries:")
print(df['original_query'].value_counts().head(10))

# Average execution time by query complexity
df['query_length'] = df['original_query'].str.len()
print("\nAvg execution time by query length:")
print(df.groupby(pd.cut(df['query_length'], bins=5))['execution_time_ms'].mean())

# Feedback by interpretation accuracy
df['first_interp_selected'] = df['selected_interpretation_index'] == 0
print("\nFeedback when first interpretation selected:")
print(df[df['first_interp_selected']]['user_feedback'].mean())
print("\nFeedback when other interpretation selected:")
print(df[~df['first_interp_selected']]['user_feedback'].mean())
```

---

## 🎯 Best Practices

### For Users

1. **Be Specific**: More specific queries get better interpretations
2. **Review Options**: Take time to read all interpretations
3. **Provide Feedback**: Help the system improve
4. **Add Comments**: Explain why results were/weren't helpful

### For Developers

1. **Monitor Metrics**: Check interpretation accuracy weekly
2. **Analyze Patterns**: Look for common misunderstandings
3. **Iterate Prompts**: Improve interpretation generation based on data
4. **Export Regularly**: Backup query logs for long-term analysis

### For Business

1. **Track ROI**: Measure time-to-insight improvements
2. **User Adoption**: Monitor query volume trends
3. **Quality Metrics**: Track user satisfaction scores
4. **Compliance**: Use logs for audit trails

---

## 🔧 Customization

### Adjust Number of Interpretations

In `streamlit_app_hitl.py`:

```python
interpretations = st.session_state.clarifier.generate_interpretations(
    user_query,
    schema_info,
    num_interpretations=3  # Change from 5 to 3
)
```

### Change Confidence Threshold

In `src/query_engine/query_clarification.py`:

```python
# Filter out low-confidence interpretations
interpretations = [i for i in interpretations if i['confidence'] > 0.6]
```

### Add Custom Metrics

```python
tracker.log_metric(
    query_id=query_id,
    metric_name="custom_metric",
    metric_value=123.45
)
```

---

## 🐛 Troubleshooting

### Issue: No interpretations generated

**Cause:** LLM API error or invalid response

**Solution:** Check API keys and logs

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Issue: Database locked

**Cause:** Multiple processes accessing SQLite

**Solution:** Use one Streamlit instance at a time, or upgrade to PostgreSQL

### Issue: Slow interpretation generation

**Cause:** LLM API latency

**Solution:** 
- Cache common queries
- Use faster model (GPT-3.5 instead of GPT-4)
- Reduce `num_interpretations`

---

## 📚 API Reference

### QueryClarifier

```python
from src.query_engine.query_clarification import QueryClarifier

clarifier = QueryClarifier(use_anthropic=True)

# Generate interpretations
interpretations = clarifier.generate_interpretations(
    query="Show high spend campaigns",
    schema_info={"columns": [...], "sample_data": [...]},
    num_interpretations=5
)

# Refine interpretation
refined = clarifier.refine_interpretation(
    original_query="Show high spend",
    selected_interpretation=interpretations[0],
    user_feedback="Only last 30 days"
)
```

### QueryTracker

```python
from src.evaluation.query_tracker import QueryTracker

tracker = QueryTracker(db_path="logs/query_tracker.db")

# Start tracking
query_id = tracker.start_query(
    original_query="Show campaigns",
    interpretations=[...],
    user_id="user123",
    session_id="session456"
)

# Update with execution details
tracker.update_query(
    query_id=query_id,
    selected_interpretation_index=0,
    generated_sql="SELECT * FROM...",
    execution_time_ms=150,
    result_count=42
)

# Add feedback
tracker.add_feedback(
    query_id=query_id,
    feedback=1,  # thumbs up
    comment="Very helpful!"
)

# Get metrics
metrics = tracker.get_metrics_summary()
```

---

## 🚀 Next Steps

### Phase 1: Basic Implementation (Week 1)
- ✅ Query clarification module
- ✅ Basic traceability
- ✅ Enhanced Streamlit UI

### Phase 2: Advanced Features (Week 2-3)
- [ ] Interpretation caching
- [ ] A/B testing different prompts
- [ ] Advanced analytics dashboard
- [ ] Automated reporting

### Phase 3: ML Enhancement (Week 4+)
- [ ] Learn from user selections
- [ ] Personalized interpretations
- [ ] Predictive query suggestions
- [ ] Anomaly detection in queries

---

## 📞 Support

For questions or issues:
1. Check logs: `logs/query_tracker.db`
2. Review documentation: `ENHANCED_ARCHITECTURE.md`
3. Contact: [Your contact info]

---

**Happy Querying! 🎉**
