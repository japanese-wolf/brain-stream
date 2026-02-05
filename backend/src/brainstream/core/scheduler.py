"""Background scheduler for periodic tasks."""

import logging
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

# Global scheduler instance
_scheduler: Optional[AsyncIOScheduler] = None


def get_scheduler() -> AsyncIOScheduler:
    """Get the global scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler()
    return _scheduler


async def fetch_all_sources_job() -> None:
    """Background job to fetch articles from all sources.

    This job is scheduled to run periodically.
    """
    from brainstream.core.config import settings
    from brainstream.core.database import get_session
    from brainstream.models.article import UserProfile
    from brainstream.services import collect_all
    from sqlalchemy import select

    logger.info("Starting scheduled fetch job...")

    try:
        # Get user's tech stack from profile
        tech_stack: list[str] = []
        async with get_session() as session:
            result = await session.execute(select(UserProfile).limit(1))
            profile = result.scalar_one_or_none()
            if profile:
                tech_stack = profile.tech_stack

        # Collect from all sources
        summary = await collect_all(
            tech_stack=tech_stack,
            skip_processing=False,  # Enable LLM processing
        )

        logger.info(
            f"Scheduled fetch complete: {summary.total_new} new articles "
            f"({summary.total_processed} processed) in {summary.duration_ms}ms"
        )

        for src in summary.sources:
            if src.errors:
                for err in src.errors:
                    logger.warning(f"  {src.source_name}: {err}")
            else:
                logger.info(f"  {src.source_name}: {src.new} new")

    except Exception as e:
        logger.error(f"Scheduled fetch failed: {e}")


def setup_scheduler(
    fetch_interval_minutes: int = 30,
    start_immediately: bool = True,
) -> AsyncIOScheduler:
    """Set up the background scheduler with default jobs.

    Args:
        fetch_interval_minutes: How often to fetch new articles (default: 30 min).
        start_immediately: Whether to run the fetch job immediately on startup.

    Returns:
        Configured scheduler instance.
    """
    scheduler = get_scheduler()

    # Remove existing jobs if any
    scheduler.remove_all_jobs()

    # Add the fetch job
    scheduler.add_job(
        fetch_all_sources_job,
        trigger=IntervalTrigger(minutes=fetch_interval_minutes),
        id="fetch_all_sources",
        name="Fetch articles from all sources",
        replace_existing=True,
        max_instances=1,  # Prevent overlapping runs
    )

    logger.info(f"Scheduler configured: fetch every {fetch_interval_minutes} minutes")

    # Optionally run immediately
    if start_immediately:
        scheduler.add_job(
            fetch_all_sources_job,
            id="fetch_all_sources_startup",
            name="Initial fetch on startup",
            replace_existing=True,
        )
        logger.info("Initial fetch scheduled")

    return scheduler


def start_scheduler() -> None:
    """Start the background scheduler."""
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")


def stop_scheduler() -> None:
    """Stop the background scheduler."""
    scheduler = get_scheduler()
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")


def get_scheduler_status() -> dict:
    """Get current scheduler status and job information."""
    scheduler = get_scheduler()

    jobs = []
    for job in scheduler.get_jobs():
        next_run = job.next_run_time
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": next_run.isoformat() if next_run else None,
        })

    return {
        "running": scheduler.running,
        "jobs": jobs,
    }
