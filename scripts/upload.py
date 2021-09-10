import sys
import requests
import json

base = "https://pur7c54ejc.execute-api.us-west-2.amazonaws.com/prod"


def upload_file(presigned_response: dict, object) -> bool:
    response = requests.post(
        presigned_response["url"],
        data=presigned_response["fields"],
        files={"file": open(object, "rb")},
    )
    return int(response.status_code) // 100 == 2


def upload_type(category: str, object):

    # 1. get presigned post url to upload file
    object_name = object.split("/")[-1]
    url = f"{base}/{category}?name={object_name}"
    response = requests.post(url)
    print("response: ", response)
    response = json.loads(response.text)
    print("response: ", response)

    # 2. Upload the file
    presigned = response["presigned"]
    response = upload_file(presigned, object)
    print("upload file response: ", response)

    # 3. let API know file is uploaded
    url = f"{url}&uploaded=true"
    response = requests.post(url)
    print("upload complete response: ", response)


def print_error_message():
    print("\nUsage: python upload.py <category> <file>")
    print("  <category> = parsers | schemas | mappings")
    print("Example: python upload.py parsers ../examples/parser_1.py")
    print("")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print_error_message()
        exit(1)

    category = sys.argv[1]
    if category not in {"parsers", "schemas", "mappings"}:
        print_error_message()
        exit(1)

    object = sys.argv[2]

    upload_type(category, object)
