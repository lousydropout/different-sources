import os
import json
from uuid import uuid4 as uuid
from helper import logger_setup
from helper import s3
from helper.dynamodb import is_execute_statement_successful, format_response

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from botocore.exceptions import ClientError
import boto3

logger = logger_setup.logger
app = FastAPI()

dynamodb = boto3.client("dynamodb")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#
class Env:
    table = os.environ["metadata_table"]
    storage = os.environ["storage"]


# SQL injection check
def raise_exception_if_unsafe(name: str) -> None:
    """Raise exception if name contains quotes. Else, do nothing."""
    if "'" in name or '"' in name:
        detail = "The input name must not contain quotes."
        raise HTTPException(status_code=403, detail=detail)


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


def handler(event: dict, context) -> dict:
    logger.info("Event: %s", json.dumps(event, default=str))

    api_handler = Mangum(app)
    return api_handler(event, context)
