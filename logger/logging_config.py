import logging
import json
from datetime import datetime
import os

def get_logger(name, logfile):
    log_dir = os.path.dirname(logfile)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler(logfile)
    handler.setFormatter(logging.Formatter('%(message)s'))

    if not logger.handlers:
        logger.addHandler(handler)

    return logger

def log_json(logger, payload):
    payload["timestamp"] = datetime.utcnow().isoformat()
    logger.info(json.dumps(payload))