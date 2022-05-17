from flask import Blueprint, request
from flask_restful import Api, Resource
import psycopg2
import json
import uuid

blueprint_sharable = Blueprint(
    name="blueprint_sharable", import_name=__name__)
api = Api(blueprint_sharable)

def get_sharable_data(sharable_id):
    conn = psycopg2.connect(
        host="localhost", port=5432, database="testdb3", user="postgres", password="admin")
    sharable_cursor = conn.cursor()

    # Get Sharable Info
    sharable_cursor.execute(f'SELECT sharable_id, shared_timestamp, sharable_type, num_of_likes, num_of_comments, description FROM sharable WHERE sharable_id=\'{sharable_id}\';')

    sharable_info = sharable_cursor.fetchone()
    if not sharable_info:
        return {"error": "Invalid Sharable Id"}, 4044

    sharable_info_formatted = {
        "sharableId": sharable_info[0],
        "sharedTimestamp": sharable_info[1].strftime("%m/%d/%Y, %H:%M:%S"),
        "sharableType": sharable_info[2],
        "numOfLikes": sharable_info[3],
        "numOfComments": sharable_info[4],
        "sharableDesc": sharable_info[5]
    }

    sharable_type = sharable_info[0][2]

    # Get User Id
    user_rel_cursor = conn.cursor()
    user_rel_cursor.execute(f'SELECT sharable_id, user_id FROM creates_sharable WHERE sharable_id=\'{sharable_id}\';')
    user_rel = user_rel_cursor.fetchone()

    user_id = user_rel[1]
    

    # Get User Data
    user_cursor = conn.cursor()
    user_cursor.execute(f'SELECT user_id, user_name, email FROM generic_user WHERE user_id={user_id};')
    user_data = user_cursor.fetchone()
    if not user_data:
        return {"error": "User Data Not Found"}, 400
    user_data_formatted = {
        "userId": user_data[0],
        "userName": user_data[1],
        "email": user_data[2]
    }

    content_dict = {}
    # Get Sharable Content Data
    content_rel_cursor = conn.cursor()
    content_cursor = conn.cursor()
    if sharable_type == "betslip":
        content_rel_cursor.execute(f'SELECT bet_slip_id FROM shared_bet WHERE sharable_id=\'{sharable_id}\';')
        bet_slip_id = content_rel_cursor.fetchone()
        if not bet_slip_id:
            return {"error": "No Bet Slip Data Associated With Sharable"}, 400
        
        # Get Bet Slip Data
        content_cursor.execute(f'SELECT bet_slip_id, finalizes_on, total_odd, mbn, bet_slip_state FROM bet_slip WHERE bet_slip_id={bet_slip_id[0]};')
        bet_slip_content = content_cursor.fetchone()
        
        # Get Associated Bets
        bets_cursor = conn.cursor()
        bets_cursor.execute(f'SELECT bet_id, bet_name, bet_desc, odd, type, playable_until FROM bet WHERE bet_id IN (SELECT bet_id FROM is_betted_on WHERE bet_slip_id={bet_slip_id[0]});')
        bets_list = bets_cursor.fetchall()
        if not bets_list:
            return {"error": "No Bets Found in Bet Slip."}, 400
        bets_formatted = [
            {
                "betId": bet_item[0],
                "betName": bet_item[1],
                "betDesc": bet_item[2],
                "odd": bet_item[3],
                "type": bet_item[4],
                "playableUntil": bet_item[5].strftime("%m/%d/%Y, %H:%M:%S")
            } for bet_item in bets_list
        ]
        content_dict = {
            "contentType": sharable_type,
            "betSlipData": {
                "betSlipId": bet_slip_content[0],
                "finalizesOn": bet_slip_content[1].strftime("%m/%d/%Y, %H:%M:%S"),
                "totalOdd": bet_slip_content[2],
                "mbn": bet_slip_content[3],
                "betSlipState": bet_slip_content[4]
            },
            "betsData": bets_formatted
        }
            


    else:
        content_rel_cursor.execute(f'SELECT photo_id FROM photo_is_in WHERE sharable_id=\'{sharable_id}\';')
        photo_id = content_rel_cursor.fetchone()
        if not photo_id:
            return {"error": "No Photo Id Associated With Sharable"}, 400
        content_cursor.execute(f'SELECT photo_id, photo_file FROM photo WHERE photo_id=\'{photo_id[0]}\';')
        photo_data = content_cursor.fetchone()
        if not photo_data:
            return {"error": "Photo Data Couldn't Be Found."}, 400

        content_dict = {
            "contentType": sharable_type,
            "photoId": photo_data[0],
            "photoUrl": photo_data[1]
        }

    conn.close()
    return {
        "sharableInfo": sharable_info_formatted,
        "sharableContent": content_dict,
        "userData": user_data_formatted
    }



class Sharable(Resource):
    def get(self):
        sharable_id = request.args.get("sharableId")
        sharable_data = get_sharable_data()
        return sharable_data, 200
        

        

    def post(self):
        post_body = request.json
        user_id = post_body["userId"]
        sharable_type = post_body["sharableType"]
        content_id = post_body["contentId"]
        sharable_desc = post_body["sharableDesc"]

        sharable_id = uuid.uuid4()
        conn = psycopg2.connect(
            host="localhost", port=5432, database="testdb3", user="postgres", password="admin")
        cursor = conn.cursor()

        cursor.execute(f'INSERT INTO sharable (sharable_id, shared_timestamp, sharable_type, num_of_likes, num_of_comments, description) VALUES (\'{sharable_id}\', current_timestamp, \'{sharable_type}\', 0, 0, \'{sharable_desc}\');')

        if sharable_type == "betslip":
            cursor.execute(f'INSERT INTO shared_bet (sharable_id, bet_slip_id) VALUES (\'{sharable_id}\', \'{content_id}\');')
        else:
            cursor.execute(f'INSERT INTO photo_is_in (sharable_id, photo_id) VALUES (\'{sharable_id}\', \'{content_id}\');')

        cursor.execute(f'INSERT INTO creates_sharable (sharable_id, user_id) VALUES (\'{sharable_id}\', {user_id});')

        conn.commit()

        conn.close()
        return {
            "message": "Sharable Created",
            "sharableId": sharable_id,
        }, 200


class UserPosts(Resource):
    def get(self):
        user_id = request.args.get("userId")
        




api.add_resource(Sharable, "/api/sharable")
api.add_resource(UserPosts, "/api/user-posts")

