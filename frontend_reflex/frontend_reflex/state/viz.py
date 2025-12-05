import reflex as rx
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import List, Any, Dict, Optional
from .analysis import AnalysisState

class VizState(AnalysisState):
    """State for Visualizations and Deep Dive charts."""
    
    # Custom Chart Controls
    chart_type: str = "Bar Chart"
    x_axis: str = ""
    y_axis: str = ""
    color_by: str = "None"
    aggregation: str = "Sum"
    
    # Generated Chart
    custom_chart_figure: Optional[go.Figure] = None
    
    # Pre-defined Charts
    funnel_figure: Optional[go.Figure] = None
    correlation_figure: Optional[go.Figure] = None
    
    # KPI Comparison Controls
    selected_kpis: List[str] = []
    primary_kpi: str = "Spend"
    compare_dimension: str = "Platform"
    comparison_chart_type: str = "Grouped Bar"
    normalize: bool = False
    comparison_chart_figure: Optional[go.Figure] = None

    @rx.var
    def color_options(self) -> List[str]:
        return self.columns + ["None"]

    def set_primary_kpi(self, value: str):
        self.primary_kpi = value
    
    def set_color_by(self, value: str):
        self.color_by = value

    def set_chart_type(self, value: str):
        self.chart_type = value

    def update_x_axis(self, value: str):
        self.x_axis = value
        
    def update_y_axis(self, value: str):
        self.y_axis = value

    def set_aggregation(self, value: str):
        self.aggregation = value

    def set_compare_dimension(self, value: str):
        self.compare_dimension = value
        
    def toggle_kpi(self, kpi: str, checked: bool):
        if checked:
            if len(self.selected_kpis) >= 3:
                return rx.window_alert("Max 3 KPIs allowed.")
            self.selected_kpis.append(kpi)
        else:
            if kpi in self.selected_kpis:
                self.selected_kpis.remove(kpi)

    def generate_custom_chart(self):
        """Generate the custom chart based on selections."""
        df = self.filtered_df
        if df is None or df.empty:
            return
            
        if not self.x_axis or not self.y_axis:
            return
            
        agg_map = {"Sum": "sum", "Mean": "mean", "Count": "count", "Max": "max", "Min": "min"}
        
        try:
            if self.chart_type == "Bar Chart":
                chart_data = df.groupby(self.x_axis)[self.y_axis].agg(agg_map[self.aggregation]).reset_index()
                if self.color_by != "None":
                    chart_data = df.groupby([self.x_axis, self.color_by])[self.y_axis].agg(agg_map[self.aggregation]).reset_index()
                    fig = px.bar(chart_data, x=self.x_axis, y=self.y_axis, color=self.color_by)
                else:
                    fig = px.bar(chart_data, x=self.x_axis, y=self.y_axis)
            
            elif self.chart_type == "Line Chart":
                chart_data = df.groupby(self.x_axis)[self.y_axis].agg(agg_map[self.aggregation]).reset_index()
                fig = px.line(chart_data, x=self.x_axis, y=self.y_axis)
                
            elif self.chart_type == "Scatter Plot":
                fig = px.scatter(df, x=self.x_axis, y=self.y_axis, 
                               color=self.color_by if self.color_by != "None" else None)
                               
            elif self.chart_type == "Pie Chart":
                chart_data = df.groupby(self.x_axis)[self.y_axis].agg(agg_map[self.aggregation]).reset_index()
                fig = px.pie(chart_data, values=self.y_axis, names=self.x_axis)
            
            else:
                chart_data = df.groupby(self.x_axis)[self.y_axis].sum().reset_index()
                fig = px.bar(chart_data, x=self.x_axis, y=self.y_axis)
                
            fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            self.custom_chart_figure = fig 
            
        except Exception as e:
            self.log(f"Chart gen error: {e}", level="error")
            return rx.window_alert(f"Chart Error: {e}")

    def generate_funnel_chart(self):
        """Generate a funnel chart."""
        df = self.filtered_df
        if df is None or df.empty:
            return

        try:
            # Aggregate metrics
            metrics = ['Impressions', 'Clicks', 'Conversions']
            values = []
            for m in metrics:
                if m in df.columns:
                    values.append(df[m].sum())
                else:
                    values.append(0)
            
            fig = go.Figure(go.Funnel(
                y=metrics,
                x=values,
                textinfo="value+percent initial"
            ))
            fig.update_layout(title="Conversion Funnel", template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            self.funnel_figure = fig
            
        except Exception as e:
            self.log(f"Funnel error: {e}", level="error")

    def generate_correlation_matrix(self):
        """Generate correlation matrix."""
        df = self.filtered_df
        if df is None or df.empty:
            return

        try:
            # Select numeric columns
            numeric_df = df.select_dtypes(include=[np.number])
            if numeric_df.empty:
                return
                
            corr = numeric_df.corr()
            
            fig = px.imshow(corr, text_auto=True, aspect="auto", color_continuous_scale='RdBu_r')
            fig.update_layout(title="Correlation Matrix", template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            self.correlation_figure = fig
            
        except Exception as e:
            self.log(f"Correlation error: {e}", level="error")

    def generate_comparison_chart(self):
        """Generate scale-adjusted comparison."""
        df = self.filtered_df
        if df is None or not self.selected_kpis:
            return

        try:
            # Group by dimension
            grouped = df.groupby(self.compare_dimension)[self.selected_kpis].sum().reset_index()
            
            fig = go.Figure()
            
            for i, kpi in enumerate(self.selected_kpis):
                # Normalize logic (simple min-max for demo, or secondary axis)
                # Here we will use relative change if needed, but for now simple grouped bar
                fig.add_trace(go.Bar(
                    name=kpi,
                    x=grouped[self.compare_dimension],
                    y=grouped[kpi],
                    # yaxis=f"y{i+1}"
                ))
            
            fig.update_layout(
                barmode='group',
                title=f"Comparison by {self.compare_dimension}",
                template='plotly_dark', 
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)'
            )
            self.comparison_chart_figure = fig
            
        except Exception as e:
            self.log(f"Comparison error: {e}", level="error")
