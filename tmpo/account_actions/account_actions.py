from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
import psycopg2
import sys

connection_instance = 0

def connect():
	#Define our connection string
	conn_string = "host='localhost' dbname='testdb3' user='postgres' password='admin'"
	conn = psycopg2.connect(conn_string)
	connection_instance = conn.cursor()

# Connect to the database
if connection_instance == 0:
    connect()
    if connection_instance == 0:
        print("Connection failed")
        abort(500)
    print("Connected!")

class Account(Resource):
    def get(self, account_id):
        connection_instance.execute("SELECT * FROM accounts WHERE id = %s", (account_id,))
        account = connection_instance.fetchone()
        if account:
            return account
        else:
            abort(404, message="Account {} doesn't exist".format(account_id))
    def update(self, account_id):
        parser = reqparse.RequestParser()
        parser.add_argument('updating_value', type=str)
        parser.add_argument('update_of', type=int)
        args = parser.parse_args()
        # IBAN number update option
        if args['update_of'] == 1:
            connection_instance.execute("UPDATE customer SET iban_number = %s WHERE id = %s", (args['updating_value'], account_id))
        # Password update option
        elif args['update_of'] == 2:
            connection_instance.execute("UPDATE customer SET password = %s WHERE user_id = %s", (args['updating_value'], account_id))
        else:
            abort(400, message="Please provide a valid update code")
        return args

    
class CreditCard(Resource):
    # Returning the instances of all credit cards
    def get(self, card_number):
        connection_instance.execute("SELECT * FROM credit_card WHERE card_number = %s", (card_number,))
        credit_card = connection_instance.fetchall()
        if credit_card:
            return credit_card
        else:
            abort(404, message="Credit Card {} doesn't exist".format(card_number))
    # Deleting the specified credit card
    def delete(self, card_number):     
        connection_instance.execute("DELETE FROM belongs_to WHERE user_id = %s and card_number = %s", (account_id, args['card_number']))
        connection_instance.execute("DELETE FROM credit_card WHERE card_number = %s", (args['card_number']))
        return card_number
    # Adding a new credit card
    def post(self, card_number):
        parser = reqparse.RequestParser()
        parser.add_argument('security_code', type=str)
        parser.add_argument('exp_date', type=str)
        parser.add_argument('creation_date', type=str)
        parser.add_argument('billing_address', type=str)
        parser.add_argument('account_id', type=int)
        args = parser.parse_args()
        connection_instance.execute("INSERT INTO credit_card (card_number, security_code, exp_date, creation_date, billing_address) VALUES (%s, %s, %s, %s, %s)", (args['card_number'], args['security_code'], args['exp_date'], args['creation_date'], args['billing_address']))
        connection_instance.execute("INSERT INTO belongs_to (user_id, card_number) VALUES (%s, %s)", (args['account_id'], args['card_number']))


