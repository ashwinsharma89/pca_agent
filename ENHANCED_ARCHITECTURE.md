# Enhanced PCA Agent Architecture

## New Features Overview

### 1. Human-in-the-Loop Query Clarification
### 2. Evaluation Metrics & Traceability

---

## 1. Human-in-the-Loop (HITL) Query Clarification

### Architecture Flow

```
User Query → LLM Understanding → Multiple Interpretations → User Selection → SQL Generation → Results
```

### Implementation Design

#### Step 1: Query Understanding Phase
When user asks a natural language question, the LLM generates **3-5 possible interpretations**:

**Example User Query:**
> "Show me campaigns with high spend"

**LLM Generates Interpretations:**
1. "Show campaigns where total spend is above $10,000"
2. "Show campaigns in the top 20% by spend"
3. "Show campaigns where spend increased by more than 50% compared to last period"
4. "Show campaigns where spend per conversion is high (above average CPA)"
5. "Show campaigns where daily spend exceeds $500"

#### Step 2: User Selection
User selects the interpretation that best matches their intent.

#### Step 3: SQL Generation
System generates SQL based on the selected interpretation with full context.

---

## 2. Evaluation Metrics & Traceability

### What to Track

#### A. Query-Level Metrics
- **Query ID**: Unique identifier for each query
- **Timestamp**: When query was asked
- **User ID**: Who asked the query
- **Original Query**: Raw natural language input
- **Selected Interpretation**: Which interpretation user chose
- **Generated SQL**: The SQL query that was executed
- **Execution Time**: How long the query took
- **Result Count**: Number of rows returned
- **User Feedback**: Thumbs up/down on results
- **Follow-up Actions**: Did user ask clarifying questions?

#### B. System-Level Metrics
- **Interpretation Accuracy**: % of times user selects first interpretation
- **Query Success Rate**: % of queries that return results
- **Average Response Time**: Time from query to results
- **User Satisfaction Score**: Average feedback rating
- **Query Complexity**: Simple vs complex queries
- **Error Rate**: % of queries that fail

#### C. Business Metrics
- **Most Asked Questions**: Top 10 queries
- **Query Categories**: Campaign, Budget, Performance, etc.
- **Time-to-Insight**: How quickly users get answers
- **Query Refinement Rate**: How often users rephrase queries

---

## Implementation Files

### File 1: Query Clarification Module
**Location:** `src/query_engine/query_clarification.py`

### File 2: Evaluation & Traceability Module
**Location:** `src/evaluation/query_tracker.py`

### File 3: Enhanced NL-to-SQL Engine
**Location:** `src/query_engine/nl_to_sql_enhanced.py`

### File 4: Streamlit UI Updates
**Location:** `streamlit_app_enhanced.py`

---

## Database Schema for Traceability

### Table: query_logs
```sql
CREATE TABLE query_logs (
    query_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50),
    session_id VARCHAR(50),
    timestamp TIMESTAMP,
    original_query TEXT,
    interpretations JSON,
    selected_interpretation_index INT,
    selected_interpretation TEXT,
    generated_sql TEXT,
    execution_time_ms INT,
    result_count INT,
    error_message TEXT,
    user_feedback INT,  -- -1, 0, 1 for thumbs down, neutral, thumbs up
    feedback_comment TEXT
);
```

### Table: query_metrics
```sql
CREATE TABLE query_metrics (
    metric_id VARCHAR(50) PRIMARY KEY,
    query_id VARCHAR(50),
    metric_name VARCHAR(100),
    metric_value FLOAT,
    timestamp TIMESTAMP,
    FOREIGN KEY (query_id) REFERENCES query_logs(query_id)
);
```

---

## UI/UX Flow

### Current Flow (Before)
```
1. User enters query
2. System generates SQL
3. System shows results
```

### Enhanced Flow (After)
```
1. User enters query
2. System shows "Understanding your query..." spinner
3. System displays 3-5 interpretations with radio buttons
4. User selects the closest interpretation
5. System generates SQL and shows it (optional: collapsible)
6. System executes and shows results
7. User provides feedback (thumbs up/down)
8. System logs everything for traceability
```

---

## Benefits

### For Users
- ✅ **Clarity**: Know exactly what the system understood
- ✅ **Control**: Choose the right interpretation
- ✅ **Confidence**: See the SQL being executed
- ✅ **Learning**: Understand how queries work

### For System
- ✅ **Accuracy**: Better query understanding
- ✅ **Feedback Loop**: Learn from user selections
- ✅ **Debugging**: Full traceability of queries
- ✅ **Improvement**: Identify common misunderstandings

### For Business
- ✅ **Insights**: Understand what users ask most
- ✅ **Quality**: Track system performance
- ✅ **Compliance**: Full audit trail
- ✅ **ROI**: Measure time-to-insight improvements

---

## Next Steps

1. **Implement Query Clarification Module** (Week 1)
2. **Add Traceability Database** (Week 1)
3. **Update Streamlit UI** (Week 2)
4. **Create Evaluation Dashboard** (Week 2)
5. **Add Feedback Collection** (Week 3)
6. **Build Analytics Reports** (Week 3)

---

## Quick Win: Minimal Implementation

If you want to start small, implement just these:

1. **Query Clarification**: Show 3 interpretations, let user pick
2. **Basic Logging**: Log query, SQL, and user selection to CSV
3. **Simple Feedback**: Add thumbs up/down buttons

This gives you 80% of the value with 20% of the effort!
