from flask import Blueprint, request
from flask_restful import Api, Resource
import psycopg2
import numpy as np
import uuid

blueprint_admin = Blueprint(
    name="blueprint_admin", import_name=__name__)

api = Api(blueprint_admin)

class DeactivateUser(Resource):
    def update(self):

        request_body = request.json

        user_id = request_body["userId"]
        conn = psycopg2.connect(
            host="localhost", port=5432, database="cs353DB", user="gcagiran")
        cursor = conn.cursor()

        cursor.execute(f'UPDATE generic_user SET user_active=FALSE WHERE user_id=\'{user_id}\';')

        conn.commit()

        conn.close()

        return {"message": "User Deactivated."}, 200

class ActivateUser(Resource):
    def update(self):

        request_body = request.json

        user_id = request_body["userId"]
        conn = psycopg2.connect(
            host="localhost", port=5432, database="cs353DB", user="gcagiran")
        cursor = conn.cursor()

        cursor.execute(f'UPDATE generic_user SET user_active=TRUE WHERE user_id=\'{user_id}\';')

        conn.commit()

        conn.close()

        return {"message": "User Activated."}, 200

api.add_resource(DeactivateUser, "/api/admin/deactivate-user")
api.add_resource(ActivateUser, "/api/admin/activate-user")