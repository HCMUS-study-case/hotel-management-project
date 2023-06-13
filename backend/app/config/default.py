# Default Configurations
# -----------------------------------------------------------------------------
import os
import secrets
from dotenv import load_dotenv

load_dotenv()


class DefaultConfig(object):
    """Base config, uses staging database server."""

    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(16))
    DB_SERVER = os.environ.get("DB_SERVER", "localhost")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "PG_URL", f"postgresql://postgres:postgres@{DB_SERVER}/flaskr"
    )
