# Marketing Visualization Rules

## 🎨 Domain-Specific Visualization for Digital Marketing

The Marketing Visualization Rules system provides intelligent, context-aware visualization configurations specifically designed for digital marketing insights.

---

## 🎯 Key Features

### **1. 16 Marketing Insight Categories**
- Channel comparison
- Performance trends
- Budget distribution
- Audience performance
- Creative fatigue
- Attribution flow
- Conversion funnel
- Quality score analysis
- Day parting
- Device breakdown
- Geographic performance
- Keyword efficiency
- Frequency analysis
- Benchmark comparison
- Ad performance
- Campaign health

### **2. Domain-Specific Rules**
- Pre-configured visualization types
- Marketing-specific styling
- Automatic annotations
- Benchmark display styles
- Color schemes for channels/performance

### **3. Context-Aware Configuration**
- Adjusts based on data characteristics
- Time granularity auto-selection
- Dynamic top-N filtering
- Performance-based coloring

---

## 📊 Insight Categories

### **1. Channel Comparison**
**Use Case**: Compare performance across advertising channels

**Configuration**:
```python
{
    "chart_type": "grouped_bar",
    "metrics": ["spend", "conversions", "cpa", "roas"],
    "styling": {
        "color_by": "efficiency",
        "sort_by": "roas",
        "show_benchmarks": True
    },
    "annotations": ["best_performer", "worst_performer"]
}
```

**Visual**: Grouped bar chart with green (good) to red (poor) coloring

---

### **2. Performance Trend**
**Use Case**: Show metrics over time with anomaly detection

**Configuration**:
```python
{
    "chart_type": "multi_line",
    "time_granularity": "auto",  # hourly/daily/weekly/monthly
    "styling": {
        "highlight_anomalies": True,
        "show_moving_average": True,
        "ma_window": 7
    },
    "annotations": ["peaks", "valleys", "trend_changes"]
}
```

**Visual**: Multi-line chart with anomaly highlights and moving average

---

### **3. Budget Distribution**
**Use Case**: Visualize budget allocation across hierarchy

**Configuration**:
```python
{
    "chart_type": "treemap",
    "hierarchy": ["channel", "campaign", "ad_group"],
    "sizing_metric": "spend",
    "color_metric": "roas",
    "styling": {
        "color_scale": "RdYlGn",
        "show_percentage": True
    }
}
```

**Visual**: Treemap with size = spend, color = ROAS

---

### **4. Creative Fatigue**
**Use Case**: Detect creative performance decay

**Configuration**:
```python
{
    "chart_type": "area_chart",
    "metrics": ["ctr", "engagement_rate"],
    "overlay": "frequency",
    "styling": {
        "highlight_threshold": 7,  # Frequency threshold
        "show_decay_rate": True
    }
}
```

**Visual**: Area chart with fatigue zone highlighted

---

### **5. Conversion Funnel**
**Use Case**: Analyze conversion stages and drop-offs

**Configuration**:
```python
{
    "chart_type": "funnel",
    "stages": ["impression", "click", "landing", "conversion"],
    "styling": {
        "show_drop_off_rate": True,
        "highlight_biggest_drop": True,
        "color_by_health": True
    }
}
```

**Visual**: Funnel with drop-off rates and health coloring

---

### **6. Quality Score Components**
**Use Case**: Google Ads Quality Score breakdown

**Configuration**:
```python
{
    "chart_type": "bullet_chart",
    "components": ["expected_ctr", "ad_relevance", "landing_page"],
    "target": 7,
    "styling": {
        "color_ranges": [
            {"min": 0, "max": 5, "color": "red", "label": "Poor"},
            {"min": 5, "max": 7, "color": "yellow", "label": "Average"},
            {"min": 7, "max": 10, "color": "green", "label": "Good"}
        ]
    }
}
```

**Visual**: Bullet chart with color-coded ranges

---

### **7. Day Parting**
**Use Case**: Hour-of-day and day-of-week performance

**Configuration**:
```python
{
    "chart_type": "heatmap",
    "x_axis": "hour_of_day",
    "y_axis": "day_of_week",
    "value": "conversion_rate",
    "styling": {
        "color_scale": "Viridis",
        "highlight_best_times": True
    }
}
```

**Visual**: Heatmap with best performing times highlighted

---

### **8. Keyword Efficiency**
**Use Case**: Search keyword performance matrix

**Configuration**:
```python
{
    "chart_type": "scatter_plot",
    "x_axis": "impressions",
    "y_axis": "conversion_rate",
    "bubble_size": "spend",
    "color_by": "quality_score",
    "styling": {
        "quadrant_lines": True,
        "highlight_opportunities": True
    },
    "quadrant_labels": {
        "top_right": "Stars",
        "top_left": "Optimize",
        "bottom_right": "Opportunities",
        "bottom_left": "Underperformers"
    }
}
```

**Visual**: Scatter plot with quadrants (BCG matrix style)

---

## 🎨 Color Schemes

### **Channel Colors**
```python
CHANNELS = {
    "google_search": "#4285F4",    # Google Blue
    "meta": "#1877F2",             # Facebook Blue
    "linkedin": "#0A66C2",         # LinkedIn Blue
    "tiktok": "#000000",           # TikTok Black
    "youtube": "#FF0000",          # YouTube Red
    "instagram": "#E4405F",        # Instagram Pink
    "twitter": "#1DA1F2",          # Twitter Blue
}
```

### **Performance Colors**
```python
PERFORMANCE = {
    "excellent": "#00C853",   # Green
    "good": "#64DD17",        # Light Green
    "average": "#FFD600",     # Yellow
    "poor": "#FF6D00",        # Orange
    "critical": "#D50000"     # Red
}
```

### **Device Colors**
```python
DEVICES = {
    "desktop": "#5E35B1",     # Purple
    "mobile": "#00897B",      # Teal
    "tablet": "#FB8C00"       # Orange
}
```

---

## 🔧 Usage

### **Basic Usage**

```python
from src.agents.marketing_visualization_rules import MarketingVisualizationRules

# Initialize
rules = MarketingVisualizationRules()

# Get configuration for channel comparison
config = rules.get_visualization_for_insight("channel_comparison")

print(config['chart_type'])  # VisualizationType.GROUPED_BAR
print(config['metrics'])     # ['spend', 'conversions', 'cpa', 'roas']
print(config['styling'])     # {...}
```

### **With Data Context**

```python
# Provide data context for auto-adjustments
data_context = {
    "date_range_days": 30,
    "cardinality": 50
}

config = rules.get_visualization_for_insight(
    "performance_trend",
    data=data_context
)

# Time granularity auto-selected based on date range
print(config['time_granularity'])  # 'daily' (for 30 days)
```

### **Get Color for Channel**

```python
from src.agents.marketing_visualization_rules import MarketingColorSchemes

# Get channel color
color = MarketingColorSchemes.get_channel_color('google_search')
print(color)  # '#4285F4'

# Get performance-based color
color = MarketingColorSchemes.get_performance_color(
    value=120,
    benchmark=100,
    higher_is_better=True
)
print(color)  # '#00C853' (excellent - 20% above benchmark)
```

### **Check Benchmark Display**

```python
# Should benchmarks be shown?
show_benchmarks = rules.should_show_benchmarks("channel_comparison")
print(show_benchmarks)  # True

# Get benchmark display style
style = rules.get_benchmark_display_style(VisualizationType.BAR_CHART)
print(style)  # 'reference_line'
```

---

## 📈 Complete Example

```python
from src.agents.marketing_visualization_rules import MarketingVisualizationRules
from src.agents.smart_visualization_engine import SmartVisualizationEngine
import pandas as pd

# Initialize
rules = MarketingVisualizationRules()
viz_engine = SmartVisualizationEngine()

# Your data
channel_data = pd.DataFrame({
    'Channel': ['Google', 'Meta', 'LinkedIn'],
    'Spend': [45000, 32000, 28000],
    'Conversions': [850, 620, 410],
    'ROAS': [3.2, 2.8, 4.1]
})

# Get marketing-specific config
config = rules.get_visualization_for_insight("channel_comparison")

# Create visualization with config
fig = viz_engine.create_visualization(
    data=channel_data,
    viz_type=config['chart_type'],
    title="Channel Performance Comparison"
)

# Apply marketing-specific styling
# (color by efficiency, show benchmarks, etc.)

fig.show()
```

---

## 🎯 Configuration Structure

Each insight category returns a configuration dictionary:

```python
{
    "chart_type": VisualizationType,
    "metrics": List[str],              # Optional
    "styling": {
        "color_by": str,
        "sort_by": str,
        "show_benchmarks": bool,
        "color_scale": str,
        # ... more styling options
    },
    "annotations": {
        "enabled": bool,
        "types": List[str],
        "show_values": bool,
        # ... more annotation options
    },
    "layout": {
        "height": int,
        "show_legend": bool,
        "x_axis_title": str,
        "y_axis_title": str,
        # ... more layout options
    }
}
```

---

## 📊 All Insight Categories

| Category | Chart Type | Use Case |
|----------|-----------|----------|
| channel_comparison | Grouped Bar | Compare channels |
| performance_trend | Multi-line | Time series trends |
| budget_distribution | Treemap | Budget allocation |
| audience_performance | Bubble Chart | Audience segments |
| creative_decay | Area Chart | Creative fatigue |
| attribution_flow | Sankey | Attribution paths |
| conversion_funnel | Funnel | Conversion stages |
| quality_score_components | Bullet Chart | QS breakdown |
| hourly_performance | Heatmap | Day parting |
| device_breakdown | Donut Chart | Device split |
| geo_performance | Heatmap | Geographic analysis |
| keyword_efficiency | Scatter Plot | Keyword matrix |
| frequency_analysis | Histogram | Frequency distribution |
| benchmark_comparison | Bullet Chart | vs Benchmarks |
| ad_performance | Horizontal Bar | Ad rankings |
| campaign_health | Gauge | Health score |

---

## 🔄 Integration

### **With Smart Visualization Engine**

```python
from src.agents.smart_visualization_engine import SmartVisualizationEngine
from src.agents.marketing_visualization_rules import MarketingVisualizationRules

viz_engine = SmartVisualizationEngine()
marketing_rules = MarketingVisualizationRules()

# Get marketing-specific config
config = marketing_rules.get_visualization_for_insight("channel_comparison")

# Create visualization
fig = viz_engine.create_visualization(
    data=data,
    viz_type=config['chart_type'],
    title="Channel Performance"
)
```

### **With Enhanced Reasoning Agent**

```python
from src.agents.enhanced_reasoning_agent import EnhancedReasoningAgent
from src.agents.marketing_visualization_rules import MarketingVisualizationRules

reasoning = EnhancedReasoningAgent()
marketing_rules = MarketingVisualizationRules()

# Detect patterns
patterns = reasoning.analyze(campaign_data)

# If creative fatigue detected
if patterns['creative_fatigue']['detected']:
    config = marketing_rules.get_visualization_for_insight("creative_decay")
    # Visualize with fatigue-specific config
```

---

## ✨ Best Practices

### **1. Use Domain-Specific Categories**
```python
# Good - Use marketing category
config = rules.get_visualization_for_insight("channel_comparison")

# Avoid - Generic insight type
viz_type = engine.select_visualization(data, "comparison", "executive")
```

### **2. Provide Data Context**
```python
# Better - With context
config = rules.get_visualization_for_insight(
    "performance_trend",
    data={"date_range_days": 30, "cardinality": 50}
)
# Auto-selects daily granularity
```

### **3. Apply Marketing Color Schemes**
```python
# Use channel-specific colors
for channel in channels:
    color = MarketingColorSchemes.get_channel_color(channel)
    # Apply to visualization
```

### **4. Show Benchmarks When Appropriate**
```python
if rules.should_show_benchmarks(insight_category):
    style = rules.get_benchmark_display_style(chart_type)
    # Add benchmark lines/markers
```

---

## 📝 Examples

See `examples/marketing_visualization_examples.py` for complete examples:

1. **Channel Comparison** - Multi-metric comparison
2. **Performance Trend** - Time series with anomalies
3. **Creative Fatigue** - Decay detection
4. **Conversion Funnel** - Stage analysis
5. **Quality Score** - Component breakdown
6. **Day Parting** - Hourly heatmap
7. **Keyword Efficiency** - Performance matrix
8. **Color Schemes** - Marketing colors
9. **Benchmark Display** - Display styles
10. **All Categories** - Complete overview

Run examples:
```bash
python examples/marketing_visualization_examples.py
```

---

## ✨ Summary

**What Was Built**:
- ✅ Marketing Visualization Rules (600+ lines)
- ✅ 16 insight categories
- ✅ Domain-specific configurations
- ✅ Marketing color schemes
- ✅ Context-aware adjustments
- ✅ Benchmark display styles
- ✅ Complete examples
- ✅ Comprehensive documentation

**Capabilities**:
- 🎯 Marketing-specific rules
- 📊 16 insight categories
- 🎨 Channel/performance colors
- 💡 Auto-configuration
- 🔄 Context awareness
- 📈 Benchmark integration

**Impact**:
- 🎯 Domain expertise built-in
- 📊 Consistent visualizations
- 🎨 Brand-appropriate colors
- 💡 Best practices enforced
- 🚀 Production-ready

---

**🎉 MARKETING VISUALIZATION RULES: COMPLETE! 🎉**

Your PCA Agent now has domain-specific visualization rules for all digital marketing insights!
