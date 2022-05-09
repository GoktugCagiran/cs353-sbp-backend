import imp
import json
from re import A
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
import datetime
import psycopg2
import sys

connection_instance = 0
conn = 0

def defaultconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


def connect():
    #Define our connection string
    conn_string = "host='localhost' dbname='testdb3' user='postgres' password='admin'"
    conn = psycopg2.connect(conn_string)
    conn.autocommit = True
    tmp = conn.cursor()
    return tmp


# Connect to the database
if connection_instance == 0:
    connection_instance = connect()

    if connection_instance == 0:
        print("Connection failed")
        abort(500)
    print("Connected!")


class Account(Resource):
    def get(self, account_id):
        connection_instance.execute(
            "SELECT * FROM customer WHERE user_id = %s", (account_id,))
        account = connection_instance.fetchone()

        if account:

            # Parsing the account data to a JSON format with columns as keys
            account_data = {}
            for i in range(len(account)):
                account_data[connection_instance.description[i]
                             [0]] = account[i].__str__()
            return account_data

        else:
            abort(404, message="Account {} doesn't exist".format(account_id))

    def post(self, account_id):
        parser = reqparse.RequestParser()
        parser.add_argument('updating_value', type=str)
        parser.add_argument('update_of', type=int)
        args = parser.parse_args()
        # IBAN number update option
        if args['update_of'] == 1:
            connection_instance.execute(
                "UPDATE customer SET iban_number = %s WHERE user_id = %s", (args['updating_value'], account_id))
        # Password update option
        elif args['update_of'] == 2:
            connection_instance.execute(
                "UPDATE customer SET password = %s WHERE user_id = %s", (args['updating_value'], account_id))
        else:
            abort(400, message="Please provide a valid update code")
        return "Account {} updated".format(account_id)


class CreditCard(Resource):
    # Returning the instances of all credit cards
    def get(self, account_id):
        connection_instance.execute(
            "SELECT * FROM credit_card INNER JOIN belongs_to ON credit_card.card_number = belongs_to.card_number WHERE user_id = %s", (account_id,))
        credit_card = connection_instance.fetchall()
        if credit_card:
            # Parsing the credit card data to a JSON format with columns as keys
            credit_card_data = []
            for i in range(len(credit_card)):
                credit_card_data.append({})
                for j in range(len(credit_card[i])):
                    credit_card_data[i][connection_instance.description[j][0]] = credit_card[i][j].__str__()
            return credit_card_data
        else:
            abort(404, message="User {} does not have any cards".format(account_id))
    # Deleting the specified credit card

    def delete(self, account_id):

        parser = reqparse.RequestParser()
        parser.add_argument('card_number', type=str)
        args = parser.parse_args()
        connection_instance.execute(
            "DELETE FROM belongs_to WHERE user_id = %s and card_number = %s", (account_id.__str__(), args['card_number']))
        connection_instance.execute(
            "DELETE FROM credit_card WHERE card_number = \'{}\'".format(args['card_number'].__str__()))
        return account_id
        
    # Adding a new credit card

    def post(self, account_id):
        parser = reqparse.RequestParser()
        parser.add_argument('security_code', type=int)
        parser.add_argument('exp_date', type=str)
        parser.add_argument('billing_address', type=str)
        parser.add_argument('card_number', type=str)
        args = parser.parse_args()

        # Checking if the credit card already exists
        connection_instance.execute(
            "SELECT * FROM credit_card WHERE card_number = %s", (args['card_number'],))
        credit_card = connection_instance.fetchone()
        if credit_card:
            abort(400, message="Credit Card {} already exists".format(
                args['card_number']))
        # Adding the credit card in a try block to avoid errors
        connection_instance.execute("INSERT INTO credit_card (card_number, security_code, exp_date, creation_date, billing_address) VALUES (%s, %s, %s, %s, %s)", (
            args['card_number'], args['security_code'], args['exp_date'], datetime.date.today().__format__('%Y-%d-%m'), args['billing_address']))
        connection_instance.execute(
            "INSERT INTO belongs_to (user_id, card_number) VALUES (%s, %s)", (account_id, args['card_number']))

        return "Credit Card {} added".format(args['card_number'])
