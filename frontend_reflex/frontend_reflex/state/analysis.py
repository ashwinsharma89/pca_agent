import reflex as rx
from typing import Dict, Any, List, Optional
from .filter import FilterState
from src.analytics import MediaAnalyticsExpert

class AnalysisState(FilterState):
    """State for AI Analysis."""
    
    # Analysis Options
    use_rag: bool = True
    include_benchmarks: bool = True
    depth: str = "Standard"
    
    # Results
    analysis_complete: bool = False
    executive_summary: str = ""
    detailed_summary: str = ""
    insights: List[str] = []
    recommendations: List[str] = []
    
    # Progress
    is_analyzing: bool = False
    
    def run_analysis(self):
        """Run the AI analysis on the current data."""
        # Use filtered_df property
        df = self.filtered_df
        
        if df is None or df.empty:
            return rx.window_alert("No data loaded or data is empty after filtering.")
            
        self.is_analyzing = True
        yield
        
        try:
            analytics = MediaAnalyticsExpert()
            
            # Run analysis
            results = analytics.analyze_all(
                df, # Use filtered df
                use_parallel=True
            )
            
            if results:
                summary = results.get('executive_summary', {})
                if isinstance(summary, dict):
                    self.executive_summary = summary.get('brief', "Analysis complete.")
                    self.detailed_summary = summary.get('detailed', "")
                else:
                    self.executive_summary = str(summary)
                
                self.insights = results.get('insights', [])
                self.recommendations = results.get('recommendations', [])
                self.analysis_complete = True
            else:
                return rx.window_alert("Analysis failed to generate results.")
                
        except Exception as e:
            print(f"Analysis error: {e}")
            self.log(f"Analysis error: {e}", level="error")
            return rx.window_alert(f"Analysis Error: {str(e)}")
        finally:
            self.is_analyzing = False
