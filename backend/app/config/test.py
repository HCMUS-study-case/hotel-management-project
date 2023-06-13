# Test configuration
# -----------------------------------------------------------------------------
import os
from dotenv import load_dotenv

load_dotenv()

from .default import DefaultConfig


class TestConfig(DefaultConfig):
    """Test configuration."""

    TESTING = True
    DEBUG = True
