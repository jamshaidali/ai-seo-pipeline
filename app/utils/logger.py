import logging
import json
from pythonjsonlogger import jsonlogger
from flask import g, request
import uuid

class CorrelationIdFilter(logging.Filter):
    def filter(self, record):
        record.correlation_id = getattr(g, 'correlation_id', 'unknown')
        return True

def setup_logging(app):
    # Create JSON formatter
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(correlation_id)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Get the Flask logger
    logger = logging.getLogger('app')
    logger.setLevel(logging.INFO)

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create console handler
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.addFilter(CorrelationIdFilter())
    logger.addHandler(handler)

    # Set up correlation ID middleware
    @app.before_request
    def set_correlation_id():
        g.correlation_id = str(uuid.uuid4())

    return logger