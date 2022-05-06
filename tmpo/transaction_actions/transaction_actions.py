from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
import psycopg2
import sys

app = Flask(__name__)
api = Api(app)
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

class Transaction(Resource):

    def get(self, user_id):
        connection_instance.execute("SELECT * FROM transaction INNER JOIN made_by ON transaction.transaction_id = made_by.transaction_id WHERE user_id = %s", (user_id,))
        transaction = connection_instance.fetchall()
        if transaction:
            return transaction
        else:
            abort(404, message="Transaction {} doesn't exist".format(transaction_id))

    def post(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument('transaction_id', type=int)
        parser.add_argument('amount', type=float)
        parser.add_argument('transaction_type', type=str)
        parser.add_argument('date', type=str)
        args = parser.parse_args()
        connection_instance.execute("INSERT INTO transaction (transaction_id, amount, transaction_type, date) VALUES (%s, %s, %s, %s)", (args['transaction_id'], args['amount'], args['transaction_type'], args['date']))
        connection_instance.execute("INSERT INTO made_by (transaction_id, user_id) VALUES (%s, %s)", (args['transaction_id'], user_id))
        return args

    
    