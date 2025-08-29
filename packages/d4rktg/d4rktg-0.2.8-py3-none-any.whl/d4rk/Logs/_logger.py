# src/Log/_logger_config.py

import os
import logging
from datetime import datetime, timezone, timedelta
from logging.handlers import TimedRotatingFileHandler

def get_timezone_offset(time_zone: str = "00:00") -> timezone:
    if time_zone:
        try:
            hours, minutes = time_zone.split(':')
            if hours.startswith("-"):
                return timezone(timedelta(hours=-int(hours), minutes=-int(minutes)))
            else:
                return timezone(timedelta(hours=int(hours), minutes=int(minutes)))
        except ValueError:
            raise ValueError(f"Invalid TIME_ZONE format: {time_zone}")
    return timezone(timedelta(hours=0))

TZ = get_timezone_offset(os.getenv("TIME_ZONE", "05:30"))

class TimeZoneFormatter(logging.Formatter):
    def converter(self, timestamp):
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return dt.astimezone(TZ).timetuple()

    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=timezone.utc)
        time_zone_time = dt.astimezone(TZ)
        if datefmt:
            return time_zone_time.strftime(datefmt)
        else:
            return time_zone_time.strftime('%Y-%m-%d %H:%M:%S %z')

def setup_logger(name=__name__, log_level=logging.INFO):
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    if logger.handlers:
        return logger
    
    time_zone_now = datetime.now(TZ)
    
    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(log_dir, f"log-{time_zone_now.strftime('%Y-%m-%d')}.txt"),
        when='midnight',
        interval=1,
        backupCount=30
    )
    file_handler.setLevel(log_level)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # Create formatter with Sri Lanka timezone
    formatter = TimeZoneFormatter(
        '%(asctime)s - %(name)s - %(funcName)s:%(lineno)d - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False
    return logger