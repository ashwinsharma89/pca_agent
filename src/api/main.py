"""
FastAPI main application for PCA Agent.
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import uuid
import os
from pathlib import Path
from datetime import date

from loguru import logger

from ..models import (
    Campaign,
    CampaignObjective,
    CampaignStatus,
    DateRange,
    PlatformType,
    PlatformSnapshot,
    ReportConfig
)
from ..orchestration import PCAWorkflow
from ..config import settings
from ..utils import setup_logger
from ..utils.resilience import (
    get_resilience_status, health_checker, HealthStatus,
    CircuitBreaker, DeadLetterQueue
)
from ..utils.observability import (
    get_observability_status, metrics, tracer, cost_tracker, alerts,
    structured_logger
)
from ..utils.performance import (
    get_optimizer, get_performance_metrics, estimate_optimization_impact,
    SemanticCache
)

# Initialize logger
setup_logger()

# Create FastAPI app
app = FastAPI(
    title="PCA Agent API",
    description="Post Campaign Analysis with Agentic AI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (replace with database in production)
campaigns_db = {}

# Initialize workflow
workflow = PCAWorkflow()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "PCA Agent API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy"}


@app.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check with resilience status.
    
    Returns:
        Comprehensive health status including:
        - Overall system health
        - Circuit breaker states
        - Dead letter queue stats
        - Individual service health checks
    """
    try:
        resilience_status = get_resilience_status()
        
        # Check if any circuit breakers are open
        circuit_breakers = resilience_status.get("circuit_breakers", {})
        any_circuit_open = any(
            cb.get("state") == "open" 
            for cb in circuit_breakers.values()
        )
        
        # Check dead letter queue
        dlq_stats = resilience_status.get("dead_letter_queue", {})
        dlq_count = dlq_stats.get("total_jobs", 0)
        
        # Determine overall health
        is_healthy = not any_circuit_open and dlq_count < 100
        
        return {
            "status": "healthy" if is_healthy else "degraded",
            "timestamp": date.today().isoformat(),
            "components": {
                "api": {"status": "healthy"},
                "circuit_breakers": {
                    "status": "degraded" if any_circuit_open else "healthy",
                    "details": circuit_breakers
                },
                "dead_letter_queue": {
                    "status": "warning" if dlq_count > 50 else "healthy",
                    "pending_jobs": dlq_count,
                    "details": dlq_stats
                }
            },
            "health_checks": resilience_status.get("health_checks", {})
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.get("/resilience/status")
async def resilience_status() -> Dict[str, Any]:
    """
    Get full resilience system status.
    
    Returns:
        Complete status of all resilience components.
    """
    return get_resilience_status()


@app.get("/resilience/circuit-breakers")
async def circuit_breaker_status() -> Dict[str, Any]:
    """Get status of all circuit breakers."""
    return CircuitBreaker.get_all_states()


@app.post("/resilience/circuit-breakers/{name}/reset")
async def reset_circuit_breaker(name: str):
    """Manually reset a circuit breaker."""
    try:
        cb = CircuitBreaker.get_instance(name)
        cb.reset()
        return {"status": "success", "message": f"Circuit breaker '{name}' reset"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/resilience/dead-letter-queue")
async def dead_letter_queue_status() -> Dict[str, Any]:
    """Get dead letter queue status and jobs."""
    dlq = DeadLetterQueue.get_instance()
    return {
        "stats": dlq.stats(),
        "jobs": [job.to_dict() for job in dlq.get_all()[:50]]  # Limit to 50
    }


@app.delete("/resilience/dead-letter-queue/{job_id}")
async def remove_dlq_job(job_id: str):
    """Remove a job from the dead letter queue."""
    dlq = DeadLetterQueue.get_instance()
    if dlq.remove(job_id):
        return {"status": "success", "message": f"Job '{job_id}' removed"}
    raise HTTPException(status_code=404, detail="Job not found")


# =============================================================================
# OBSERVABILITY ENDPOINTS
# =============================================================================

@app.get("/observability/status")
async def observability_status() -> Dict[str, Any]:
    """
    Get complete observability status.
    
    Returns:
        Full observability data including metrics, traces, alerts, and costs.
    """
    return get_observability_status()


@app.get("/observability/metrics")
async def get_metrics() -> Dict[str, Any]:
    """Get all collected metrics."""
    return metrics.get_all_metrics()


@app.get("/observability/metrics/prometheus")
async def get_metrics_prometheus():
    """Get metrics in Prometheus text format."""
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(
        content=metrics.to_prometheus_format(),
        media_type="text/plain"
    )


@app.get("/observability/traces")
async def get_traces(limit: int = 50) -> Dict[str, Any]:
    """Get recent traces."""
    return {
        "traces": tracer.get_recent_traces(limit=limit)
    }


@app.get("/observability/traces/{trace_id}")
async def get_trace(trace_id: str) -> Dict[str, Any]:
    """Get a specific trace by ID."""
    spans = tracer.get_trace(trace_id)
    if not spans:
        raise HTTPException(status_code=404, detail="Trace not found")
    return {
        "trace_id": trace_id,
        "spans": spans
    }


@app.get("/observability/alerts")
async def get_alerts() -> Dict[str, Any]:
    """Get active alerts and alert history."""
    return {
        "active": alerts.get_active_alerts(),
        "history": alerts.get_alert_history(limit=100)
    }


@app.post("/observability/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    """Acknowledge an alert."""
    alerts.acknowledge_alert(alert_id)
    return {"status": "success", "message": f"Alert '{alert_id}' acknowledged"}


@app.post("/observability/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Resolve an alert."""
    alerts.resolve_alert(alert_id)
    return {"status": "success", "message": f"Alert '{alert_id}' resolved"}


@app.get("/observability/costs")
async def get_costs() -> Dict[str, Any]:
    """Get LLM cost tracking data."""
    return cost_tracker.get_usage_stats()


@app.post("/observability/costs/budget")
async def set_budget(daily: float = None, monthly: float = None):
    """Set cost budget limits."""
    cost_tracker.set_budget(daily=daily, monthly=monthly)
    return {
        "status": "success",
        "budgets": {
            "daily": cost_tracker._daily_budget,
            "monthly": cost_tracker._monthly_budget
        }
    }


# =============================================================================
# PERFORMANCE OPTIMIZATION ENDPOINTS
# =============================================================================

@app.get("/performance/status")
async def performance_status() -> Dict[str, Any]:
    """
    Get performance optimization status and metrics.
    
    Returns:
        Performance metrics from all optimization components.
    """
    return get_performance_metrics()


@app.get("/performance/impact")
async def performance_impact() -> Dict[str, Any]:
    """
    Get estimated impact of performance optimizations.
    
    Returns:
        Estimated time and cost savings from optimizations.
    """
    return estimate_optimization_impact()


@app.get("/performance/cache/stats")
async def cache_stats() -> Dict[str, Any]:
    """Get semantic cache statistics."""
    cache = SemanticCache.get_instance()
    return cache.get_metrics()


@app.post("/performance/cache/clear")
async def clear_cache():
    """Clear the semantic cache."""
    cache = SemanticCache.get_instance()
    cache.clear()
    return {"status": "success", "message": "Cache cleared"}


@app.post("/performance/cache/save")
async def save_cache():
    """Save cache to disk for persistence."""
    cache = SemanticCache.get_instance()
    cache.save_cache()
    return {"status": "success", "message": "Cache saved to disk"}


@app.post("/api/campaigns")
async def create_campaign(
    campaign_name: str,
    objectives: List[CampaignObjective],
    start_date: date,
    end_date: date
):
    """
    Create a new campaign analysis job.
    
    Args:
        campaign_name: Name of the campaign
        objectives: List of campaign objectives
        start_date: Campaign start date
        end_date: Campaign end date
        
    Returns:
        Campaign ID and details
    """
    campaign_id = str(uuid.uuid4())
    
    campaign = Campaign(
        campaign_id=campaign_id,
        campaign_name=campaign_name,
        objectives=objectives,
        date_range=DateRange(start=start_date, end=end_date)
    )
    
    campaigns_db[campaign_id] = campaign
    
    logger.info(f"Created campaign {campaign_id}: {campaign_name}")
    
    return {
        "campaign_id": campaign_id,
        "campaign_name": campaign_name,
        "status": campaign.status.value,
        "created_at": campaign.created_at
    }


@app.get("/api/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str):
    """Get campaign details."""
    if campaign_id not in campaigns_db:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign = campaigns_db[campaign_id]
    
    return {
        "campaign_id": campaign.campaign_id,
        "campaign_name": campaign.campaign_name,
        "status": campaign.status.value,
        "objectives": [obj.value for obj in campaign.objectives],
        "date_range": {
            "start": campaign.date_range.start,
            "end": campaign.date_range.end
        },
        "snapshots_count": len(campaign.snapshots),
        "report_path": campaign.report_path,
        "created_at": campaign.created_at,
        "updated_at": campaign.updated_at
    }


@app.post("/api/campaigns/{campaign_id}/snapshots")
async def upload_snapshots(
    campaign_id: str,
    files: List[UploadFile] = File(...),
    platform: PlatformType = None
):
    """
    Upload dashboard snapshots for a campaign.
    
    Args:
        campaign_id: Campaign ID
        files: List of image files
        platform: Platform type (optional, will be auto-detected)
        
    Returns:
        List of uploaded snapshot IDs
    """
    if campaign_id not in campaigns_db:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign = campaigns_db[campaign_id]
    campaign.status = CampaignStatus.UPLOADING
    
    snapshot_ids = []
    
    for file in files:
        # Validate file size
        content = await file.read()
        if len(content) > settings.max_upload_size_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File {file.filename} exceeds max size of {settings.max_upload_size_mb}MB"
            )
        
        # Save file
        snapshot_id = str(uuid.uuid4())
        file_ext = Path(file.filename).suffix
        file_path = settings.snapshot_dir / f"{campaign_id}_{snapshot_id}{file_ext}"
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Create snapshot record
        snapshot = PlatformSnapshot(
            snapshot_id=snapshot_id,
            platform=platform or PlatformType.GOOGLE_ADS,  # Default, will be auto-detected
            campaign_id=campaign_id,
            file_path=str(file_path)
        )
        
        campaign.snapshots.append(snapshot)
        snapshot_ids.append(snapshot_id)
        
        logger.info(f"Uploaded snapshot {snapshot_id} for campaign {campaign_id}")
    
    return {
        "campaign_id": campaign_id,
        "uploaded_count": len(snapshot_ids),
        "snapshot_ids": snapshot_ids
    }


@app.get("/api/campaigns/{campaign_id}/snapshots")
async def list_snapshots(campaign_id: str):
    """List all snapshots for a campaign."""
    if campaign_id not in campaigns_db:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign = campaigns_db[campaign_id]
    
    return {
        "campaign_id": campaign_id,
        "snapshots": [
            {
                "snapshot_id": s.snapshot_id,
                "platform": s.platform.value,
                "detected_platform": s.detected_platform.value if s.detected_platform else None,
                "uploaded_at": s.uploaded_at,
                "processing_status": s.processing_status
            }
            for s in campaign.snapshots
        ]
    }


@app.post("/api/campaigns/{campaign_id}/analyze")
async def analyze_campaign(
    campaign_id: str,
    background_tasks: BackgroundTasks
):
    """
    Start campaign analysis.
    
    Args:
        campaign_id: Campaign ID
        
    Returns:
        Analysis job status
    """
    if campaign_id not in campaigns_db:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign = campaigns_db[campaign_id]
    
    if not campaign.snapshots:
        raise HTTPException(status_code=400, detail="No snapshots uploaded")
    
    # Run analysis in background
    background_tasks.add_task(run_analysis, campaign_id)
    
    return {
        "campaign_id": campaign_id,
        "status": "analysis_started",
        "message": "Campaign analysis started. Check status endpoint for progress."
    }


async def run_analysis(campaign_id: str):
    """Background task to run campaign analysis."""
    try:
        campaign = campaigns_db[campaign_id]
        logger.info(f"Starting analysis for campaign {campaign_id}")
        
        # Run workflow
        consolidated_report = await workflow.run(campaign)
        
        # Update campaign
        campaigns_db[campaign_id] = campaign
        
        logger.info(f"Analysis completed for campaign {campaign_id}")
        
    except Exception as e:
        logger.error(f"Analysis failed for campaign {campaign_id}: {e}")
        campaign = campaigns_db[campaign_id]
        campaign.status = CampaignStatus.FAILED
        campaign.processing_error = str(e)


@app.get("/api/campaigns/{campaign_id}/status")
async def get_campaign_status(campaign_id: str):
    """Get campaign processing status."""
    if campaign_id not in campaigns_db:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign = campaigns_db[campaign_id]
    
    return {
        "campaign_id": campaign_id,
        "status": campaign.status.value,
        "processing_error": campaign.processing_error,
        "processing_logs": campaign.processing_logs[-10:],  # Last 10 logs
        "report_ready": campaign.report_path is not None
    }


@app.get("/api/campaigns/{campaign_id}/data")
async def get_campaign_data(campaign_id: str):
    """Get extracted campaign data in JSON format."""
    if campaign_id not in campaigns_db:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign = campaigns_db[campaign_id]
    
    return {
        "campaign_id": campaign_id,
        "normalized_metrics": [m.model_dump() for m in campaign.normalized_metrics],
        "insights": campaign.insights,
        "achievements": campaign.achievements,
        "recommendations": campaign.recommendations
    }


@app.get("/api/campaigns/{campaign_id}/report")
async def download_report(campaign_id: str):
    """Download the generated PowerPoint report."""
    if campaign_id not in campaigns_db:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign = campaigns_db[campaign_id]
    
    if not campaign.report_path:
        raise HTTPException(status_code=404, detail="Report not yet generated")
    
    report_path = Path(campaign.report_path)
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report file not found")
    
    return FileResponse(
        path=str(report_path),
        filename=f"{campaign.campaign_name}_report.pptx",
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )


@app.post("/api/campaigns/{campaign_id}/regenerate")
async def regenerate_report(
    campaign_id: str,
    template: str = "corporate",
    background_tasks: BackgroundTasks = None
):
    """Regenerate report with a different template."""
    if campaign_id not in campaigns_db:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign = campaigns_db[campaign_id]
    
    if campaign.status != CampaignStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Campaign analysis not completed")
    
    # TODO: Implement report regeneration with new template
    
    return {
        "campaign_id": campaign_id,
        "message": "Report regeneration started"
    }


@app.delete("/api/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: str):
    """Delete a campaign and its data."""
    if campaign_id not in campaigns_db:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign = campaigns_db[campaign_id]
    
    # Delete snapshot files
    for snapshot in campaign.snapshots:
        file_path = Path(snapshot.file_path)
        if file_path.exists():
            file_path.unlink()
    
    # Delete report file
    if campaign.report_path:
        report_path = Path(campaign.report_path)
        if report_path.exists():
            report_path.unlink()
    
    # Remove from database
    del campaigns_db[campaign_id]
    
    logger.info(f"Deleted campaign {campaign_id}")
    
    return {"message": "Campaign deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level="info"
    )
