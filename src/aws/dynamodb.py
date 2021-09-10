from helper import logger_setup
from helper.fastapi_setup import HTTPException

from botocore.exceptions import ClientError
import boto3
from boto3.dynamodb.types import TypeDeserializer

logger = logger_setup.logger
dynamodb = boto3.client("dynamodb")
deserializer = TypeDeserializer()

# Check if dynamodb.execute_statement was successful
def is_execute_statement_successful(response: dict) -> bool:
    status_code = response.get("ResponseMetadata", {}).get(
        "HTTPStatusCode", 400
    )
    return status_code // 100 == 2


def format_response(response: dict) -> dict:
    return {
        "Items": [
            {k: deserializer.deserialize(v) for k, v in x.items()}
            for x in response["Items"]
        ]
    }


def execute_statement(statement: str) -> dict:
    try:
        response = dynamodb.execute_statement(Statement=statement)
    except dynamodb.exceptions.DuplicateItemException as err:
        # since the record already exists, there's no problem
        logger.warning(err)
        response = {"warning": "duplicate item"}
    except ClientError as err:
        logger.exception(err)
        raise HTTPException(status_code=400, detail="Something went wrong.")

    return response
