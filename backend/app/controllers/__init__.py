# hello world
from flask import Blueprint
from flask_restful import Resource, Api

info = Blueprint("info", __name__, url_prefix="/")
api = Api(info)


class Info(Resource):
    def get(self):
        return {
            "message": "API is running",
            "status": "success",
        }


api.add_resource(Info, "/")
