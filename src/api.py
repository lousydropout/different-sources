import json


def handler(event: dict, context):
    print(f"Event: {json.dumps(event, default=str)}")
