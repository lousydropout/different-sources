import json
from helper import logger_setup
from helper.fastapi_setup import app

# import routes
from routes import parser_routes
from routes import schema_routes

from mangum import Mangum

logger = logger_setup.logger


def handler(event: dict, context) -> dict:
    logger.info("Event: %s", json.dumps(event, default=str))

    api_handler = Mangum(app)
    return api_handler(event, context)
