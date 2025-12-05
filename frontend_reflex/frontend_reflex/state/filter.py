import reflex as rx
from typing import List, Optional
import pandas as pd
from datetime import datetime
from .data import DataState

class FilterState(DataState):
    """Mixin for Global Filters."""
    
    # Filter Selections
    filter_date_range: List[str] = [] # [start, end]
    selected_platforms: List[str] = []
    selected_campaigns: List[str] = []
    
    # Filter Options
    available_platforms: List[str] = []
    available_campaigns: List[str] = []
    
    def set_date_range(self, dates: List[str]):
        self.filter_date_range = dates
        self.apply_filters()
        
    def set_selected_platforms(self, platforms: List[str]):
        self.selected_platforms = platforms
        self.apply_filters()
        
    def toggle_platform(self, platform: str, checked: bool):
        if checked:
            self.selected_platforms.append(platform)
        else:
            if platform in self.selected_platforms:
                self.selected_platforms.remove(platform)
        self.apply_filters()
        
    def set_selected_campaigns(self, campaigns: List[str]):
        self.selected_campaigns = campaigns
        self.apply_filters()

    def toggle_campaign(self, campaign: str, checked: bool):
        if checked:
            self.selected_campaigns.append(campaign)
        else:
            if campaign in self.selected_campaigns:
                self.selected_campaigns.remove(campaign)
        self.apply_filters()

    def update_filter_options(self):
        """Update available options based on data."""
        if self._df is not None:
             # Platforms
            if "Platform" in self._df.columns:
                self.available_platforms = sorted(self._df["Platform"].dropna().unique().tolist())
            
            # Campaigns
            if "Campaign" in self._df.columns:
                self.available_campaigns = sorted(self._df["Campaign"].dropna().unique().tolist())
            
            # Date Range default
            if not self.filter_date_range and self._df is not None:
                date_col = next((c for c in self._df.columns if 'date' in c.lower()), None)
                if date_col:
                     # Convert to datetime to find min/max
                     dates = pd.to_datetime(self._df[date_col], errors='coerce')
                     if not dates.empty:
                         self.filter_date_range = [
                             dates.min().strftime('%Y-%m-%d'),
                             dates.max().strftime('%Y-%m-%d')
                         ]

    def process_dataframe(self, df: pd.DataFrame):
        """Override to update options after processing."""
        super().process_dataframe(df)
        self.update_filter_options()

    def apply_filters(self):
        """Apply filters and update metrics."""
        df = self.filtered_df
        if df is not None:
            self.compute_metrics(df)

    @property
    def filtered_df(self) -> pd.DataFrame:
        """Return the dataframe filtered by current selections."""
        if self._df is None:
            return None
            
        df = self._df.copy()
        
        # Filter by Platform
        if self.selected_platforms:
            if "Platform" in df.columns:
                df = df[df["Platform"].isin(self.selected_platforms)]
                
        # Filter by Campaign
        if self.selected_campaigns:
            if "Campaign" in df.columns:
                df = df[df["Campaign"].isin(self.selected_campaigns)]
        
        # Filter by Date
        if self.filter_date_range and len(self.filter_date_range) == 2:
            date_col = next((c for c in df.columns if 'date' in c.lower()), None)
            if date_col:
                start_date = pd.to_datetime(self.filter_date_range[0])
                end_date = pd.to_datetime(self.filter_date_range[1])
                mask = (pd.to_datetime(df[date_col]) >= start_date) & (pd.to_datetime(df[date_col]) <= end_date)
                df = df.loc[mask]
                
        return df
