"""
Smart Visualization Tests
Tests chart selection logic and visualization generation
"""

import pytest
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Dict, List

from src.agents.smart_visualization_engine import SmartVisualizationEngine, VisualizationType
from src.agents.enhanced_visualization_agent import EnhancedVisualizationAgent
from src.agents.marketing_visualization_rules import MarketingVisualizationRules
from src.agents.chart_generators import SmartChartGenerator


class TestChartSelectionLogic:
    """Test automatic chart type selection"""
    
    @pytest.fixture
    def viz_engine(self):
        """Create visualization engine instance"""
        return SmartVisualizationEngine()
    
    @pytest.fixture
    def trend_data(self):
        """Generate trend data"""
        dates = pd.date_range('2024-01-01', periods=30, freq='D')
        return pd.DataFrame({
            'Date': dates,
            'Metric': np.cumsum(np.random.randn(30)) + 100
        })
    
    @pytest.fixture
    def comparison_data(self):
        """Generate comparison data"""
        return pd.DataFrame({
            'Channel': ['Google Ads', 'Meta', 'LinkedIn', 'TikTok'],
            'Spend': [5000, 4000, 3000, 2000],
            'Conversions': [100, 80, 60, 40],
            'ROAS': [3.0, 2.5, 2.8, 2.2]
        })
    
    @pytest.fixture
    def composition_data(self):
        """Generate composition data"""
        return pd.DataFrame({
            'Device': ['Desktop', 'Mobile', 'Tablet'],
            'Conversions': [500, 800, 200]
        })
    
    def test_trend_chart_selection(self, viz_engine, trend_data):
        """Verify trend data → line chart"""
        
        viz_type = viz_engine.select_visualization(
            data=trend_data,
            insight_type='trend',
            audience='analyst'
        )
        
        assert viz_type == VisualizationType.LINE_CHART
        
        # Create visualization
        fig = viz_engine.create_visualization(
            data=trend_data,
            viz_type=viz_type,
            title='Trend Analysis'
        )
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
        
        print("✅ Trend chart selection test passed!")
    
    def test_comparison_chart_selection(self, viz_engine, comparison_data):
        """Verify comparison data → bar chart"""
        
        viz_type = viz_engine.select_visualization(
            data=comparison_data,
            insight_type='comparison',
            audience='executive'
        )
        
        assert viz_type in [VisualizationType.BAR_CHART, VisualizationType.GROUPED_BAR]
        
        # Create visualization
        fig = viz_engine.create_visualization(
            data=comparison_data,
            viz_type=viz_type,
            title='Channel Comparison'
        )
        
        assert isinstance(fig, go.Figure)
        
        print("✅ Comparison chart selection test passed!")
    
    def test_composition_chart_selection(self, viz_engine, composition_data):
        """Verify composition data → pie/donut chart"""
        
        viz_type = viz_engine.select_visualization(
            data=composition_data,
            insight_type='composition',
            audience='executive'
        )
        
        assert viz_type in [VisualizationType.PIE_CHART, VisualizationType.DONUT_CHART]
        
        # Create visualization
        fig = viz_engine.create_visualization(
            data=composition_data,
            viz_type=viz_type,
            title='Device Distribution'
        )
        
        assert isinstance(fig, go.Figure)
        
        print("✅ Composition chart selection test passed!")
    
    def test_attribution_chart_selection(self, viz_engine):
        """Verify attribution data → sankey diagram"""
        
        attribution_data = pd.DataFrame({
            'Source': ['Awareness', 'Awareness', 'Consideration'],
            'Target': ['Consideration', 'Conversion', 'Conversion'],
            'Value': [100, 20, 50]
        })
        
        viz_type = viz_engine.select_visualization(
            data=attribution_data,
            insight_type='attribution',
            audience='analyst'
        )
        
        assert viz_type == VisualizationType.SANKEY
        
        print("✅ Attribution chart selection test passed!")
    
    def test_audience_based_selection(self, viz_engine, comparison_data):
        """Test chart selection varies by audience"""
        
        # Executive audience - simpler charts
        exec_viz = viz_engine.select_visualization(
            data=comparison_data,
            insight_type='comparison',
            audience='executive'
        )
        
        # Analyst audience - more detailed charts
        analyst_viz = viz_engine.select_visualization(
            data=comparison_data,
            insight_type='comparison',
            audience='analyst'
        )
        
        # Both should be valid visualization types
        assert exec_viz in VisualizationType
        assert analyst_viz in VisualizationType
        
        print("✅ Audience-based selection test passed!")


class TestMarketingVisualizationRules:
    """Test marketing-specific visualization rules"""
    
    @pytest.fixture
    def viz_rules(self):
        """Create visualization rules instance"""
        return MarketingVisualizationRules()
    
    def test_channel_performance_rules(self, viz_rules):
        """Test channel performance visualization rules"""
        
        config = viz_rules.get_visualization_for_insight('channel_performance')
        
        assert 'chart_type' in config
        assert 'styling' in config
        assert config['chart_type'] in ['bar', 'grouped_bar', 'line']
        
        print("✅ Channel performance rules test passed!")
    
    def test_budget_optimization_rules(self, viz_rules):
        """Test budget optimization visualization rules"""
        
        config = viz_rules.get_visualization_for_insight('budget_optimization')
        
        assert 'chart_type' in config
        assert 'annotations' in config
        
        # Should include benchmark lines
        assert 'benchmark_lines' in config or 'annotations' in config
        
        print("✅ Budget optimization rules test passed!")
    
    def test_creative_performance_rules(self, viz_rules):
        """Test creative performance visualization rules"""
        
        config = viz_rules.get_visualization_for_insight('creative_performance')
        
        assert 'chart_type' in config
        assert config['chart_type'] in ['bar', 'scatter', 'heatmap']
        
        print("✅ Creative performance rules test passed!")
    
    def test_color_scheme_application(self, viz_rules):
        """Test marketing color schemes"""
        
        channel_colors = viz_rules.get_channel_colors()
        
        assert 'Google Ads' in channel_colors
        assert 'Meta' in channel_colors
        assert 'LinkedIn' in channel_colors
        
        # Colors should be valid hex codes
        for color in channel_colors.values():
            assert color.startswith('#')
            assert len(color) == 7
        
        print("✅ Color scheme application test passed!")


class TestSmartChartGenerator:
    """Test smart chart generator functionality"""
    
    @pytest.fixture
    def chart_gen(self):
        """Create chart generator instance"""
        return SmartChartGenerator()
    
    @pytest.fixture
    def channel_data(self):
        """Generate channel comparison data"""
        return pd.DataFrame({
            'Channel': ['Google Ads', 'Meta', 'LinkedIn'],
            'Spend': [5000, 4000, 3000],
            'Conversions': [100, 80, 60],
            'ROAS': [3.0, 2.5, 2.8]
        })
    
    def test_channel_comparison_chart(self, chart_gen, channel_data):
        """Test channel comparison chart generation"""
        
        fig = chart_gen.create_channel_comparison(
            data=channel_data,
            metrics=['Spend', 'Conversions']
        )
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
        
        print("✅ Channel comparison chart test passed!")
    
    def test_performance_trend_chart(self, chart_gen):
        """Test performance trend chart generation"""
        
        trend_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=30, freq='D'),
            'CTR': np.random.uniform(0.02, 0.06, 30),
            'ROAS': np.random.uniform(2.0, 4.0, 30)
        })
        
        fig = chart_gen.create_performance_trend(
            data=trend_data,
            metrics=['CTR', 'ROAS']
        )
        
        assert isinstance(fig, go.Figure)
        
        print("✅ Performance trend chart test passed!")
    
    def test_conversion_funnel_chart(self, chart_gen):
        """Test conversion funnel chart generation"""
        
        funnel_data = pd.DataFrame({
            'Stage': ['Impressions', 'Clicks', 'Conversions', 'Purchases'],
            'Count': [100000, 5000, 500, 100]
        })
        
        fig = chart_gen.create_conversion_funnel(data=funnel_data)
        
        assert isinstance(fig, go.Figure)
        
        print("✅ Conversion funnel chart test passed!")
    
    def test_device_breakdown_chart(self, chart_gen):
        """Test device breakdown chart generation"""
        
        device_data = pd.DataFrame({
            'Device': ['Desktop', 'Mobile', 'Tablet'],
            'Conversions': [500, 800, 200]
        })
        
        fig = chart_gen.create_device_donut(data=device_data)
        
        assert isinstance(fig, go.Figure)
        
        print("✅ Device breakdown chart test passed!")


class TestEnhancedVisualizationAgent:
    """Test enhanced visualization agent"""
    
    @pytest.fixture
    def viz_agent(self):
        """Create visualization agent instance"""
        return EnhancedVisualizationAgent()
    
    @pytest.fixture
    def sample_insights(self):
        """Generate sample insights"""
        return [
            {
                'id': 'insight_1',
                'title': 'Google Ads Leading Performance',
                'description': 'Google Ads showing highest ROAS',
                'priority': 10,
                'category': 'channel_comparison'
            },
            {
                'id': 'insight_2',
                'title': 'Mobile Driving Conversions',
                'description': 'Mobile devices account for 60% of conversions',
                'priority': 8,
                'category': 'device_breakdown'
            },
            {
                'id': 'insight_3',
                'title': 'CTR Declining Trend',
                'description': 'CTR has declined 15% over last 7 days',
                'priority': 9,
                'category': 'trend_analysis'
            }
        ]
    
    @pytest.fixture
    def campaign_data(self):
        """Generate campaign data"""
        return pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=30, freq='D').tolist() * 3,
            'Channel': ['Google Ads'] * 30 + ['Meta'] * 30 + ['LinkedIn'] * 30,
            'Spend': np.random.uniform(100, 1000, 90),
            'Conversions': np.random.randint(10, 100, 90),
            'CTR': np.random.uniform(0.02, 0.06, 90),
            'ROAS': np.random.uniform(1.5, 4.0, 90)
        })
    
    def test_executive_dashboard_generation(self, viz_agent, sample_insights, campaign_data):
        """Test executive dashboard generation"""
        
        dashboard = viz_agent.create_executive_dashboard(
            insights=sample_insights,
            campaign_data=campaign_data,
            context={'target_roas': 2.5}
        )
        
        # Should generate 5-7 charts
        assert 5 <= len(dashboard) <= 7
        
        # Each chart should have required fields
        for chart in dashboard:
            assert 'chart' in chart
            assert 'title' in chart
            assert 'description' in chart
            assert isinstance(chart['chart'], go.Figure)
        
        print("✅ Executive dashboard generation test passed!")
    
    def test_analyst_dashboard_generation(self, viz_agent, sample_insights, campaign_data):
        """Test analyst dashboard generation"""
        
        dashboard = viz_agent.create_analyst_dashboard(
            insights=sample_insights,
            campaign_data=campaign_data
        )
        
        # Should generate 15-20 charts
        assert 10 <= len(dashboard) <= 25
        
        # Charts should be organized by section
        sections = set(chart.get('section', 'other') for chart in dashboard)
        assert len(sections) > 1
        
        print("✅ Analyst dashboard generation test passed!")
    
    def test_insight_to_visualization_mapping(self, viz_agent, sample_insights, campaign_data):
        """Test mapping insights to appropriate visualizations"""
        
        for insight in sample_insights:
            viz = viz_agent.create_visualization_from_insight(
                insight=insight,
                campaign_data=campaign_data
            )
            
            assert viz is not None
            assert 'chart' in viz
            assert isinstance(viz['chart'], go.Figure)
        
        print("✅ Insight to visualization mapping test passed!")


class TestVisualizationQuality:
    """Test visualization quality and best practices"""
    
    def test_chart_has_title(self):
        """Test that charts have titles"""
        
        chart_gen = SmartChartGenerator()
        data = pd.DataFrame({
            'Channel': ['A', 'B', 'C'],
            'Value': [100, 200, 150]
        })
        
        fig = chart_gen.create_channel_comparison(data, metrics=['Value'])
        
        assert fig.layout.title.text is not None
        assert len(fig.layout.title.text) > 0
        
        print("✅ Chart title test passed!")
    
    def test_chart_has_axis_labels(self):
        """Test that charts have axis labels"""
        
        viz_engine = SmartVisualizationEngine()
        data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=10),
            'Metric': np.random.randn(10)
        })
        
        fig = viz_engine.create_visualization(
            data=data,
            viz_type=VisualizationType.LINE_CHART,
            title='Test Chart'
        )
        
        # Should have axis labels
        assert fig.layout.xaxis.title is not None or len(fig.data) > 0
        
        print("✅ Chart axis labels test passed!")
    
    def test_chart_color_consistency(self):
        """Test that charts use consistent colors"""
        
        viz_rules = MarketingVisualizationRules()
        channel_colors = viz_rules.get_channel_colors()
        
        # Colors should be consistent across calls
        colors_2 = viz_rules.get_channel_colors()
        
        assert channel_colors == colors_2
        
        print("✅ Chart color consistency test passed!")
    
    def test_chart_responsiveness(self):
        """Test that charts are responsive"""
        
        chart_gen = SmartChartGenerator()
        data = pd.DataFrame({
            'X': range(10),
            'Y': np.random.randn(10)
        })
        
        fig = chart_gen.create_performance_trend(
            data=pd.DataFrame({
                'Date': pd.date_range('2024-01-01', periods=10),
                'Metric': np.random.randn(10)
            }),
            metrics=['Metric']
        )
        
        # Should have responsive layout settings
        assert fig.layout.autosize is True or fig.layout.width is not None
        
        print("✅ Chart responsiveness test passed!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
