import json

from google.cloud import secretmanager

secrets = secretmanager.SecretManagerServiceClient()


class Config:
    POSTGRES_SECRETS = json.loads(
        secrets.access_secret_version(
            request={
                "name": "projects/439044485118/secrets/postgres_secrets/versions/3"
            }
        ).payload.data.decode("utf-8")
    )
    POSTGRES_DB = "postgres"
    INSTANCE_CONNECTION = POSTGRES_SECRETS["private_ip"]
    SQLALCHEMY_DATABASE_BASE = (
        f"postgresql+psycopg2://{POSTGRES_SECRETS['user']}:"
        f"{POSTGRES_SECRETS['password']}"
    )
    SQLALCHEMY_DATABASE_URI = (
        f"{SQLALCHEMY_DATABASE_BASE}@/{POSTGRES_DB}"
        f"?host=/cloudsql/{INSTANCE_CONNECTION}"
    )
