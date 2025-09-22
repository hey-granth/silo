from dotenv import load_dotenv
import os
import boto3


load_dotenv()

class Config:
    AUTH0_ALGORITHMS: list[str] = ["RS256"]
    AUTH0_DOMAIN: str = os.getenv("AUTH0_DOMAIN")
    AUTH0_CLIENT_ID: str = os.getenv("AUTH0_CLIENT_ID")
    AUTH0_CLIENT_SECRET: str = os.getenv("AUTH0_CLIENT_SECRET")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    AUTH0_AUDIENCE: str = os.getenv("AUTH0_AUDIENCE")
    AUTH0_IDENTIFIER: str = os.getenv("AUTH0_IDENTIFIER")

    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY")
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET_NAME")
    s3_client = boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        region_name="us-east-1",  # not for minio, but required by boto3
    )

    FILE_TYPE_CHOICES: list[tuple[str, str]] = [
        ("image/jpeg", "JPEG Image"),
        ("image/png", "PNG Image"),
        ("application/pdf", "PDF Document"),
        ("text/plain", "Plain Text"),
        ("application/zip", "ZIP Archive"),
        ("video/mp4", "MP4 Video"),
        ("audio/mpeg", "MP3 Audio"),
        ("application/vnd.ms-excel", "Excel Spreadsheet"),
    ]

    PLAN_CHOICES: list[tuple[str, str]] = [
        ("free", "Free"),
        ("pro", "Pro"),
        ("enterprise", "Enterprise"),
    ]