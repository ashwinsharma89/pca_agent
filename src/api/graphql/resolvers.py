"""
GraphQL Resolvers
Business logic for GraphQL queries and mutations
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from src.database.models import Campaign as CampaignModel, Benchmark as BenchmarkModel

class CampaignResolver:
    """Resolver for campaign queries."""
    
    @staticmethod
    def get_campaigns(
        db: Session,
        filter_params: dict,
        limit: int,
        offset: int
    ) -> List[dict]:
        """Get campaigns with filtering."""
        query = db.query(CampaignModel)
        
        # Apply filters
        if filter_params.get("platform"):
            query = query.filter(CampaignModel.platform == filter_params["platform"])
        
        if filter_params.get("min_spend"):
            query = query.filter(CampaignModel.spend >= filter_params["min_spend"])
        
        if filter_params.get("max_spend"):
            query = query.filter(CampaignModel.spend <= filter_params["max_spend"])
        
        if filter_params.get("date_from"):
            query = query.filter(CampaignModel.created_at >= filter_params["date_from"])
        
        if filter_params.get("date_to"):
            query = query.filter(CampaignModel.created_at <= filter_params["date_to"])
        
        # Apply pagination
        campaigns = query.offset(offset).limit(limit).all()
        
        return [
            {
                "id": str(c.id),
                "name": c.name,
                "platform": c.platform,
                "spend": c.spend,
                "impressions": c.impressions,
                "clicks": c.clicks,
                "conversions": c.conversions,
                "ctr": c.ctr,
                "cpc": c.cpc,
                "cpa": c.cpa,
                "created_at": c.created_at,
                "updated_at": c.updated_at
            }
            for c in campaigns
        ]
    
    @staticmethod
    def get_campaign(db: Session, campaign_id: str) -> Optional[dict]:
        """Get single campaign."""
        campaign = db.query(CampaignModel).filter(
            CampaignModel.id == campaign_id
        ).first()
        
        if not campaign:
            return None
        
        return {
            "id": str(campaign.id),
            "name": campaign.name,
            "platform": campaign.platform,
            "spend": campaign.spend,
            "impressions": campaign.impressions,
            "clicks": campaign.clicks,
            "conversions": campaign.conversions,
            "ctr": campaign.ctr,
            "cpc": campaign.cpc,
            "cpa": campaign.cpa,
            "created_at": campaign.created_at,
            "updated_at": campaign.updated_at
        }
    
    @staticmethod
    def create_campaign(db: Session, campaign_data: dict) -> dict:
        """Create new campaign."""
        campaign = CampaignModel(**campaign_data)
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        
        return {
            "id": str(campaign.id),
            "name": campaign.name,
            "platform": campaign.platform,
            "spend": campaign.spend,
            "impressions": campaign.impressions,
            "clicks": campaign.clicks,
            "conversions": campaign.conversions,
            "ctr": campaign.ctr,
            "cpc": campaign.cpc,
            "cpa": campaign.cpa,
            "created_at": campaign.created_at,
            "updated_at": campaign.updated_at
        }

class BenchmarkResolver:
    """Resolver for benchmark queries."""
    
    @staticmethod
    def get_benchmarks(
        db: Session,
        filter_params: dict,
        limit: int
    ) -> List[dict]:
        """Get benchmarks with filtering."""
        query = db.query(BenchmarkModel)
        
        if filter_params.get("industry"):
            query = query.filter(BenchmarkModel.industry == filter_params["industry"])
        
        if filter_params.get("platform"):
            query = query.filter(BenchmarkModel.platform == filter_params["platform"])
        
        if filter_params.get("metric"):
            query = query.filter(BenchmarkModel.metric == filter_params["metric"])
        
        benchmarks = query.limit(limit).all()
        
        return [
            {
                "id": str(b.id),
                "industry": b.industry,
                "platform": b.platform,
                "metric": b.metric,
                "value": b.value,
                "percentile": b.percentile,
                "source": b.source
            }
            for b in benchmarks
        ]
