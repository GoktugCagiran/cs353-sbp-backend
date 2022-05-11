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


class Bet(Resource):
    def get(self, bet_id):
        abort

class BetSlip(Resource):
    def get(self, bet_slip_id):
        abort

class MonetizedBetSlip(Resource):
    def get(self, monetized_bet_slip_id):
        abort
