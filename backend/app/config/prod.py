# Production configuration
# -----------------------------------------------------------------------------
import os
from dotenv import load_dotenv

load_dotenv()

from .default import DefaultConfig


class ProductionConfig(DefaultConfig):
    """Production configuration."""

    TESTING = False
    DEBUG = False
