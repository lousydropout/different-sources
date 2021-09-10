import os
import sys
import json
from typing import Tuple
from helper import logger_setup

import boto3

logger = logger_setup.logger
s3 = boto3.client("s3")

mappings = json.load(open("mapping.json", "r"))


class Env:
    table = os.environ["metadata_table"]
    storage = os.environ["storage"]
    apigw = os.environ["apigw"].rstrip("/")


def download_parser(file: str) -> bool:
    """Download the parser python file from S3 into /tmp."""
    try:
        s3.download_file(Env.storage, f"parsers/{file}", "/tmp/parser.py")
    except:
        return False
    return True


def get_mapping(data: dict) -> Tuple[str, dict]:
    """Get the appropriate parser name & mapping for the given data."""
    data_format = data["type"]
    pre_mapping = mappings[data_format]
    parser_name = list(pre_mapping)[0]
    logger.info("Parser: %s", parser_name)

    mapping: dict = pre_mapping[parser_name]
    logger.info("Mapping: %s", json.dumps(mapping, default=str))

    return parser_name, mapping


def handler(data: dict, context):
    logger.info("Event: %s", json.dumps(data, default=str))

    # Parse out the appropriate information
    parser_name, mapping = get_mapping(data)

    # Download parser from S3 into /tmp
    success = download_parser(parser_name)
    if not success:
        raise Exception(f"Failed to download parser {parser_name}")

    # Import Parser dataclass from /tmp
    sys.path.insert(0, os.path.abspath("/tmp"))
    from parser import Parser

    # Instantiate dataclass
    parser = Parser(data=data, mapping=mapping)

    # Print info
    logger.info("First name: %s", parser.first_name())
    logger.info("Last name: %s", parser.last_name())
    logger.info("Age: %s", parser.age())
    logger.info("Loan ammount: %s", parser.loan_amount())
