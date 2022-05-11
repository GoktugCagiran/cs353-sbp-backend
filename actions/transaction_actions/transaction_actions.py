from flask import Flask, jsonify
from flask_restful import reqparse, abort, Api, Resource
import psycopg2
import sys

connection_instance = 0


def connect():
	#Define our connection string
	conn_string = "host='localhost' dbname='testdb3' user='postgres' password='admin'"
	conn = psycopg2.connect(conn_string)
	conn.autocommit = True
	return conn.cursor()

# Connect to the database
if connection_instance == 0:
    connection_instance = connect()
    if connection_instance == 0:
        print("Connection failed")
        abort(500)
    print("Connected!")

class DepositingTransaction(Resource):

    def get(self, account_id):
        connection_instance.execute("SELECT * FROM transaction INNER JOIN made_by ON transaction.transaction_id = made_by.transaction_id WHERE user_id = {} AND transaction_type LIKE 'DP%'".format(account_id.__str__(),))
        transaction = connection_instance.fetchall()
        if transaction:
            if len(transaction) == 0:
                return "No transactions"
            
            # Parsing the transaction data to a JSON format with columns as keys
            transaction_data = []
            for i in range(len(transaction)):
                transaction_data.append({})
                for j in range(len(transaction[i])):
                    transaction_data[i][connection_instance.description[j][0]] = transaction[i][j].__str__()
            return transaction_data
        else:
            abort(404, message="User {} does not have any depositing transactions".format(account_id))

    def post(self, account_id):
        parser = reqparse.RequestParser()
        parser.add_argument('amount', type=float)
        parser.add_argument('transaction_type', type=str)
        parser.add_argument('date', type=str)
        args = parser.parse_args()
        # Getting the current transaction id from the database
        connection_instance.execute("SELECT MAX(transaction_id) FROM transaction")
        transaction_id = connection_instance.fetchone()[0]
        if transaction_id is None:
            transaction_id = 1
        else:
            transaction_id += 1
        connection_instance.execute("INSERT INTO transaction (transaction_id, amount, transaction_type, date) VALUES (%s, %s, %s, %s)", (transaction_id, args['amount'], args['transaction_type'], args['date']))
        connection_instance.execute("INSERT INTO made_by (transaction_id, user_id) VALUES (%s, %s)", (transaction_id, account_id))
        connection_instance.execute("UPDATE customer SET balance = balance + %s WHERE user_id = %s", (args['amount'], account_id))
        return args


class WithdrawingTransaction(Resource):
    
    def get(self, account_id):
       
        connection_instance.execute("SELECT * FROM transaction INNER JOIN made_by ON transaction.transaction_id = made_by.transaction_id WHERE user_id = {} AND transaction_type LIKE 'WD%'".format(account_id.__str__(),))
        transaction = connection_instance.fetchall()
        if transaction:
            if len(transaction) == 0:
                return "No transactions"
            
            # Parsing the account data to a JSON format with columns as keys
            transaction_data = []
            for i in range(len(transaction)):
                transaction_data.append({})
                for j in range(len(transaction[i])):
                    transaction_data[i][connection_instance.description[j][0]] = transaction[i][j].__str__()
            return transaction_data
        else:
            abort(404, message="User {} does not have any depositing transactions".format(account_id))

    def post(self, account_id):
        parser = reqparse.RequestParser()
        parser.add_argument('amount', type=float)
        parser.add_argument('transaction_type', type=str)
        parser.add_argument('date', type=str)
        args = parser.parse_args()

        # Getting user balance from the database
        connection_instance.execute("SELECT * FROM customer WHERE user_id = {} ".format(account_id.__str__(),))
        customer = connection_instance.fetchone()
        print(customer.__str__())
        balance = int(customer[9])
        if balance < args['amount']:
            abort(400, message="User {} does not have enough balance".format(account_id))        

        # Getting the current transaction id from the database
        connection_instance.execute("SELECT MAX(transaction_id) FROM transaction")
        transaction_id = connection_instance.fetchone()[0]
        if transaction_id is None:
            transaction_id = 1
        else:
            transaction_id += 1
        connection_instance.execute("INSERT INTO transaction (transaction_id, amount, transaction_type, date) VALUES (%s, %s, %s, %s)", (transaction_id, args['amount'], args['transaction_type'], args['date']))
        connection_instance.execute("INSERT INTO made_by (transaction_id, user_id) VALUES (%s, %s)", (transaction_id, account_id))
        connection_instance.execute("UPDATE customer SET balance = balance - {} WHERE user_id = {}".format(args['amount'], account_id))
        return args
