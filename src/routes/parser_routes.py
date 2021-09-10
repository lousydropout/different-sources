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


# /parsers
@app.get("/parsers")
def list_parsers() -> dict:
    statement = (
        f"""SELECT * FROM "{Env.table}" WHERE BEGINS_WITH("pk", 'parsers');"""
    )
    logger.info("Statement: %s", statement)

    try:
        response = dynamodb.execute_statement(Statement=statement)
    except ClientError as err:
        logger.exception(err)
        raise HTTPException(status_code=400, detail="Something went wrong.")

    logger.info(
        "GET /parsers response: %s",
        json.dumps(response, default=str),
    )
    logger.info("Successful: %s", is_execute_statement_successful(response))

    return format_response(response)


@app.get("/parsers/{name}")
def list_parsers(name: str) -> dict:
    raise_exception_if_unsafe(name)

    value = f"parsers#{name}"
    statement = f"""SELECT * FROM "{Env.table}" WHERE "pk"='{value}' AND "sk"='{value}';"""
    logger.info("Statement: %s", statement)

    try:
        response = dynamodb.execute_statement(Statement=statement)
    except ClientError as err:
        logger.exception(err)
        raise HTTPException(status_code=400, detail="Something went wrong.")

    logger.info(
        "GET /parsers/{name} response: %s",
        json.dumps(response, default=str),
    )
    logger.info("Successful: %s", is_execute_statement_successful(response))

    return format_response(response)


@app.post("/parsers", status_code=201)
def create_parser(name: str = str(uuid())) -> dict:
    data = {
        "pk": f"parsers#{name}",
        "sk": f"parsers#{name}",
        "bucket": Env.storage,
        "key": s3.get_key("parsers", name),
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
        "POST /parsers?name={name} response: %s",
        json.dumps(response, default=str),
    )
    logger.info("Successful: %s", is_execute_statement_successful(response))

    return s3.create_presigned_post(Env.storage, "parsers", name)