from os import getenv

from dotenv import load_dotenv

load_dotenv()
SECRET = getenv("SECRET")

EMAIL_HOST = getenv("EMAIL_HOST")
EMAIL_PORT = getenv("EMAIL_PORT")
EMAIL_HOST_USER = getenv("EMAIL_USER")
EMAIL_HOST_PASSWORD = getenv("EMAIL_PASS")


CLOUD_NAME = getenv("CLOUD_NAME")
CLOUD_KEY = getenv("CLOUD_KEY")
CLOUD_SECRET = getenv("CLOUD_SECRET")


PG_USER = getenv("PG_USER")
PG_PWD = getenv("PG_PWD")
PG_HOST = getenv("PG_HOST")
PG_PORT = getenv("PG_PORT")
PG_DB_NAME = getenv("PG_DB_NAME")

DB_URI = f"postgresql+asyncpg://{PG_USER}:{PG_PWD}@{PG_HOST}:{PG_PORT}/{PG_DB_NAME}"
