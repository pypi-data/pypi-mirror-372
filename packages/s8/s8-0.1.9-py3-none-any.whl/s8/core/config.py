# common/core/config.py
import os
import json
from pathlib import Path
from dotenv import load_dotenv
import boto3

class Settings:
    def __init__(self):
        # ---------------------
        # Load local .env if exists
        # ---------------------
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)

        # ---------------------
        # Detect environment: EC2, Render, Local
        # ---------------------
        # If running on EC2 (Secrets Manager), fetch secrets
        if os.getenv("USE_SECRETS_MANAGER", "false").lower() == "true":
            self._load_from_secrets_manager()
        else:
            # Local or Render
            self._load_from_env()

    def _load_from_env(self):
        # MongoDB
        self.MONGO_URL = os.getenv("MONGO_URL")
        # JWT
        self.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
        self.JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")
        self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "10080"))
        # SMTP
        self.SMTP_SERVER = os.getenv("SMTP_SERVER")
        self.SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
        self.SMTP_USER = os.getenv("SMTP_USER")
        self.SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
        # Admin
        self.ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
        self.ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")
        # AWS / S3 / SQS
        self.AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
        self.AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.AWS_REGION = os.getenv("AWS_REGION", "eu-north-1")
        self.BUCKET_NAME = os.getenv("BUCKET_NAME", "s8templates")
        self.SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")

    def _load_from_secrets_manager(self):
        secret_name = "prod/s8Backend/env"
        region_name = os.getenv("AWS_REGION", "eu-north-1")

        client = boto3.client("secretsmanager", region_name=region_name)
        response = client.get_secret_value(SecretId=secret_name)
        secrets = json.loads(response["SecretString"])

        # MongoDB
        self.MONGO_URL = secrets.get("MONGO_URL")
        # JWT
        self.JWT_SECRET_KEY = secrets.get("JWT_SECRET_KEY")
        self.JWT_REFRESH_SECRET_KEY = secrets.get("JWT_REFRESH_SECRET_KEY")
        self.ALGORITHM = secrets.get("ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(secrets.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
        self.REFRESH_TOKEN_EXPIRE_MINUTES = int(secrets.get("REFRESH_TOKEN_EXPIRE_MINUTES", 10080))
        # SMTP
        self.SMTP_SERVER = secrets.get("SMTP_SERVER")
        self.SMTP_PORT = int(secrets.get("SMTP_PORT", 587))
        self.SMTP_USER = secrets.get("SMTP_USER")
        self.SMTP_PASSWORD = secrets.get("SMTP_PASSWORD")
        # Admin
        self.ADMIN_EMAIL = secrets.get("ADMIN_EMAIL")
        self.ADMIN_PASSWORD_HASH = secrets.get("ADMIN_PASSWORD_HASH")
        # AWS / S3 / SQS
        self.AWS_ACCESS_KEY_ID = secrets.get("AWS_ACCESS_KEY_ID")
        self.AWS_SECRET_ACCESS_KEY = secrets.get("AWS_SECRET_ACCESS_KEY")
        self.AWS_REGION = secrets.get("AWS_REGION", "eu-north-1")
        self.BUCKET_NAME = secrets.get("BUCKET_NAME", "s8templates")
        self.SQS_QUEUE_URL = secrets.get("SQS_QUEUE_URL")

# Instantiate settings
settings = Settings()
