from dotenv import load_dotenv
import os
from minio import Minio


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
    MINIO_SECURE: bool = os.getenv("MINIO_SECURE", "True").lower() in ("true", "1", "t")
    s3_client = Minio(
        MINIO_ENDPOINT.replace("http://", "").replace("https://", ""),
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE,
    )
    # Implemented Minio official sdk instead of boto3 for simplicity, as we only need basic S3 operations. Also, Minio sdk is more lightweight. No extra overhead and dependencies.

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
