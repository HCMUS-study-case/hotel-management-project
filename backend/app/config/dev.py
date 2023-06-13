# Development configuration
# -----------------------------------------------------------------------------
import os
from dotenv import load_dotenv

load_dotenv()

from .default import DefaultConfig


class DevelopmentConfig(DefaultConfig):
    """Development configuration."""

    TESTING = True
    DEBUG = True
