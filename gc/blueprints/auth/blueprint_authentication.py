from flask import Blueprint, jsonify, request, Response
from flask_restful import Api, Resource
from flask_cors import CORS, cross_origin
import psycopg2

from util.auth_token_helper import get_auth_token, save_new_token, revoke_token

blueprint_authentication = Blueprint(
    name="blueprint_registration", import_name=__name__)
api = Api(blueprint_authentication)


class HelloWorld(Resource):
    def get(self):
        return {'data': 'Hello World'}


class RegisterUser(Resource):
    def post(self):
        post_data = request.json
        
    #    post_data = {
    #        "fullName": "Python Test Full Name",
    #        "password": "123456",
    #        "age": 25,
    #        "gender": "Male",
    #        "phoneNumber": "111222333444",
    #        "username": "pyTestInit",
    #        "email": "init@pytest.com",
    #    }
        conn = psycopg2.connect(
            host="localhost", port=5432, database="testdb3", user="postgres", password="admin")
        cursor = conn.cursor()
        cursor.execute(
            f'INSERT INTO generic_user VALUES (DEFAULT, \'{post_data["password"]}\', \'{post_data["fullName"]}\', current_timestamp, {post_data["age"]}, \'{post_data["gender"]}\', \'{post_data["phoneNumber"]}\', \'{post_data["username"]}\', \'{post_data["email"]}\' );')
        conn.commit()
        conn.close()        
        print("New User Data: ", post_data)

        return {'result': 'User Created Successfully'}, 200


class LoginUser(Resource):
    def get(self):
        user_authenticated = False
        auth_token = None

        user_creds_correct = False
        user_creds = request.args
        print(user_creds)
        print('User Name: ', user_creds.get('userName'))
        print('typeof userName', type(user_creds.get('userName')))
        print('password: ', user_creds.get('password') )
        conn = psycopg2.connect(host="localhost", port=5432, database="testdb3", user="postgres", password="admin")
        cursor = conn.cursor()
        cursor.execute(f'SELECT user_id, password FROM generic_user WHERE user_name=\'{user_creds.get("userName")}\'')
        row = cursor.fetchone()
        if row is not None:
            print('User Data Found userName: ', user_creds.get('userName'))
            passw_from_db = row[1]
            print('Password From DB: ', passw_from_db)
            if passw_from_db == user_creds.get('password'):
                print('Passwords Matches!!!')
                user_creds_correct = True
                auth_token_res = get_auth_token(row[0])
                print('Auth Token Res from get: ', auth_token_res)
                if auth_token_res['auth_token_found']:
                    if auth_token_res['token_valid']:
                        user_authenticated = True
                        auth_token = auth_token_res['auth_token']
                    else:
                        new_token_res = save_new_token(row[0])
                        print('New Auth Token Res: ', new_token_res)
                        user_authenticated = True
                        auth_token = new_token_res['auth_token']
                else:
                    new_token_res = save_new_token(row[0])
                    print('New Auth Token Res: ', new_token_res)
                    user_authenticated = True
                    auth_token = new_token_res['auth_token']
        conn.close()
        return {
            'userAuthenticated': user_authenticated,
            'authToken': auth_token
        }, 200

class LogoutUser(Resource):
    def post(self):
        post_data = request.json
        user_id = post_data['userId']
        token_revoked = revoke_token(user_id)
        return {
            'logoutSuccessfull': token_revoked
        }


api.add_resource(HelloWorld, '/')
api.add_resource(RegisterUser, '/api/auth/register-user')
api.add_resource(LoginUser, '/api/auth/login-user')
api.add_resource(LogoutUser, '/api/auth/logout-user')
