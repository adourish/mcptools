#!/usr/bin/env python3
"""
Continuous scheduler for MCP Daily Planning
Runs the process every N hours

This scheduler can run standalone or as a Windows service.
It prevents concurrent runs and logs all activity.
"""

import asyncio
import logging
import schedule
import time
import sys
import argparse
from datetime import datetime
from pathlib import Path
from filelock import FileLock, Timeout
from run_process_new_v2 import process_new_comprehensive, DEFAULT_ENV_PATH

# Setup logging
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f"scheduler_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Lock file to prevent concurrent runs
LOCK_FILE = Path(__file__).parent / "scheduler.lock"
lock = FileLock(LOCK_FILE, timeout=1)

# Statistics
stats = {
    'total_runs': 0,
    'successful_runs': 0,
    'failed_runs': 0,
    'last_run': None,
    'last_success': None,
    'last_error': None
}

def run_planning_process(env_path: Path = DEFAULT_ENV_PATH):
    """Wrapper to run async process in sync context with locking"""
    try:
        # Try to acquire lock (prevents concurrent runs)
        with lock.acquire(timeout=1):
            stats['total_runs'] += 1
            stats['last_run'] = datetime.now()
            
            logger.info("=" * 80)
            logger.info(f"SCHEDULED RUN #{stats['total_runs']} STARTING - {stats['last_run']}")
            logger.info("=" * 80)
            
            # Run the process
            asyncio.run(process_new_comprehensive(env_path=env_path))
            
            # Update stats
            stats['successful_runs'] += 1
            stats['last_success'] = datetime.now()
            
            logger.info("=" * 80)
            logger.info(f"SCHEDULED RUN COMPLETED - {datetime.now()}")
            logger.info(f"Stats: {stats['successful_runs']} successful, {stats['failed_runs']} failed, {stats['total_runs']} total")
            logger.info("=" * 80)
            
    except Timeout:
        logger.warning("Previous run still in progress, skipping this scheduled run")
    except Exception as e:
        stats['failed_runs'] += 1
        stats['last_error'] = str(e)
        logger.error(f"Scheduled run failed: {e}", exc_info=True)
        logger.error(f"Stats: {stats['successful_runs']} successful, {stats['failed_runs']} failed, {stats['total_runs']} total")

def print_schedule():
    """Print current schedule"""
    logger.info("Current schedule:")
    for job in schedule.get_jobs():
        logger.info(f"  - {job}")

def main(env_path: Path = DEFAULT_ENV_PATH, run_now: bool = True):
    """Main scheduler loop
    
    Args:
        env_path: Path to environments.json
        run_now: If True, run immediately on startup
    """
    logger.info("=" * 80)
    logger.info("MCP DAILY PLANNING SCHEDULER")
    logger.info("=" * 80)
    logger.info(f"Environment file: {env_path}")
    logger.info(f"Log directory: {LOG_DIR}")
    logger.info(f"Lock file: {LOCK_FILE}")
    logger.info("")
    
    # Schedule runs at specific times
    schedule.every().day.at("06:00").do(run_planning_process, env_path=env_path)
    schedule.every().day.at("09:00").do(run_planning_process, env_path=env_path)
    schedule.every().day.at("12:00").do(run_planning_process, env_path=env_path)
    schedule.every().day.at("15:00").do(run_planning_process, env_path=env_path)
    schedule.every().day.at("18:00").do(run_planning_process, env_path=env_path)
    
    print_schedule()
    logger.info("")
    logger.info("Scheduler is now running. Press Ctrl+C to stop.")
    logger.info("")
    
    # Run immediately on startup if requested
    if run_now:
        logger.info("Running initial process now...")
        run_planning_process(env_path=env_path)
    
    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("")
        logger.info("=" * 80)
        logger.info("SCHEDULER STOPPED BY USER")
        logger.info(f"Final stats: {stats['successful_runs']} successful, {stats['failed_runs']} failed, {stats['total_runs']} total")
        logger.info("=" * 80)
        
        # Clean up lock file
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='MCP Daily Planning Scheduler - Runs planning process at scheduled times',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings (runs immediately, then at scheduled times)
  python scheduler.py
  
  # Use custom environment path
  python scheduler.py --env-path "C:\\Custom\\Path\\environments.json"
  
  # Don't run immediately on startup
  python scheduler.py --no-run-now
  
  # Custom path and no immediate run
  python scheduler.py --env-path "C:\\Custom\\environments.json" --no-run-now

Scheduled times: 6am, 9am, 12pm, 3pm, 6pm daily
        """
    )
    
    parser.add_argument(
        '--env-path',
        type=Path,
        default=DEFAULT_ENV_PATH,
        help=f'Path to environments.json file (default: {DEFAULT_ENV_PATH})'
    )
    
    parser.add_argument(
        '--no-run-now',
        action='store_true',
        help='Do not run immediately on startup (wait for first scheduled time)'
    )
    
    args = parser.parse_args()
    
    # Validate environment file
    if not args.env_path.exists():
        logger.error(f"Environment file not found: {args.env_path}")
        logger.error("Please create the file or specify a different path with --env-path")
        sys.exit(1)
    
    try:
        main(env_path=args.env_path, run_now=not args.no_run_now)
    except Exception as e:
        logger.error(f"Scheduler crashed: {e}", exc_info=True)
        sys.exit(1)
