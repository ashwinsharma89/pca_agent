# Streamlit Database Integration Guide

## Overview

The Streamlit app now automatically saves uploaded campaign data to the SQLite database. Data persists across sessions!

## What Was Added

### 1. Import Statement (Line 51)
```python
from src.streamlit_integration import get_streamlit_db_manager
```

### 2. Helper Functions (Lines 550-578)
```python
@st.cache_resource
def get_db_manager():
    """Get cached database manager instance."""
    return get_streamlit_db_manager()


def save_to_database(df: pd.DataFrame) -> bool:
    """Save DataFrame to database."""
    try:
        db_manager = get_db_manager()
        result = db_manager.import_dataframe(df)
        
        if result['success']:
            logger.info(f"✅ Saved {result['imported_count']} campaigns to database")
            return True
        else:
            logger.error(f"❌ Database save failed: {result['message']}")
            return False
    except Exception as e:
        logger.error(f"❌ Database save error: {e}")
        return False
```

### 3. Auto-Save on Upload (Lines 1081-1087)
```python
# Save to database
with st.spinner("💾 Saving to database..."):
    if save_to_database(df):
        st.success(f"✅ Loaded {len(df)} rows • {len(df.columns)} columns • Saved to database")
    else:
        st.success(f"✅ Loaded {len(df)} rows • {len(df.columns)} columns")
        st.warning("⚠️ Database save failed (data still available in session)")
```

## How It Works

1. **User uploads CSV/Excel** → Data is loaded into `st.session_state.df`
2. **Auto-save triggered** → `save_to_database(df)` is called
3. **Database manager** → Imports data to SQLite database
4. **Success message** → User sees confirmation

## Benefits

✅ **Data Persistence**: Campaigns survive app restarts  
✅ **No Code Changes Needed**: Works automatically on upload  
✅ **Graceful Degradation**: App works even if database save fails  
✅ **User Feedback**: Clear success/failure messages  

## Testing

Upload a CSV file in the Streamlit app and you should see:
```
✅ Loaded 100 rows • 15 columns • Saved to database
```

Check the database:
```python
from src.streamlit_integration import get_streamlit_db_manager

db_manager = get_streamlit_db_manager()
campaigns = db_manager.get_campaigns(limit=10)
print(f"Found {len(campaigns)} campaigns in database")
```

## Advanced Usage

### Query Campaigns from Database

```python
# In your Streamlit app
db_manager = get_db_manager()

# Get campaigns with filters
campaigns = db_manager.get_campaigns(
    filters={'platform': 'Google'},
    limit=100,
    use_cache=True  # Uses 5-minute cache
)

# Display in Streamlit
st.dataframe(campaigns)
```

### Get Aggregated Metrics

```python
# Get metrics
metrics = db_manager.get_aggregated_metrics(
    filters={'platform': 'Google'}
)

# Display metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Spend", f"${metrics['total_spend']:,.2f}")
col2.metric("Total Clicks", f"{metrics['total_clicks']:,}")
col3.metric("Total Conversions", f"{metrics['total_conversions']:,}")
```

### Track LLM Usage

```python
# After LLM call
db_manager.track_llm_usage(
    provider='openai',
    model='gpt-4',
    prompt_tokens=1000,
    completion_tokens=500,
    cost=0.045,
    operation='auto_analysis'
)

# View usage stats
stats = db_manager.get_llm_usage_stats(days=30)
st.metric("Total LLM Cost", f"${stats['total']['total_cost']:.2f}")
```

### Save Analysis Results

```python
# After analysis completes
analysis_id = db_manager.save_analysis(
    analysis_type='auto',
    results={
        'insights': insights,
        'recommendations': recommendations,
        'metrics': metrics,
        'executive_summary': summary
    },
    execution_time=45.2
)

st.success(f"Analysis saved! ID: {analysis_id}")
```

## Database Location

- **SQLite**: `pca_agent.db` in project root
- **PostgreSQL**: Configure in `.env` (set `USE_SQLITE=false`)

## Troubleshooting

### Database Save Failed

If you see the warning "Database save failed", check:

1. **Database initialized?**
   ```bash
   python scripts/init_database.py
   ```

2. **Environment configured?**
   ```bash
   # Check .env file
   USE_SQLITE=true
   ```

3. **Permissions?**
   - Ensure write access to project directory

### View Database Contents

```bash
# SQLite
sqlite3 pca_agent.db "SELECT COUNT(*) FROM campaigns;"

# Or use Python
python test_db_integration.py
```

## Next Steps

1. **Add Database Health Check** to sidebar
2. **Show Campaign History** from database
3. **Export from Database** functionality
4. **Database Analytics Dashboard**

---

**Status**: ✅ **INTEGRATED**  
**Date**: December 1, 2024  
**Version**: 2.1.0
