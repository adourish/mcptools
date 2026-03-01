#!/usr/bin/env python3
"""
Continuous scheduler for MCP Daily Planning
Runs the process every N hours
"""

import asyncio
import logging
import schedule
import time
from datetime import datetime
from pathlib import Path
from run_process_new_v2 import process_new_comprehensive, DEFAULT_ENV_PATH

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_planning_process():
    """Wrapper to run async process in sync context"""
    try:
        logger.info("=" * 80)
        logger.info(f"SCHEDULED RUN STARTING - {datetime.now()}")
        logger.info("=" * 80)
        
        asyncio.run(process_new_comprehensive(env_path=DEFAULT_ENV_PATH))
        
        logger.info("=" * 80)
        logger.info(f"SCHEDULED RUN COMPLETED - {datetime.now()}")
        logger.info("=" * 80)
    except Exception as e:
        logger.error(f"Scheduled run failed: {e}", exc_info=True)

def main():
    """Main scheduler loop"""
    # Schedule runs at specific times
    schedule.every().day.at("06:00").do(run_planning_process)
    schedule.every().day.at("09:00").do(run_planning_process)
    schedule.every().day.at("12:00").do(run_planning_process)
    schedule.every().day.at("15:00").do(run_planning_process)
    schedule.every().day.at("18:00").do(run_planning_process)
    
    logger.info("MCP Daily Planning Scheduler started")
    logger.info("Scheduled runs: 6am, 9am, 12pm, 3pm, 6pm")
    logger.info("Press Ctrl+C to stop")
    
    # Run immediately on startup
    run_planning_process()
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
