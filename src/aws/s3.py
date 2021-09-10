from helper import logger_setup
import boto3

logger = logger_setup.logger
s3 = boto3.client("s3")


def create_presigned_post(bucket_name: str, category: str, name: str) -> dict:
    expiration = 600  # 10 minutes

    key = get_key(category, name)
    presigned = s3.generate_presigned_post(
        bucket_name, key, ExpiresIn=expiration
    )

    return {"presigned": presigned, "bucket": bucket_name, "key": key}


def get_key(category: str, name: str) -> str:
    return f"{category}/{name}"
