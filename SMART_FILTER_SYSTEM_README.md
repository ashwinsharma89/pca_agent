# Smart Filter System for Intelligent Visualizations

## 🎯 Overview

The Smart Filter System provides intelligent, context-aware filtering capabilities for campaign data visualizations. It automatically suggests relevant filters based on data characteristics and provides powerful filtering options with impact analysis.

---

## 📊 Key Features

### **1. Intelligent Filter Suggestions**
- Analyzes data characteristics
- Suggests relevant filters automatically
- Prioritizes filters by importance
- Provides reasoning for each suggestion

### **2. Comprehensive Filter Types**
- **Temporal**: Date ranges, presets, comparisons
- **Dimensional**: Channel, campaign, device, geography
- **Performance**: Thresholds, tiers, benchmarks
- **Advanced**: Statistical significance, anomaly detection

### **3. Filter Impact Analysis**
- Tracks filter application history
- Provides impact summaries
- Generates warnings for aggressive/ineffective filters
- Recommends filter adjustments

---

## 🔧 Filter Types

### **Temporal Filters**

#### **Date Range**
```python
{
    'type': FilterType.DATE_RANGE,
    'start_date': '2024-01-01',
    'end_date': '2024-01-31'
}
```

#### **Date Presets**
```python
{
    'type': FilterType.DATE_PRESET,
    'preset': 'last_30_days'  # Options: last_7_days, last_30_days, last_90_days, etc.
}
```

#### **Date Comparison**
```python
{
    'type': FilterType.DATE_COMPARISON,
    'comparison': 'month_over_month'  # week_over_week, year_over_year
}
```

---

### **Dimensional Filters**

#### **Channel Filter**
```python
{
    'type': FilterType.CHANNEL,
    'column': 'channel',
    'values': ['Google Ads', 'Meta', 'LinkedIn']
}
```

#### **Campaign Filter**
```python
{
    'type': FilterType.CAMPAIGN,
    'column': 'campaign',
    'values': ['Brand Awareness', 'Lead Gen']
}
```

#### **Device Filter**
```python
{
    'type': FilterType.DEVICE,
    'column': 'device',
    'values': ['Mobile', 'Desktop']
}
```

---

### **Performance Filters**

#### **Metric Threshold**
```python
{
    'type': FilterType.METRIC_THRESHOLD,
    'conditions': [
        {'metric': 'ctr', 'operator': '>', 'value': 0.035},
        {'metric': 'spend', 'operator': '>=', 'value': 1000},
        {'metric': 'cpa', 'operator': 'between', 'value': (30, 60)}
    ]
}
```

**Operators**: `>`, `>=`, `<`, `<=`, `==`, `!=`, `between`

#### **Performance Tier**
```python
{
    'type': FilterType.PERFORMANCE_TIER,
    'tier': 'top',  # 'top', 'middle', 'bottom'
    'metric': 'roas'
}
```

- **Top**: Top 20% performers
- **Middle**: 21-80% performers
- **Bottom**: Bottom 20% performers

#### **Benchmark Relative**
```python
{
    'type': FilterType.BENCHMARK_RELATIVE,
    'comparison': 'above',  # 'above', 'below', 'at'
    'benchmarks': {'ctr': 0.035, 'roas': 2.5},
    'tolerance': 0.1  # ±10% for 'at' comparison
}
```

---

### **Advanced Filters**

#### **Statistical Significance**
```python
{
    'type': FilterType.STATISTICAL,
    'alpha': 0.05  # p-value threshold
}
```

Filters for statistically significant results only (requires `p_value` column).

#### **Anomaly Detection**
```python
{
    'type': FilterType.ANOMALY,
    'mode': 'anomalies_only',  # 'anomalies_only', 'normal_only', 'all'
    'metric': 'roas',
    'threshold': 2  # Z-score threshold (standard deviations)
}
```

---

## 🚀 Usage

### **Basic Usage**

```python
from src.agents.visualization_filters import SmartFilterEngine, FilterType
import pandas as pd

# Initialize filter engine
filter_engine = SmartFilterEngine()

# Your campaign data
campaign_data = pd.DataFrame({...})

# Get smart filter suggestions
context = {
    'business_model': 'B2B',
    'benchmarks': {'ctr': 0.035, 'roas': 2.5}
}

suggestions = filter_engine.suggest_filters_for_data(campaign_data, context)

# Review suggestions
for suggestion in suggestions:
    print(f"{suggestion['label']}: {suggestion['reasoning']}")
```

### **Applying Filters**

```python
# Define filters
filters = {
    'date_filter': {
        'type': FilterType.DATE_PRESET,
        'preset': 'last_30_days'
    },
    'channel_filter': {
        'type': FilterType.CHANNEL,
        'column': 'channel',
        'values': ['Google Ads', 'Meta']
    },
    'performance_filter': {
        'type': FilterType.METRIC_THRESHOLD,
        'conditions': [
            {'metric': 'ctr', 'operator': '>', 'value': 0.03}
        ]
    }
}

# Apply filters
filtered_data = filter_engine.apply_filters(campaign_data, filters)

print(f"Original: {len(campaign_data)} rows")
print(f"Filtered: {len(filtered_data)} rows")
```

### **Filter Impact Analysis**

```python
# Get impact summary
impact = filter_engine.get_filter_impact_summary()

print(f"Rows removed: {impact['rows_removed']}")
print(f"Reduction: {impact['reduction_percentage']:.1f}%")

# Check for warnings
if impact.get('warnings'):
    for warning in impact['warnings']:
        print(f"[{warning['severity']}] {warning['message']}")
        print(f"Suggestion: {warning['suggestion']}")
```

---

## 📈 Complete Example

```python
from src.agents.visualization_filters import SmartFilterEngine, FilterType
import pandas as pd

# Initialize
filter_engine = SmartFilterEngine()

# Load data
campaign_data = pd.read_csv('campaign_data.csv')

# Step 1: Get suggestions
context = {'business_model': 'B2B', 'benchmarks': {'roas': 2.5}}
suggestions = filter_engine.suggest_filters_for_data(campaign_data, context)

print(f"Suggested {len(suggestions)} filters:")
for s in suggestions:
    print(f"  • {s['label']} ({s['priority']} priority)")

# Step 2: Apply filters
filters = {
    'date': {
        'type': FilterType.DATE_PRESET,
        'preset': 'last_30_days'
    },
    'channels': {
        'type': FilterType.CHANNEL,
        'column': 'channel',
        'values': ['Google Ads', 'Meta']
    },
    'performance': {
        'type': FilterType.PERFORMANCE_TIER,
        'tier': 'top',
        'metric': 'roas'
    }
}

filtered_data = filter_engine.apply_filters(campaign_data, filters)

# Step 3: Analyze impact
impact = filter_engine.get_filter_impact_summary()
print(f"\nFilter Impact:")
print(f"  Original: {impact['rows_original']} rows")
print(f"  Filtered: {impact['rows_filtered']} rows")
print(f"  Reduction: {impact['reduction_percentage']:.1f}%")

# Step 4: Use filtered data for visualization
# ... create visualizations with filtered_data
```

---

## 🎯 Filter Suggestions Logic

### **High Priority Filters**
Suggested when:
- Multiple channels detected → Channel filter
- Benchmarks available → Benchmark relative filter
- A/B test detected → Statistical significance filter
- Time series data → Date preset filter

### **Medium Priority Filters**
Suggested when:
- Performance metrics available → Performance tier filter
- Multiple campaigns → Campaign filter
- Numeric metrics available → Metric threshold filter
- B2B context → Funnel stage filter

### **Low Priority Filters**
Suggested when:
- Multiple devices → Device filter
- Sufficient historical data → Anomaly filter
- Geographic data → Geography filter

---

## ⚠️ Filter Warnings

### **High Severity**
- **Over-filtering**: Filters removed >90% of data
- **Action**: Consider relaxing filters or expanding date range

### **Medium Severity**
- **Small sample**: <30 rows remaining
- **Action**: Sample size may be too small for reliable insights

### **Low Severity**
- **Under-filtering**: Filters removed <5% of data
- **Action**: Filters may not provide meaningful segmentation

---

## 🔄 Integration with Visualization Framework

```python
from src.agents.enhanced_visualization_agent import EnhancedVisualizationAgent
from src.agents.visualization_filters import SmartFilterEngine

# Initialize
viz_agent = EnhancedVisualizationAgent()
filter_engine = SmartFilterEngine()

# Apply filters
filters = {...}
filtered_data = filter_engine.apply_filters(campaign_data, filters)

# Create visualizations with filtered data
dashboard = viz_agent.create_executive_dashboard(
    insights=insights,
    campaign_data=filtered_data,  # Use filtered data
    context=context
)
```

---

## 📊 Filter Combinations

### **Example 1: Focus on Recent High Performers**
```python
filters = {
    'date': {'type': FilterType.DATE_PRESET, 'preset': 'last_30_days'},
    'tier': {'type': FilterType.PERFORMANCE_TIER, 'tier': 'top', 'metric': 'roas'}
}
```

### **Example 2: Mobile Performance Analysis**
```python
filters = {
    'device': {'type': FilterType.DEVICE, 'column': 'device', 'values': ['Mobile']},
    'metrics': {
        'type': FilterType.METRIC_THRESHOLD,
        'conditions': [{'metric': 'ctr', 'operator': '>', 'value': 0.04}]
    }
}
```

### **Example 3: Underperforming Campaigns**
```python
filters = {
    'benchmark': {
        'type': FilterType.BENCHMARK_RELATIVE,
        'comparison': 'below',
        'benchmarks': {'roas': 2.5}
    },
    'tier': {'type': FilterType.PERFORMANCE_TIER, 'tier': 'bottom', 'metric': 'roas'}
}
```

---

## 🎨 Best Practices

### **1. Start with Suggestions**
```python
# Always get suggestions first
suggestions = filter_engine.suggest_filters_for_data(data, context)
# Then apply relevant ones
```

### **2. Monitor Impact**
```python
# Check impact after applying filters
impact = filter_engine.get_filter_impact_summary()
if impact['reduction_percentage'] > 90:
    print("Warning: Over-filtering detected!")
```

### **3. Combine Thoughtfully**
```python
# Don't over-combine filters
# Good: Date + Channel + Performance tier
# Bad: Date + Channel + Device + Campaign + 5 metric thresholds
```

### **4. Use Appropriate Operators**
```python
# For ranges, use 'between'
{'metric': 'cpa', 'operator': 'between', 'value': (30, 60)}

# Not multiple conditions
# {'metric': 'cpa', 'operator': '>=', 'value': 30}
# {'metric': 'cpa', 'operator': '<=', 'value': 60}
```

---

## 📈 Performance Considerations

### **Filter Order**
Filters are applied in the order specified. For best performance:
1. Date filters first (usually most selective)
2. Dimensional filters (channel, campaign)
3. Performance filters last

### **Data Size**
- Small datasets (<1000 rows): All filters work well
- Medium datasets (1K-100K rows): Consider filter combinations
- Large datasets (>100K rows): Use date filters first to reduce size

---

## ✨ Summary

**What the Filter System Provides**:
- ✅ Intelligent filter suggestions
- ✅ 10+ filter types
- ✅ Automatic impact analysis
- ✅ Warning system
- ✅ Filter history tracking
- ✅ Context-aware recommendations

**Key Capabilities**:
- 🎯 Smart suggestions based on data
- 📊 Comprehensive filter types
- 🔍 Impact analysis
- ⚠️ Warning system
- 🔄 Easy integration
- 📈 Performance optimized

**Use Cases**:
- Focus on specific time periods
- Analyze top/bottom performers
- Filter by channels or campaigns
- Identify anomalies
- Benchmark comparisons
- A/B test analysis

---

**🎉 SMART FILTER SYSTEM: COMPLETE AND PRODUCTION-READY! 🎉**

Your PCA Agent now has intelligent filtering capabilities that automatically suggest relevant filters, apply them efficiently, and provide impact analysis!
