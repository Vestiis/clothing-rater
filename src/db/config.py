import json

from google.cloud import secretmanager

secrets = secretmanager.SecretManagerServiceClient()


class Config:
    INSTANCE_CONNECTION = "impactful-ring-314819:europe-west1:clothing-rater-postgres"
    POSTGRES_DB = "postgres"
    POSTGRES_SECRETS = json.loads(
        secrets.access_secret_version(
            request={
                "name": "projects/439044485118/secrets/postgres_secrets/versions/1"
            }
        ).payload.data.decode("utf-8")
    )
    SQLALCHEMY_DATABASE_BASE = (
        f"postgresql+psycopg2://{POSTGRES_SECRETS['user']}:"
        f"{POSTGRES_SECRETS['password']}"
    )
    SQLALCHEMY_DATABASE_URI = (
        f"{SQLALCHEMY_DATABASE_BASE}@/{POSTGRES_DB}"
        f"?host=/cloudsql/{INSTANCE_CONNECTION}"
    )
