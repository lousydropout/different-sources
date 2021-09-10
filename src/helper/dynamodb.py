import boto3
from boto3.dynamodb.types import TypeDeserializer

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
