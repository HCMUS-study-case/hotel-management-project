import os
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config
from flask_argon2 import Argon2

# import blueprints
from .controllers import info
from .controllers.auth import auth

# create and configure the app
app = Flask(__name__, instance_relative_config=True)
app.config.from_object(Config)
# create and configure the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)
argon2 = Argon2(app)
# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

# Registering blueprint
app.register_blueprint(info)
app.register_blueprint(auth)


def create_app():
    # a simple page that says hello
    @app.route("/hello")
    def hello():
        return "Hello, World!"

    return app
