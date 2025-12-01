"""
Campaign service layer.
Provides business logic for campaign operations.
"""

import logging
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from src.database.repositories import CampaignRepository, AnalysisRepository, CampaignContextRepository
from src.database.connection import DatabaseManager

logger = logging.getLogger(__name__)


class CampaignService:
    """Service for campaign operations."""
    
    def __init__(
        self,
        campaign_repo: CampaignRepository,
        analysis_repo: AnalysisRepository,
        context_repo: CampaignContextRepository
    ):
        self.campaign_repo = campaign_repo
        self.analysis_repo = analysis_repo
        self.context_repo = context_repo
    
    def import_from_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Import campaigns from a pandas DataFrame.
        
        Args:
            df: DataFrame with campaign data
            
        Returns:
            Dictionary with import results
        """
        try:
            campaigns_data = []
            
            for _, row in df.iterrows():
                # Convert row to dict and handle Timestamp serialization
                row_dict = {}
                for key, value in row.items():
                    if pd.isna(value):
                        row_dict[key] = None
                    elif isinstance(value, pd.Timestamp):
                        row_dict[key] = value.isoformat()
                    elif isinstance(value, (int, float, str, bool)):
                        row_dict[key] = value
                    else:
                        row_dict[key] = str(value)
                
                campaign_data = {
                    'campaign_id': str(row.get('Campaign_ID', uuid.uuid4())),
                    'campaign_name': str(row.get('Campaign_Name', row.get('Campaign', 'Unknown'))),
                    'platform': str(row.get('Platform', 'Unknown')),
                    'channel': str(row.get('Channel', row.get('platform', 'Unknown'))),
                    'spend': float(row.get('Spend', 0)),
                    'impressions': int(row.get('Impressions', 0)),
                    'clicks': int(row.get('Clicks', 0)),
                    'conversions': int(row.get('Conversions', 0)),
                    'ctr': float(row.get('CTR', 0)),
                    'cpc': float(row.get('CPC', 0)),
                    'cpa': float(row.get('CPA', 0)),
                    'roas': float(row.get('ROAS')) if 'ROAS' in row and pd.notna(row.get('ROAS')) else None,
                    'date': pd.to_datetime(row.get('Date')) if 'Date' in row else None,
                    'funnel_stage': str(row.get('Funnel_Stage', row.get('Funnel', row.get('Stage')))),
                    'audience': str(row.get('Audience')) if 'Audience' in row else None,
                    'creative_type': str(row.get('Creative_Type', row.get('Creative'))) if 'Creative_Type' in row or 'Creative' in row else None,
                    'placement': str(row.get('Placement')) if 'Placement' in row else None,
                    'additional_data': row_dict  # Use serializable dict
                }
                campaigns_data.append(campaign_data)
            
            # Bulk insert
            campaigns = self.campaign_repo.create_bulk(campaigns_data)
            self.campaign_repo.commit()
            
            logger.info(f"Imported {len(campaigns)} campaigns")
            
            return {
                'success': True,
                'imported_count': len(campaigns),
                'message': f'Successfully imported {len(campaigns)} campaigns'
            }
            
        except Exception as e:
            self.campaign_repo.rollback()
            logger.error(f"Failed to import campaigns: {e}")
            return {
                'success': False,
                'imported_count': 0,
                'message': f'Import failed: {str(e)}'
            }
    
    def get_campaigns(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get campaigns with optional filters.
        
        Args:
            filters: Optional filters (platform, channel, date_range, etc.)
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of campaign dictionaries
        """
        try:
            if filters:
                campaigns = self.campaign_repo.search(filters, limit=limit)
            else:
                campaigns = self.campaign_repo.get_all(limit=limit, offset=offset)
            
            return [self._campaign_to_dict(c) for c in campaigns]
            
        except Exception as e:
            logger.error(f"Failed to get campaigns: {e}")
            return []
    
    def get_campaign_by_id(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get a single campaign by ID."""
        try:
            campaign = self.campaign_repo.get_by_campaign_id(campaign_id)
            return self._campaign_to_dict(campaign) if campaign else None
        except Exception as e:
            logger.error(f"Failed to get campaign {campaign_id}: {e}")
            return None
    
    def get_aggregated_metrics(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get aggregated metrics across campaigns."""
        try:
            return self.campaign_repo.get_aggregated_metrics(filters)
        except Exception as e:
            logger.error(f"Failed to get aggregated metrics: {e}")
            return {}
    
    def save_analysis(
        self,
        campaign_id: str,
        analysis_type: str,
        results: Dict[str, Any],
        execution_time: float
    ) -> Optional[str]:
        """
        Save analysis results for a campaign.
        
        Args:
            campaign_id: Campaign ID
            analysis_type: Type of analysis ('auto', 'rag', 'channel', 'pattern')
            results: Analysis results
            execution_time: Execution time in seconds
            
        Returns:
            Analysis ID if successful, None otherwise
        """
        try:
            # Get campaign
            campaign = self.campaign_repo.get_by_campaign_id(campaign_id)
            if not campaign:
                logger.error(f"Campaign {campaign_id} not found")
                return None
            
            # Create analysis
            analysis_data = {
                'analysis_id': str(uuid.uuid4()),
                'campaign_id': campaign.id,
                'analysis_type': analysis_type,
                'insights': results.get('insights', []),
                'recommendations': results.get('recommendations', []),
                'metrics': results.get('metrics', {}),
                'executive_summary': results.get('executive_summary', {}),
                'status': 'completed',
                'execution_time': execution_time,
                'completed_at': datetime.utcnow()
            }
            
            analysis = self.analysis_repo.create(analysis_data)
            self.analysis_repo.commit()
            
            logger.info(f"Saved analysis {analysis.analysis_id} for campaign {campaign_id}")
            return analysis.analysis_id
            
        except Exception as e:
            self.analysis_repo.rollback()
            logger.error(f"Failed to save analysis: {e}")
            return None
    
    def get_campaign_analyses(self, campaign_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get all analyses for a campaign."""
        try:
            campaign = self.campaign_repo.get_by_campaign_id(campaign_id)
            if not campaign:
                return []
            
            analyses = self.analysis_repo.get_by_campaign(campaign.id, limit=limit)
            return [self._analysis_to_dict(a) for a in analyses]
            
        except Exception as e:
            logger.error(f"Failed to get analyses for campaign {campaign_id}: {e}")
            return []
    
    def update_campaign_context(
        self,
        campaign_id: str,
        context_data: Dict[str, Any]
    ) -> bool:
        """Update campaign context."""
        try:
            campaign = self.campaign_repo.get_by_campaign_id(campaign_id)
            if not campaign:
                logger.error(f"Campaign {campaign_id} not found")
                return False
            
            self.context_repo.update(campaign.id, context_data)
            self.context_repo.commit()
            
            logger.info(f"Updated context for campaign {campaign_id}")
            return True
            
        except Exception as e:
            self.context_repo.rollback()
            logger.error(f"Failed to update campaign context: {e}")
            return False
    
    def _campaign_to_dict(self, campaign) -> Dict[str, Any]:
        """Convert campaign model to dictionary."""
        if not campaign:
            return {}
        
        return {
            'id': campaign.id,
            'campaign_id': campaign.campaign_id,
            'campaign_name': campaign.campaign_name,
            'platform': campaign.platform,
            'channel': campaign.channel,
            'spend': campaign.spend,
            'impressions': campaign.impressions,
            'clicks': campaign.clicks,
            'conversions': campaign.conversions,
            'ctr': campaign.ctr,
            'cpc': campaign.cpc,
            'cpa': campaign.cpa,
            'roas': campaign.roas,
            'date': campaign.date.isoformat() if campaign.date else None,
            'funnel_stage': campaign.funnel_stage,
            'audience': campaign.audience,
            'creative_type': campaign.creative_type,
            'placement': campaign.placement,
            'created_at': campaign.created_at.isoformat(),
            'updated_at': campaign.updated_at.isoformat()
        }
    
    def _analysis_to_dict(self, analysis) -> Dict[str, Any]:
        """Convert analysis model to dictionary."""
        if not analysis:
            return {}
        
        return {
            'id': analysis.id,
            'analysis_id': analysis.analysis_id,
            'analysis_type': analysis.analysis_type,
            'insights': analysis.insights,
            'recommendations': analysis.recommendations,
            'metrics': analysis.metrics,
            'executive_summary': analysis.executive_summary,
            'status': analysis.status,
            'execution_time': analysis.execution_time,
            'created_at': analysis.created_at.isoformat(),
            'completed_at': analysis.completed_at.isoformat() if analysis.completed_at else None
        }
