import schedule
import threading
import time
from datetime import datetime, timedelta

from d4rk.Logs import setup_logger
logger = setup_logger(__name__)

class scheduler:
    async def start_scheduler(self):
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            return
        schedule.clear()
        schedule.every().day.at(time_str="00:01",tz="Asia/Kolkata").do(lambda: self._safe_async(self.send_logs))
        self._stop_scheduler.clear()
        self._scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self._scheduler_thread.start()
        logger.info("Background scheduler started for log maintenance")    

    def stop_scheduler(self):
        if self._scheduler_thread:
            self._stop_scheduler.set()
            self._scheduler_thread.join(timeout=5)
            logger.info("Background scheduler stopped")

    def _run_scheduler(self):
        while not self._stop_scheduler.is_set():
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                if logger:
                    logger.error(f"Scheduler error: {e}")
