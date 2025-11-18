"""
Data models for campaign analysis and reporting.
"""
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime, date
from pydantic import BaseModel, Field
from .platform import PlatformType, PlatformSnapshot, NormalizedMetric


class CampaignObjective(str, Enum):
    """Campaign objectives."""
    AWARENESS = "awareness"
    CONSIDERATION = "consideration"
    CONVERSION = "conversion"
    ENGAGEMENT = "engagement"
    TRAFFIC = "traffic"
    LEAD_GENERATION = "lead_generation"
    APP_INSTALLS = "app_installs"


class CampaignStatus(str, Enum):
    """Campaign analysis status."""
    CREATED = "created"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    EXTRACTING = "extracting"
    REASONING = "reasoning"
    GENERATING_REPORT = "generating_report"
    COMPLETED = "completed"
    FAILED = "failed"


class DateRange(BaseModel):
    """Campaign date range."""
    start: date = Field(..., description="Start date")
    end: date = Field(..., description="End date")
    
    @property
    def duration_days(self) -> int:
        """Calculate duration in days."""
        return (self.end - self.start).days + 1


class Campaign(BaseModel):
    """Campaign analysis request."""
    campaign_id: str = Field(..., description="Unique campaign ID")
    campaign_name: str = Field(..., description="Campaign name")
    objectives: List[CampaignObjective] = Field(..., description="Campaign objectives")
    date_range: DateRange = Field(..., description="Campaign date range")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: CampaignStatus = Field(default=CampaignStatus.CREATED)
    
    # Snapshots
    snapshots: List[PlatformSnapshot] = Field(
        default_factory=list,
        description="Uploaded dashboard snapshots"
    )
    
    # Extracted Data
    normalized_metrics: List[NormalizedMetric] = Field(
        default_factory=list,
        description="Normalized metrics across all platforms"
    )
    
    # Analysis Results
    insights: Optional[Dict[str, Any]] = Field(None, description="AI-generated insights")
    achievements: Optional[List[Dict[str, Any]]] = Field(None, description="Key achievements")
    recommendations: Optional[List[str]] = Field(None, description="Recommendations")
    
    # Report
    report_path: Optional[str] = Field(None, description="Path to generated report")
    report_generated_at: Optional[datetime] = Field(None, description="Report generation timestamp")
    
    # Processing
    processing_error: Optional[str] = Field(None, description="Error message if failed")
    processing_logs: List[str] = Field(default_factory=list, description="Processing logs")


class ChannelPerformance(BaseModel):
    """Performance analysis for a single channel."""
    platform: PlatformType
    platform_name: str
    
    # Key Metrics
    total_impressions: Optional[float] = None
    total_clicks: Optional[float] = None
    total_conversions: Optional[float] = None
    total_spend: Optional[float] = None
    
    # Calculated Metrics
    ctr: Optional[float] = Field(None, description="Click-through rate")
    cpc: Optional[float] = Field(None, description="Cost per click")
    cpa: Optional[float] = Field(None, description="Cost per acquisition")
    roas: Optional[float] = Field(None, description="Return on ad spend")
    conversion_rate: Optional[float] = Field(None, description="Conversion rate")
    
    # Rankings
    performance_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=100.0,
        description="Overall performance score (0-100)"
    )
    efficiency_rank: Optional[int] = Field(None, description="Efficiency ranking")
    
    # Insights
    strengths: List[str] = Field(default_factory=list, description="Channel strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Channel weaknesses")
    opportunities: List[str] = Field(default_factory=list, description="Opportunities")
    
    # Top Performers
    top_creative: Optional[str] = Field(None, description="Best performing creative")
    top_audience: Optional[str] = Field(None, description="Best performing audience")
    top_placement: Optional[str] = Field(None, description="Best performing placement")


class CrossChannelInsight(BaseModel):
    """Cross-channel analysis insight."""
    insight_type: str = Field(..., description="Type of insight (synergy, attribution, etc.)")
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Detailed description")
    affected_platforms: List[PlatformType] = Field(..., description="Platforms involved")
    impact_score: float = Field(..., ge=0.0, le=10.0, description="Impact score (0-10)")
    supporting_data: Optional[Dict[str, Any]] = Field(None, description="Supporting data")


class Achievement(BaseModel):
    """Campaign achievement."""
    achievement_type: str = Field(..., description="Type of achievement")
    title: str = Field(..., description="Achievement title")
    description: str = Field(..., description="Detailed description")
    metric_value: Optional[float] = Field(None, description="Associated metric value")
    metric_name: Optional[str] = Field(None, description="Associated metric name")
    platform: Optional[PlatformType] = Field(None, description="Platform (if channel-specific)")
    impact_level: str = Field(..., description="Impact level (high, medium, low)")
    visual_data: Optional[Dict[str, Any]] = Field(None, description="Data for visualization")


class ConsolidatedReport(BaseModel):
    """Consolidated campaign report data."""
    campaign: Campaign
    
    # Summary
    executive_summary: str = Field(..., description="Executive summary")
    total_spend: float = Field(..., description="Total spend across all channels")
    total_conversions: float = Field(..., description="Total conversions")
    overall_roas: Optional[float] = Field(None, description="Overall ROAS")
    
    # Channel Performance
    channel_performances: List[ChannelPerformance] = Field(
        default_factory=list,
        description="Performance by channel"
    )
    
    # Cross-Channel Analysis
    cross_channel_insights: List[CrossChannelInsight] = Field(
        default_factory=list,
        description="Cross-channel insights"
    )
    
    # Achievements
    achievements: List[Achievement] = Field(
        default_factory=list,
        description="Key achievements"
    )
    
    # Recommendations
    recommendations: List[str] = Field(
        default_factory=list,
        description="Strategic recommendations"
    )
    
    # Attribution
    attribution_model: Optional[str] = Field(None, description="Attribution model used")
    attribution_data: Optional[Dict[str, Any]] = Field(None, description="Attribution data")
    
    # Visualizations
    visualizations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Generated visualizations metadata"
    )


class ReportTemplate(str, Enum):
    """Available report templates."""
    CORPORATE = "corporate"
    CREATIVE = "creative"
    MINIMAL = "minimal"
    DETAILED = "detailed"


class ReportConfig(BaseModel):
    """Report generation configuration."""
    template: ReportTemplate = Field(default=ReportTemplate.CORPORATE)
    include_raw_data: bool = Field(default=False, description="Include raw data appendix")
    include_methodology: bool = Field(default=True, description="Include methodology section")
    brand_color: Optional[str] = Field(None, description="Override brand color")
    company_name: Optional[str] = Field(None, description="Override company name")
    company_logo_path: Optional[str] = Field(None, description="Override company logo")
    
    # Content Options
    include_executive_summary: bool = Field(default=True)
    include_channel_breakdown: bool = Field(default=True)
    include_cross_channel_analysis: bool = Field(default=True)
    include_achievements: bool = Field(default=True)
    include_recommendations: bool = Field(default=True)
    include_visualizations: bool = Field(default=True)
    
    # Format Options
    output_format: str = Field(default="pptx", description="Output format (pptx, pdf)")
    page_size: str = Field(default="16:9", description="Slide aspect ratio")
