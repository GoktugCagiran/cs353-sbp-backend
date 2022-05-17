from flask import Blueprint, request
from flask_restful import Api, Resource
import psycopg2
import numpy as np
import uuid

blueprint_reward = Blueprint(
    name="blueprint_reward", import_name=__name__)
api = Api(blueprint_reward)


class Reward(Resource):
    def get(self):
        reward_id = request.args.get("rewardId")

        conn = psycopg2.connect(
            host="localhost", port=5432, database="testdb3", user="postgres", password="admin")

        cursor = conn.cursor()

        cursor.execute(f'SELECT reward_id, title, description, value, is_available FROM reward WHERE reward_id={reward_id};')

        reward_data = cursor.fetchone()

        if not reward_data:
            return {'error': "Reward Not Found"}, 400
        
        reward_dict = {
            "rewardId": reward_data[0],
            "title": reward_data[1],
            "description": reward_data[2],
            "value": reward_data[3],
            "isAvailable": reward_data[4]
        }

        conn.close()

        return {"rewardData": reward_dict}, 200


    def post(self):
        post_body = request.json

        conn = psycopg2.connect(
            host="localhost", port=5432, database="testdb3", user="postgres", password="admin")

        cursor = conn.cursor()

        cursor.execute(f'INSERT INTO reward (reward_id, title, description, value, is_available) VALUES (DEFAULT, {post_body["title"]}, {post_body["description"]}, {post_body["value"]}, {post_body["isAvailable"]});')

        conn.commit()

        conn.close()

        return {"message": "Reward Created Successfully"}, 200

api.add_resource(Reward, "/api/reward")