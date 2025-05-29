import logging
import sys

logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)

# Log to file
file_handler = logging.FileHandler("./log/app.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Log to console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
