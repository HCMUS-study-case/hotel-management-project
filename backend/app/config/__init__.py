from .dev import DevelopmentConfig
from .prod import ProductionConfig
from .test import TestConfig

import os
from dotenv import load_dotenv

load_dotenv()

config = {
    "dev": DevelopmentConfig,
    "prod": ProductionConfig,
    "test": TestConfig,
}

config_name = os.getenv("FLASK_ENV", "dev")

Config = config[config_name]
