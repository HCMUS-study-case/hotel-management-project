from flask import Blueprint
from flask_restful import Resource, Api


auth = Blueprint("auth", __name__, url_prefix="/auth")
api = Api(auth)


class Login(Resource):
    def post(self):
        pass


api.add_resource(Login, "/login")
