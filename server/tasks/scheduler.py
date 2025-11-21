"""
Background Task Scheduler
Scheduled jobs for periodic data updates and maintenance
"""
import sys
from pathlib import Path
from datetime import datetime, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import asyncio
import structlog

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))

from server.config import settings
from server.websocket.manager import manager
from src.data_fetcher import DataFetcher
from src.data_processor import DataProcessor
import config

logger = structlog.get_logger(__name__)


class MarketDataScheduler:
    """Scheduler for market data updates"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.fetcher = DataFetcher()
        self.processor = DataProcessor()
        self.is_running = False
    
    async def update_market_data(self):
        """
        Fetch and process latest market data
        Runs during market hours
        """
        try:
            logger.info("scheduled_market_update_started")
            
            # Fetch data
            raw_data = self.fetcher.fetch_complete_dataset(
                max_stocks=50,  # Limit for frequent updates
                use_cache=True
            )
            
            if raw_data.empty:
                logger.warning("no_data_fetched_in_scheduled_update")
                return
            
            # Process data
            processed_data, sector_summary, _ = self.processor.process_complete_dataset(
                raw_data,
                animation_period='M'
            )
            
            # Save to files
            processed_data.to_csv(Path(config.DATA_DIR) / "processed_data.csv", index=False)
            sector_summary.to_csv(Path(config.DATA_DIR) / "sector_summary.csv", index=False)
            
            # Broadcast update via WebSocket
            await manager.broadcast({
                "type": "market_update",
                "timestamp": datetime.utcnow().isoformat(),
                "stocks_updated": processed_data['Symbol'].nunique(),
                "message": "Market data updated"
            })
            
            logger.info("scheduled_market_update_completed",
                       stocks=processed_data['Symbol'].nunique())
            
        except Exception as e:
            logger.error("scheduled_market_update_failed", error=str(e), exc_info=True)
    
    async def cleanup_old_data(self):
        """
        Cleanup old cached data and logs
        Runs daily at midnight
        """
        try:
            logger.info("cleanup_task_started")
            
            # Cleanup cache files older than 30 days
            cache_dir = Path(config.CACHE_DIR)
            if cache_dir.exists():
                cutoff_time = datetime.now().timestamp() - (30 * 24 * 60 * 60)
                cleaned_count = 0
                
                for file in cache_dir.glob("*.csv"):
                    if file.stat().st_mtime < cutoff_time:
                        file.unlink()
                        cleaned_count += 1
                
                logger.info("cache_cleanup_completed", files_removed=cleaned_count)
            
            # Could add log rotation here
            
        except Exception as e:
            logger.error("cleanup_task_failed", error=str(e), exc_info=True)
    
    async def send_daily_summary(self):
        """
        Generate and send daily market summary
        Runs after market close
        """
        try:
            logger.info("daily_summary_task_started")
            
            # Load processed data
            data_file = Path(config.DATA_DIR) / "processed_data.csv"
            if not data_file.exists():
                logger.warning("no_data_for_daily_summary")
                return
            
            import pandas as pd
            df = pd.read_csv(data_file)
            
            # Calculate summary
            latest_data = df.sort_values('Date').groupby('Symbol').last()
            
            summary = {
                "type": "daily_summary",
                "date": datetime.now().strftime('%Y-%m-%d'),
                "total_stocks": len(latest_data),
                "avg_return": float(latest_data['YTD_Return'].mean()),
                "top_performers": latest_data.nlargest(5, 'YTD_Return')[['Symbol', 'YTD_Return']].to_dict('records')
            }
            
            # Broadcast to all connected clients
            await manager.broadcast(summary)
            
            logger.info("daily_summary_sent", total_stocks=summary['total_stocks'])
            
        except Exception as e:
            logger.error("daily_summary_failed", error=str(e), exc_info=True)
    
    def start(self):
        """Start the scheduler"""
        if not settings.ENABLE_SCHEDULER:
            logger.info("scheduler_disabled_by_config")
            return
        
        # Market data update - every N minutes during market hours (9:30 AM - 4:00 PM ET)
        # For simplicity, we'll run every N minutes regardless of market hours
        self.scheduler.add_job(
            self.update_market_data,
            IntervalTrigger(minutes=settings.MARKET_UPDATE_INTERVAL_MINUTES),
            id='market_data_update',
            name='Update market data',
            replace_existing=True
        )
        
        # Daily cleanup at midnight
        self.scheduler.add_job(
            self.cleanup_old_data,
            CronTrigger(hour=0, minute=0),
            id='daily_cleanup',
            name='Daily cleanup',
            replace_existing=True
        )
        
        # Daily summary at 5 PM ET (after market close)
        self.scheduler.add_job(
            self.send_daily_summary,
            CronTrigger(hour=17, minute=0),
            id='daily_summary',
            name='Daily summary',
            replace_existing=True
        )
        
        self.scheduler.start()
        self.is_running = True
        
        logger.info("scheduler_started",
                   jobs=len(self.scheduler.get_jobs()),
                   update_interval_minutes=settings.MARKET_UPDATE_INTERVAL_MINUTES)
    
    def stop(self):
        """Stop the scheduler"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("scheduler_stopped")


# Global scheduler instance
scheduler_instance = MarketDataScheduler()


def start_scheduler():
    """Start the background scheduler"""
    scheduler_instance.start()
    try:
        # Keep the scheduler running
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        scheduler_instance.stop()


if __name__ == "__main__":
    # Run as standalone worker
    from src.logging_config import setup_logging
    setup_logging()
    
    logger.info("starting_scheduler_worker")
    start_scheduler()

