import json
from uuid import uuid4 as uuid
from helper import logger_setup
from helper.env import Env
from helper.fastapi_setup import app, raise_exception_if_unsafe, HTTPException
from aws import s3
from aws.dynamodb import is_execute_statement_successful, format_response

from botocore.exceptions import ClientError
import boto3

logger = logger_setup.logger

dynamodb = boto3.client("dynamodb")


# /schemas
@app.get("/schemas")
def list_schemas() -> dict:
    statement = (
        f"""SELECT * FROM "{Env.table}" WHERE BEGINS_WITH("pk", 'schemas');"""
    )
    logger.info("Statement: %s", statement)

    try:
        response = dynamodb.execute_statement(Statement=statement)
    except ClientError as err:
        logger.exception(err)
        raise HTTPException(status_code=400, detail="Something went wrong.")

    logger.info(
        "GET /schemas response: %s",
        json.dumps(response, default=str),
    )
    logger.info("Successful: %s", is_execute_statement_successful(response))

    return format_response(response)


@app.get("/schemas/{name}")
def list_schemas(name: str) -> dict:
    raise_exception_if_unsafe(name)

    value = f"schemas#{name}"
    statement = f"""SELECT * FROM "{Env.table}" WHERE "pk"='{value}' AND "sk"='{value}';"""
    logger.info("Statement: %s", statement)

    try:
        response = dynamodb.execute_statement(Statement=statement)
    except ClientError as err:
        logger.exception(err)
        raise HTTPException(status_code=400, detail="Something went wrong.")

    logger.info(
        "GET /schemas/{name} response: %s",
        json.dumps(response, default=str),
    )
    logger.info("Successful: %s", is_execute_statement_successful(response))

    return format_response(response)


@app.post("/schemas", status_code=201)
def create_schema(name: str = str(uuid())) -> dict:
    data = {
        "pk": f"schemas#{name}",
        "sk": f"schemas#{name}",
        "bucket": Env.storage,
        "key": s3.get_key("schemas", name),
        "uploaded": False,
    }
    statement = f"""INSERT INTO "{Env.table}" VALUE {data};"""
    logger.info("Statement: %s", statement)

    try:
        response = dynamodb.execute_statement(Statement=statement)
    except dynamodb.exceptions.DuplicateItemException as err:
        logger.exception(err)
        detail = "DuplicateItemError: {name} already exists."
        raise HTTPException(status_code=400, detail=detail)
    except ClientError as err:
        logger.exception(err)
        raise HTTPException(status_code=400, detail="Something went wrong.")

    logger.info(
        "POST /schemas?name={name} response: %s",
        json.dumps(response, default=str),
    )
    logger.info("Successful: %s", is_execute_statement_successful(response))

    return s3.create_presigned_post(Env.storage, "schemas", name)
