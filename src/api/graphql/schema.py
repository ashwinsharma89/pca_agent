"""
GraphQL Schema for PCA Agent
Provides flexible querying capabilities for complex data relationships
"""

import strawberry
from typing import List, Optional
from datetime import datetime

@strawberry.type
class Campaign:
    """Campaign data type."""
    id: str
    name: str
    platform: str
    spend: float
    impressions: int
    clicks: int
    conversions: int
    ctr: float
    cpc: float
    cpa: float
    created_at: datetime
    updated_at: datetime

@strawberry.type
class Benchmark:
    """Benchmark data type."""
    id: str
    industry: str
    platform: str
    metric: str
    value: float
    percentile: Optional[int]
    source: str

@strawberry.type
class Insight:
    """Insight data type."""
    id: str
    campaign_id: str
    type: str
    priority: str
    message: str
    impact: str
    recommendations: List[str]
    created_at: datetime

@strawberry.type
class User:
    """User data type."""
    id: str
    email: str
    name: str
    role: str
    created_at: datetime
    last_login: Optional[datetime]

@strawberry.type
class AnalyticsMetric:
    """Analytics metric type."""
    name: str
    value: float
    timestamp: datetime
    tags: Optional[List[str]]

@strawberry.input
class CampaignFilter:
    """Filter for campaigns."""
    platform: Optional[str] = None
    min_spend: Optional[float] = None
    max_spend: Optional[float] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

@strawberry.input
class BenchmarkFilter:
    """Filter for benchmarks."""
    industry: Optional[str] = None
    platform: Optional[str] = None
    metric: Optional[str] = None

@strawberry.type
class Query:
    """GraphQL queries."""
    
    @strawberry.field
    def campaigns(
        self,
        filter: Optional[CampaignFilter] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[Campaign]:
        """Get campaigns with optional filtering."""
        # Implementation would query database
        return []
    
    @strawberry.field
    def campaign(self, id: str) -> Optional[Campaign]:
        """Get single campaign by ID."""
        return None
    
    @strawberry.field
    def benchmarks(
        self,
        filter: Optional[BenchmarkFilter] = None,
        limit: int = 10
    ) -> List[Benchmark]:
        """Get benchmarks with optional filtering."""
        return []
    
    @strawberry.field
    def insights(
        self,
        campaign_id: Optional[str] = None,
        priority: Optional[str] = None,
        limit: int = 10
    ) -> List[Insight]:
        """Get insights with optional filtering."""
        return []
    
    @strawberry.field
    def user(self, id: str) -> Optional[User]:
        """Get user by ID."""
        return None
    
    @strawberry.field
    def metrics(
        self,
        name: Optional[str] = None,
        from_time: Optional[datetime] = None,
        to_time: Optional[datetime] = None
    ) -> List[AnalyticsMetric]:
        """Get analytics metrics."""
        return []

@strawberry.type
class Mutation:
    """GraphQL mutations."""
    
    @strawberry.mutation
    def create_campaign(
        self,
        name: str,
        platform: str,
        spend: float
    ) -> Campaign:
        """Create a new campaign."""
        # Implementation would create in database
        return Campaign(
            id="new_id",
            name=name,
            platform=platform,
            spend=spend,
            impressions=0,
            clicks=0,
            conversions=0,
            ctr=0.0,
            cpc=0.0,
            cpa=0.0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    @strawberry.mutation
    def update_campaign(
        self,
        id: str,
        name: Optional[str] = None,
        spend: Optional[float] = None
    ) -> Optional[Campaign]:
        """Update an existing campaign."""
        return None
    
    @strawberry.mutation
    def delete_campaign(self, id: str) -> bool:
        """Delete a campaign."""
        return True

schema = strawberry.Schema(query=Query, mutation=Mutation)
