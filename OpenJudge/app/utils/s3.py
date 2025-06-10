import os
import base64
import boto3

def get_bucket():
    return os.getenv("S3_BUCKET", "coughoverflow-image-bucket1hyc")

def get_s3_client():
    return boto3.client("s3", region_name=os.getenv("us-east-1"))

def upload_image_to_s3(base64_str, key):
    try:
        bucket = get_bucket()
        s3 = get_s3_client()
        image_bytes = base64.b64decode(base64_str)
        s3.put_object(Bucket=bucket, Key=key, Body=image_bytes)
        return key
    except Exception as e:
        raise RuntimeError(f"failed: {e}")

def download_image_from_s3(key, destination_path):
    try:
        bucket = get_bucket()
        s3 = get_s3_client()
        with open(destination_path, "wb") as f:
            s3.download_fileobj(bucket, key, f)
    except Exception as e:
        raise RuntimeError(f"failed: {e}")
