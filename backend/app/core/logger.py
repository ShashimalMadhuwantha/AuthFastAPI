# https://docs.python.org/3/library/logging.html#logrecord-attributes

import logging
import sys
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Create a custom logger
logger = logging.getLogger(__name__)

# Set the default log level
logger.setLevel(logging.DEBUG)

# Create logs directory if it doesn't exist
logs_dir = Path(__file__).parent.parent.parent / 'logs'
logs_dir.mkdir(exist_ok=True)

# Create handlers
stream_handler = logging.StreamHandler(sys.stdout)
start_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
logFile = logs_dir / f'{start_time}.log'
# file_handler = logging.FileHandler(f'{start_time}.log')
file_handler= RotatingFileHandler(logFile, mode='a', maxBytes=50*1024*1024, backupCount=5, encoding='utf-8', delay=False)
# file_handler= RotatingFileHandler(logFile, mode='a', maxBytes=2000, backupCount=5, encoding='utf-8', delay=False)

'''Yes, the `RotatingFileHandler` in your code is configured to delete old logs. Specifically, it keeps up to 5 backup log files (`backupCount=5`). When the current log file reaches the size limit of 50MB (`maxBytes=50*1024*1024`), it rotates the log file, creating a new one. If there are already 5 backup files, the oldest one will be deleted to make room for the new log file.
Here's a brief summary of the relevant configuration:
- `maxBytes=50*1024*1024`: Each log file can grow up to 50MB.
- `backupCount=5`: Keeps up to 5 backup log files. When the limit is reached, the oldest log file is deleted.
This ensures that your application does not consume too much disk space with old log files.'''



# Set the log level for handlers, all info,debug,warning,error,critical will be logged
stream_handler.setLevel(logging.DEBUG)
file_handler.setLevel(logging.DEBUG)

# Create formatters and add them to handlers
stream_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
stream_handler.setFormatter(stream_format)
file_handler.setFormatter(file_format)

# Add handlers to the logger
logger.addHandler(stream_handler)
logger.addHandler(file_handler)

# Example usage
if __name__ == "__main__":
    logger.debug('This is a debug message')
    logger.info('This is an info message')
    logger.warning('This is a warning message')
    logger.error('This is an error message')
    logger.critical('This is a critical message')
