import logging

logger = logging.getLogger()
logger.setLevel(level=logging.INFO)

FILE_FORMAT = (
    "[%(levelname)s] %(message)s"
    "\nLocation: (%(filename)s, %(funcName)s, line %(lineno)d)"
    "\nAWS Request ID: %(aws_request_id)s"
    "\nTime: %(asctime)s"
)
for h in logger.handlers:
    h.setFormatter(logging.Formatter(FILE_FORMAT))
