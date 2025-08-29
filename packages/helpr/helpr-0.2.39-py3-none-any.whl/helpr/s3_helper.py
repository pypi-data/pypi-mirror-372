import boto3
from fastapi import HTTPException, UploadFile
from botocore.exceptions import BotoCoreError, ClientError

def is_bucket_public(bucket_name: str, region: str) -> bool:
    """
    Check if an S3 bucket is public using bucket policy status.

    Args:
        bucket_name (str): S3 bucket name.
        region (str): AWS region.

    Returns:
        bool: True if bucket is public, False otherwise.
    """
    s3_client = boto3.client("s3", region_name=region)
    try:
        result = s3_client.get_bucket_policy_status(Bucket=bucket_name)
        return result["PolicyStatus"]["IsPublic"]
    except ClientError as e:
        # If bucket has no policy, it defaults to private
        if e.response["Error"]["Code"] == "NoSuchBucketPolicy":
            return False
        print(f"Error checking bucket policy status: {e}")
        return False

def upload_to_s3(
    file: UploadFile,
    key: str,
    bucket_name: str,
    region: str,
    expiry_seconds: int = 3600
) -> str:
    """
    Upload a file to AWS S3 and return appropriate URL based on bucket visibility.

    Args:
        file (UploadFile): File to upload (from FastAPI UploadFile).
        key (str): S3 object key (path + filename).
        bucket_name (str): S3 bucket name.
        region (str): AWS region name.
        expiry_seconds (int): Expiry time for presigned URL if bucket is private.

    Returns:
        str: Public URL (if bucket is public) or Pre-signed URL (if bucket is private).
    """
    s3_client = boto3.client("s3", region_name=region)

    try:
        s3_client.upload_fileobj(
            file.file,
            bucket_name,
            key,
            ExtraArgs={"ContentType": file.content_type}
        )
    except ClientError as e:
        # AWS client-side error
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload file to S3: {e.response['Error']['Message']}"
        )
    except BotoCoreError as e:
        # AWS core error
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected AWS error during upload: {str(e)}"
        )
    except Exception as e:
        # Other errors
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during upload: {str(e)}"
        )

    # Decide which URL to return based on bucket visibility
    if is_bucket_public(bucket_name, region):
        return f"https://{bucket_name}.s3.{region}.amazonaws.com/{key}"
    else:
        return generate_presigned_url(
            key=key,
            bucket_name=bucket_name,
            region=region,
            expiry_seconds=expiry_seconds
        )

def generate_presigned_url(
    key: str,
    bucket_name: str,
    region: str,
    expiry_seconds: int = 3600
) -> str:
    """
    Generate a pre-signed URL for an S3 object.

    Args:
        key (str): S3 object key.
        bucket_name (str): S3 bucket name.
        region (str): AWS region.
        expiry_seconds (int): Expiry time in seconds (default 1 hour).

    Returns:
        str: Pre-signed URL.
    """
    s3_client = boto3.client("s3", region_name=region)
    try:
        return s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": key},
            ExpiresIn=expiry_seconds
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate pre-signed URL: {str(e)}"
        )