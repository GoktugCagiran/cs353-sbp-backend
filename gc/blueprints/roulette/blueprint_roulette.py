from flask import Blueprint, request
from flask_restful import Api, Resource
from util.auth_token_helper import check_if_token_valid
from util.wallet_helper import check_user_balance, reduce_user_balance
from config.const_variables import SCRATCH_OFF_BOX_COUNT
from datetime import time
import json
import psycopg2
import numpy as np
import uuid


blueprint_roulette = Blueprint(
    name="blueprint_roulette", import_name=__name__)
api = Api(blueprint_roulette)

class PlayRoulette(Resource):

    def get_ball_drop_colour(ball_num):
        if ball_num in [37, 38]:
            return "green"
        elif ball_num % 2 == 0:
            return "black"
        else:
            return "red"

    def post(self):
        body_data = request.json

        user_id = body_data["userId"]
        bet_amount = body_data["betAmount"]
        placed_bets = body_data["placedBets"]

        user_balance_valid = check_user_balance(user_id, bet_amount)
        if not user_balance_valid:
            return {"error": "Insufficient Balance."}, 400

        reduce_user_balance(user_id, bet_amount)
        conn = psycopg2.connect(
            host="localhost", port=5432, database="cs353DB", user="gcagiran")
        cursor = conn.cursor()
        cursor.execute(
            f'SELECT reward_id, title, description, value FROM reward WHERE is_available=true;')
        
        available_rewards = cursor.fetchall()

        roulette_id = uuid.uuid4()

        is_reward_placed = False
        placed_on = -1
        reward = None
        reward_won = False
        is_won = False
        won_amount = 0
        place_reward = np.random.randint(0,100)
        if place_reward > 96:
            is_reward_placed = True
            placed_on = np.random.randint(1,39)
            select_reward = np.random.randint(0, len(available_rewards))
            reward = available_rewards[select_reward]
            


        # 0 => 37 00 => 38
        ball_drop = np.random.randint(1,39)
        ball_drop_colour = self.get_ball_drop_colour(ball_drop)
        if placed_bets["type"] == "color":
            
            # Check green
            if placed_bets["placedOn"] == "green" and ball_drop_colour == "green":
                is_won = True
                won_amount = bet_amount * 2
            # Check black
            elif placed_bets["placedOn"] == "black" and ball_drop_colour == "black":
                is_won = True
                won_amount = bet_amount * 1.5
            # Check Red
            elif placed_bets["placedOn"] == "red" and ball_drop_colour == "red":
                is_won = True
                won_amount = bet_amount * 1.5
        else:
            if placed_bets["placedOn"] == ball_drop:
                is_won = True
                if ball_drop in [37,38]:
                    won_amount = bet_amount * 10
                else:
                    won_amount = bet_amount * 6

            if is_reward_placed and placed_bets["placedOn"] == placed_on:
                reward_won = True
                
        res_dict = {
            "ballDrop": ball_drop,
            "ballDropColour": ball_drop_colour
        }
        wheel_data_dict = {
            "rewardPlaced": is_reward_placed,
            
        }
        if is_reward_placed:
            wheel_data_dict["rewardWon"] = reward_won,
            wheel_data_dict["rewardId"] = reward[0]
        cursor.execute(f'INSERT INTO roulette (roulette_id, placed_bets, result, bet_amount, is_won, won_amount, wheel_data) VALUES ({roulette_id}, {placed_bets}, {res_dict}, {bet_amount}, {is_won}, {won_amount}, {wheel_data_dict});')
        cursor.execute(f'INSERT INTO spinned_by (user_id, roulette_id, spinned_timestamp) VALUES ({user_id}, {roulette_id}, current_timestamp);')
        if is_reward_placed:
            cursor.execute(f'INSERT INTO placed_on_slot (roulette_id, reward_id, slot_id) VALUES ({roulette_id}, {reward[0]}, {placed_on});')

        conn.commit()

        conn.close()

        
        return {
            "betWon": is_won,
            "wonAmount": won_amount,
            "rewardWon": reward_won,
            "reward": reward,
        }, 200
        



api.add_resource(PlayRoulette, "/api/roulette/play")

