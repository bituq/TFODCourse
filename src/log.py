import logging
import coloredlogs
import time

class TimeDiffFormatter(logging.Formatter):
    def format(self, record):
        # Calculate time difference in milliseconds
        if hasattr(record, 'relativeCreated'):
            record.relativeCreated = int(record.relativeCreated)
        else:
            record.relativeCreated = 0
        return super().format(record)

# Create a logger object.
logger = logging.getLogger(__name__)

# Create a handler
handler = logging.StreamHandler()

# Install the handler on the logger object.
logger.addHandler(handler)
logger.setLevel('DEBUG')

# Apply coloredlogs to the logger
coloredlogs.install(level='DEBUG', logger=logger, fmt='%(relativeCreated)dms %(levelname)s: %(message)s', datefmt='%H:%M:%S')