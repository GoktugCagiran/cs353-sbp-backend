from flask import Blueprint, request
from flask_restful import Api, Resource
from util.auth_token_helper import check_if_token_valid
from config.const_variables import SCRATCH_OFF_BOX_COUNT
from datetime import time
import json
import psycopg2
import numpy as np
import uuid

blueprint_scratch_off = Blueprint(
    name="blueprint_scratch_off", import_name=__name__)
api = Api(blueprint_scratch_off)


class GetUserScratchOffs(Resource):
    def get(self):
        user_id = request.args.get("userId", type=int)
        auth_token = request.headers.get("Authorization", type=str)
        auth_token_valid = check_if_token_valid(auth_token)
        if not auth_token_valid:
            return {"error": "Auth Token Invalid"}, 400
        conn = psycopg2.connect(
            host="localhost", port=5432, database="cs353DB", user="gcagiran")
        cursor = conn.cursor()

        cursor.execute(
            f'SELECT scratch_off_id, boxes, won_amount, is_won, played_timestamp FROM scratch_off NATURAL JOIN scratched_by WHERE played_by={user_id}')

        query_res = cursor.fetchall()

        response_data = [{"scratchOffId": x[0], "boxes": x[1], "wonAmount": x[2], "isWon": x[3],
                          "playedTimestamp": x[4].strftime("%m/%d/%Y, %H:%M:%S")} for x in query_res]

        return {
            "scratchOffs": response_data
        }, 200


class GetScratchOff(Resource):
    def get(self):
        scratch_off_id = request.args.get("scratchOffId", type=str)
        conn = psycopg2.connect(
            host="localhost", port=5432, database="cs353DB", user="gcagiran")
        cursor = conn.cursor()

        cursor.execute(f'SELECT scratch_off_id, boxes, won_amount, is_won, played_timestamp FROM scratch_off NATURAL JOIN scratched_by WHERE scratch_off_id=\'{scratch_off_id}\';')

        query_res = cursor.fetchone()

        response_data = {
            "scratchOffId" : query_res[0],
            "boxes": query_res[1],
            "wonAmount": query_res[2],
            "isWon": query_res[3],
            "playedTimestamp": query_res[4].strftime("%m/%d/%Y, %H:%M:%S")
        }

        return {
            "scratchOffData": response_data
        }, 200


class NewScratchOff(Resource):
    def post(self):
        post_data = request.json
        auth_token = request.headers.get("Authorization", type=str)
        auth_token_valid = check_if_token_valid(auth_token)
        if not auth_token_valid:
            return {"error": "Auth Token Invalid"}, 400

        scratch_off_id = uuid.uuid4()

        conn = psycopg2.connect(
            host="localhost", port=5432, database="cs353DB", user="gcagiran")
        cursor = conn.cursor()
        cursor.execute(
            f'SELECT reward_id, title, description, value FROM reward WHERE is_available=true;')
        available_rewards = cursor.fetchall()
        print("Available Rewards: ", available_rewards)
        ar_length = len(available_rewards)
        reward_placed_count = {}
        scratch_off_won = False
        reward_index = -1
        for i in range(ar_length):
            reward_placed_count[i] = 0

        boxes = {}
        box_placed_count = 0
        while box_placed_count < SCRATCH_OFF_BOX_COUNT:
            rand_num = np.random.randint(0, ar_length + 5)
            if rand_num < ar_length:
                if scratch_off_won and (reward_placed_count[rand_num] + 1 >= 3):
                    continue

                reward_placed_count[rand_num] = reward_placed_count[rand_num] + 1
                if reward_placed_count[rand_num] == 3:
                    scratch_off_won = True
                    reward_index = rand_num

                # Place Reward Data in Box
                boxes[box_placed_count] = available_rewards[rand_num]
            else:
                # Set Box to NULL
                boxes[box_placed_count] = None

            box_placed_count += 1
        won_amount = {
                "rewardId": available_rewards[reward_index][0],
                "rewardTitle": available_rewards[reward_index][1],
                "rewardDescription": available_rewards[reward_index][2],
                "rewardValue": available_rewards[reward_index][3],
            } if scratch_off_won else {}
        cursor.execute(
            f'INSERT INTO scratch_off (scratch_off_id, boxes, boxes_str, won_amount, won_amount_str, is_won) VALUES (\'{scratch_off_id}\', \'{json.dumps(boxes)}\', ARRAY [\'{json.dumps(boxes)}\'], \'{json.dumps(won_amount)}\', ARRAY [\'{json.dumps(won_amount)}\'], {scratch_off_won});')
        cursor.execute(
            f'INSERT INTO scratched_by (played_by, scratch_off_id, played_timestamp) VALUES ({post_data["userId"]}, \'{scratch_off_id}\', current_timestamp);')
        # Save Reward as Won To User
        if scratch_off_won:
            
            cursor.execute(
                f'INSERT INTO won_by (user_id, reward_id, won_timestamp, from_scratch_off) VALUES ({post_data["userId"]}, {won_amount["rewardId"]}, current_timestamp, \'{scratch_off_id}\');')

        conn.commit()
        conn.close()
        return {"message": "Scratch Off Created", "scratchOffData": {
            "boxes": boxes,
            "isWon": scratch_off_won,
            "reward": {
                "rewardId": available_rewards[reward_index][0],
                "rewardTitle": available_rewards[reward_index][1],
                "description": available_rewards[reward_index][2],
                "value": available_rewards[reward_index][3],
            }
        }}, 200


api.add_resource(NewScratchOff, "/api/scratch-off/new")
api.add_resource(GetUserScratchOffs, "/api/scratch-off/user-get-all")
api.add_resource(GetScratchOff, "/api/scratch-off/detail")
