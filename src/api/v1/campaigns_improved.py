"""
Campaign endpoints (v1) - Improved with specific exceptions.

Replaces generic Exception catches with specific error types.
"""

from fastapi import APIRouter, Depends, BackgroundTasks, Request
from typing import Dict, Any
from datetime import date
import uuid

from loguru import logger

from ..middleware.auth import get_current_user
from ..middleware.rate_limit import limiter
from ..exceptions import (
    CampaignNotFoundError,
    CampaignInvalidStatusError,
    CampaignInvalidDatesError,
    ReportInvalidTemplateError,
    DatabaseConnectionError,
    DatabaseQueryError,
    SystemInternalError
)
from src.services.campaign_service import CampaignService
from src.di.containers import Container

router = APIRouter(prefix="/campaigns", tags=["campaigns"])

# Initialize DI container
container = Container()


@router.post("")
@limiter.limit("10/minute")
async def create_campaign(
    request: Request,
    campaign_name: str,
    objective: str,
    start_date: date,
    end_date: date,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a new campaign.
    
    Raises:
        CampaignInvalidDatesError: If end_date is before start_date
        DatabaseConnectionError: If database connection fails
        DatabaseQueryError: If database query fails
    """
    # Validate dates
    if end_date < start_date:
        raise CampaignInvalidDatesError(
            details={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        )
    
    try:
        campaign_service = container.campaign_service()
        
        campaign = campaign_service.create_campaign(
            name=campaign_name,
            objective=objective,
            start_date=start_date,
            end_date=end_date,
            created_by=current_user["username"]
        )
        
        logger.info(
            f"Campaign created: {campaign.id}",
            extra={
                "campaign_id": str(campaign.id),
                "user": current_user["username"],
                "action": "create_campaign"
            }
        )
        
        return {
            "campaign_id": str(campaign.id),
            "name": campaign.name,
            "objective": campaign.objective,
            "status": campaign.status,
            "created_at": campaign.created_at.isoformat() if campaign.created_at else None
        }
        
    except ConnectionError as e:
        logger.error(f"Database connection failed: {e}")
        raise DatabaseConnectionError(details={"reason": str(e)})
    
    except Exception as e:
        logger.error(f"Failed to create campaign: {e}")
        raise DatabaseQueryError(details={"operation": "create_campaign"})


@router.get("/{campaign_id}")
@limiter.limit("100/minute")
async def get_campaign(
    request: Request,
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get campaign details.
    
    Raises:
        CampaignNotFoundError: If campaign doesn't exist
        DatabaseQueryError: If database query fails
    """
    try:
        campaign_service = container.campaign_service()
        campaign = campaign_service.get_campaign(campaign_id)
        
        if not campaign:
            raise CampaignNotFoundError(campaign_id=campaign_id)
        
        logger.info(
            f"Campaign retrieved: {campaign_id}",
            extra={
                "campaign_id": campaign_id,
                "user": current_user["username"],
                "action": "get_campaign"
            }
        )
        
        return {
            "campaign_id": str(campaign.id),
            "name": campaign.name,
            "objective": campaign.objective,
            "status": campaign.status,
            "start_date": campaign.start_date.isoformat() if campaign.start_date else None,
            "end_date": campaign.end_date.isoformat() if campaign.end_date else None,
            "created_at": campaign.created_at.isoformat() if campaign.created_at else None
        }
        
    except CampaignNotFoundError:
        raise
    
    except Exception as e:
        logger.error(f"Failed to get campaign: {e}")
        raise DatabaseQueryError(details={"operation": "get_campaign", "campaign_id": campaign_id})


@router.post("/{campaign_id}/report/regenerate")
@limiter.limit("5/minute")
async def regenerate_report(
    request: Request,
    campaign_id: str,
    template: str = "default",
    background_tasks: BackgroundTasks = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Regenerate report with a different template.
    
    Raises:
        CampaignNotFoundError: If campaign doesn't exist
        CampaignInvalidStatusError: If campaign is not completed
        ReportInvalidTemplateError: If template is invalid
    """
    # Validate template
    valid_templates = ["default", "executive", "detailed", "custom"]
    if template not in valid_templates:
        raise ReportInvalidTemplateError(
            template=template,
            valid_templates=valid_templates
        )
    
    try:
        campaign_service = container.campaign_service()
        campaign = campaign_service.get_campaign(campaign_id)
        
        if not campaign:
            raise CampaignNotFoundError(campaign_id=campaign_id)
        
        if campaign.status != "completed":
            raise CampaignInvalidStatusError(
                current_status=campaign.status,
                required_status="completed"
            )
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Queue regeneration task
        if background_tasks:
            background_tasks.add_task(
                regenerate_report_task,
                campaign_id=campaign_id,
                template=template,
                job_id=job_id,
                user=current_user["username"]
            )
        
        logger.info(
            f"Report regeneration queued: {job_id}",
            extra={
                "job_id": job_id,
                "campaign_id": campaign_id,
                "template": template,
                "user": current_user["username"],
                "action": "regenerate_report"
            }
        )
        
        return {
            "job_id": job_id,
            "campaign_id": campaign_id,
            "template": template,
            "status": "queued",
            "message": f"Report regeneration queued with template: {template}"
        }
        
    except (CampaignNotFoundError, CampaignInvalidStatusError, ReportInvalidTemplateError):
        raise
    
    except Exception as e:
        logger.error(f"Failed to queue report regeneration: {e}")
        raise SystemInternalError(details={"operation": "regenerate_report"})


async def regenerate_report_task(
    campaign_id: str,
    template: str,
    job_id: str,
    user: str
):
    """Background task to regenerate report."""
    try:
        logger.info(
            f"Starting report regeneration: {job_id}",
            extra={
                "job_id": job_id,
                "campaign_id": campaign_id,
                "template": template,
                "user": user
            }
        )
        
        campaign_service = container.campaign_service()
        campaign = campaign_service.get_campaign(campaign_id)
        
        if not campaign:
            logger.error(f"Campaign not found: {campaign_id}")
            return
        
        # TODO: Implement actual report generation
        logger.info(f"Would generate report with template: {template}")
        
        logger.info(
            f"Report regeneration completed: {job_id}",
            extra={
                "job_id": job_id,
                "campaign_id": campaign_id,
                "status": "completed"
            }
        )
        
    except Exception as e:
        logger.error(
            f"Report regeneration failed: {job_id}",
            extra={
                "job_id": job_id,
                "campaign_id": campaign_id,
                "error": str(e)
            }
        )


@router.delete("/{campaign_id}")
@limiter.limit("10/minute")
async def delete_campaign(
    request: Request,
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete a campaign.
    
    Raises:
        CampaignNotFoundError: If campaign doesn't exist
        DatabaseQueryError: If database query fails
    """
    try:
        campaign_service = container.campaign_service()
        campaign = campaign_service.get_campaign(campaign_id)
        
        if not campaign:
            raise CampaignNotFoundError(campaign_id=campaign_id)
        
        campaign_service.delete_campaign(campaign_id)
        
        logger.info(
            f"Campaign deleted: {campaign_id}",
            extra={
                "campaign_id": campaign_id,
                "user": current_user["username"],
                "action": "delete_campaign"
            }
        )
        
        return {
            "message": "Campaign deleted successfully",
            "campaign_id": campaign_id
        }
        
    except CampaignNotFoundError:
        raise
    
    except Exception as e:
        logger.error(f"Failed to delete campaign: {e}")
        raise DatabaseQueryError(details={"operation": "delete_campaign", "campaign_id": campaign_id})
