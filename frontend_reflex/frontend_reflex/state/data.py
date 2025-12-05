import reflex as rx
import pandas as pd
import numpy as np
import os
from typing import List, Dict, Any, Optional
from .auth import AuthState
from src.utils.data_validator import validate_and_clean_data

class DataState(AuthState):
    """State for handling data loading and processing."""
    
    # Exposed Metrics
    total_rows: int = 0
    total_spend: str = "$0.00"
    total_clicks: str = "0"
    total_conversions: str = "0"
    total_impressions: str = "0"
    columns: List[str] = []
    
    # Validation info
    validation_summary: str = ""
    
    # Internal dataframe storage (not sent to client)
    _df: Optional[pd.DataFrame] = None
    
    def load_sample_data(self):
        """Load the sample dataset."""
        self.log("Loading sample data...")
        try:
            import src
            root_path = self.get_project_root()
            sample_csv = os.path.join(root_path, "data", "historical_campaigns_sample.csv")
            
            if os.path.exists(sample_csv):
                df = pd.read_csv(sample_csv)
                self.process_dataframe(df)
            else:
                print(f"Sample data not found at {sample_csv}")
                return rx.window_alert("Sample data file not found.")
                
        except Exception as e:
            print(f"Error loading sample data: {e}")
            return rx.window_alert(f"Error loading data: {str(e)}")

    async def handle_upload(self, files: list):
        """Handle file upload."""
        self.log(f"Handling file upload: {len(files)} files")
        for file in files:
            upload_data = await file.read()
            from io import BytesIO
            try:
                df = pd.read_csv(BytesIO(upload_data))
                self.process_dataframe(df)
            except Exception as e:
                return rx.window_alert(f"Error parsing CSV: {str(e)}")

    def compute_metrics(self, df: pd.DataFrame):
        """Compute summary metrics from the dataframe."""
        if df is None:
            return

        self.total_rows = len(df)
        self.columns = df.columns.tolist()
        
        if 'Spend' in df.columns:
            self.total_spend = f"${df['Spend'].sum():,.2f}"
        
        if 'Clicks' in df.columns:
            self.total_clicks = f"{df['Clicks'].sum():,.0f}"
            
        if 'Conversions' in df.columns:
            self.total_conversions = f"{df['Conversions'].sum():,.0f}"
            
        if 'Impressions' in df.columns:
            self.total_impressions = f"{df['Impressions'].sum():,.0f}"

    def process_dataframe(self, df: pd.DataFrame):
        """Validate and process the dataframe."""
        self.log(f"Processing dataframe with shape: {df.shape}")
        try:
            cleaned_df, report = validate_and_clean_data(df)
            self._df = cleaned_df
            self.log(f"Data validation complete. Cleaned rows: {len(cleaned_df)}")
            
            # Update metrics
            self.compute_metrics(cleaned_df)
                
            self.validation_summary = f"Loaded {self.total_rows} rows. {report['summary']['cleaned_rows']} valid."
            
        except Exception as e:
            print(f"Error processing dataframe: {e}")
            return rx.window_alert(f"Validation error: {str(e)}")

    def get_project_root(self):
        from pathlib import Path
        import os
        current = Path(os.getcwd())
        if (current / "src").exists():
            return str(current)
        if (current.parent / "src").exists():
            return str(current.parent)
        return "/Users/ashwin/Desktop/pca_agent"

    def clear_data(self):
        """Clear the current dataset."""
        self._df = None
        self.total_rows = 0
        self.total_spend = "$0.00"
        self.total_clicks = "0"
        self.total_conversions = "0"
        self.total_impressions = "0"
        self.columns = []
        self.validation_summary = ""
