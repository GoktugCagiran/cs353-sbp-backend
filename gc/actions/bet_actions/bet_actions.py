from flask import Flask, jsonify
from flask_restful import reqparse, abort, Api, Resource
import psycopg2
from datetime import datetime
import sys

connection_instance = 0


def connect():
	#Define our connection string
    conn_string = "host='localhost', port=5432, database='testdb3', user='postgres', password='admin'"
    conn = psycopg2.connect(host="localhost", port=5432, database="testdb3", user="postgres", password="admin")
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
        
        # Get the bet
        connection_instance.execute("SELECT * FROM bet WHERE bet_id = %s", (bet_id,))
        bet = connection_instance.fetchone()
        if bet is None:
            abort(404, message="Bet {} doesn't exist".format(bet_id))
        bet_data = {}
        for i in range(len(bet)):
            bet_data[connection_instance.description[i][0]] = bet[i].__str__()
        return bet_data

    def post(self, bet_id):

        # Parsing the arguments
        parser = reqparse.RequestParser()
        # Bet name
        parser.add_argument('bet_name', type=str, required=True)
        # Bet desc
        parser.add_argument('bet_desc', type=str, required=True)
        # Bet type
        parser.add_argument('type', type=str, required=True)
        # Bet odd
        parser.add_argument('odd', type=float, required=True) 
        # Playable until
        parser.add_argument('playable_until', type=str, required=True)
        # Bet option type
        parser.add_argument('bet_option_type', type=str, required=True)
        # Bet adding id
        parser.add_argument('bet_adding_id', type=int, required=True)

        # Get the last bet_id
        connection_instance.execute("SELECT MAX(bet_id) FROM bet")
        new_bet_id = connection_instance.fetchone()[0]
        if new_bet_id is None:
            new_bet_id = 1
        else:
            new_bet_id = new_bet_id + 1


        # Get the arguments
        args = parser.parse_args()
        # Add the bet
        connection_instance.execute("INSERT INTO bet (bet_name, bet_desc, bet_type, odd, playable_until) VALUES (%s, %s, %s, %s, %s)", (args['bet_name'], args['bet_desc'], args['type'], args['odd'], args['playable_until']))

        

        # If bet_option_type is normal, add the option_on
        if args['bet_option_type'] == 'normal':
            connection_instance.execute("INSERT INTO option_on (bet_id, game_id) VALUES (%s, %s)", (new_bet_id, args['bet_adding_id']))
        # If bet_option_type is long_term, add the long_term_option_on
        elif args['bet_option_type'] == 'long_term':
            connection_instance.execute("INSERT INTO long_term_option_on (bet_id, league_id) VALUES (%s, %s)", (new_bet_id, args['bet_adding_id']))
        
class BetSlip(Resource):
    def get(self, bet_slip_id): 
        # Get the bet slip
        connection_instance.execute("SELECT * FROM bet_slip INNER JOIN is_betted_on ON bet_slip.bet_slip_id = is_betted_on.bet_slip_id WHERE bet_slip.bet_slip_id = %s", (bet_slip_id,))
        bet_slip = connection_instance.fetchone()
        if bet_slip is None:
            abort(404, message="Bet slip {} doesn't exist".format(bet_slip_id))
        bet_slip_data = {}
        for i in range(len(bet_slip)):
            bet_slip_data[connection_instance.description[i][0]] = bet_slip[i].__str__()
        return bet_slip_data

    def post(self, bet_slip_id):

        # Parsing the arguments
        parser = reqparse.RequestParser()
        # Finalizes on
        parser.add_argument('finalizes_on', type=str, required=True)
        # Total odd
        parser.add_argument('total_odd', type=float, required=True)
        # MBN
        parser.add_argument('mbn', type=int, required=True)
        # Bet slip state
        parser.add_argument('bet_slip_state', type=str, required=True)
        # Get the arguments
        args = parser.parse_args()
        current_date = datetime.now().__str__()      

        # Add the bet slip
        
        connection_instance.execute("INSERT INTO bet_slip (created_on, finalizes_on, total_odd, mbn, bet_slip_state) VALUES (%s, %s, %s, %s, %s)", (current_date, args['finalizes_on'], args['total_odd'], args['mbn'], args['bet_slip_state']))

    def put(self, bet_slip_id):

        # Parsing the arguments
        parser = reqparse.RequestParser()
        # bet_id
        parser.add_argument('update_key', type=int, required=True)
        parser.add_argument('update_type', type = str, required=True)
        # Get the arguments
        args = parser.parse_args()
        # Add into is_betted_on
        if args['update_type'] == 'is_betted_on':
            connection_instance.execute("INSERT INTO is_betted_on (bet_id, bet_slip_id) VALUES (%s, %s)", (args['update_key'], bet_slip_id))
            
        
        elif args['update_type'] == 'create_bet_slip': 

            # Get the number of bets played on a bet slip
            connection_instance.execute("SELECT COUNT(bet_id) FROM is_betted_on WHERE bet_slip_id = %s", (bet_slip_id,))
            bet_slip_count = connection_instance.fetchone()[0]
            # Get the bet slip
            connection_instance.execute("SELECT mbn FROM bet_slip WHERE bet_slip_id = %s", (bet_slip_id,))
            bet_slip_mbn = connection_instance.fetchone()[0]
            if bet_slip_count < bet_slip_mbn:
                # Return error
                abort(400, message="There should be more bets played in betslip {}".format(bet_slip_id))

            connection_instance.execute("INSERT INTO create_bet_slip (bet_slip_id, user_id) VALUES (%s, %s)", (bet_slip_id, args['update_key']))
            
        # Getting the added bets odd
        connection_instance.execute("SELECT odd FROM bet WHERE bet_id = %s", (args['update_key'],))
        bet_odd = connection_instance.fetchone()[0]
        # Updating the total odd

        connection_instance.execute("UPDATE bet_slip SET total_odd = total_odd * %s WHERE bet_slip_id = %s", (bet_odd, bet_slip_id))
        return "Success"
class MonetizedBetSlip(Resource):
    def get(self, monetized_bet_slip_id):
        # Get the monetized bet slip
        connection_instance.execute("SELECT * FROM monetized_bet_slip WHERE monetized_bet_slip_id = %s", (monetized_bet_slip_id,))
        monetized_bet_slip = connection_instance.fetchone()
        if monetized_bet_slip is None:
            abort(404, message="Monetized bet slip {} doesn't exist".format(monetized_bet_slip_id))
        monetized_bet_slip_data = {}
        for i in range(len(monetized_bet_slip)):
            monetized_bet_slip_data[connection_instance.description[i][0]] = monetized_bet_slip[i].__str__()
        return monetized_bet_slip_data

    def post(self, monetized_bet_slip_id):
        
        # Parsing the arguments
        parser = reqparse.RequestParser()
        # Played timestamp
        parser.add_argument('played_timestamp', type=str, required=True)
        # Gain paid to user
        parser.add_argument('gain_paid_to_user', type=float, required=True)
        # Total gain
        parser.add_argument('total_gain', type=float, required=True)
        # Money amount
        parser.add_argument('money_amount', type=float, required=True)


        # Get the arguments
        args = parser.parse_args()
        # Add the monetized bet slip
        connection_instance.execute("INSERT INTO monetized_bet_slip (played_timestamp, gain_paid_to_user, total_gain, money_amount) VALUES (%s, %s, %s, %s)", (args['played_timestamp'], args['gain_paid_to_user'], args['total_gain'], args['money_amount']))
        
    def put(self, monetized_bet_slip_id): 

        # Parsing the arguments
        parser = reqparse.RequestParser()
        # User id
        parser.add_argument('customer_id', type=int, required=True)
        # Bet slip id
        parser.add_argument('bet_slip_id', type=int, required=True)

        # Get the arguments
        args = parser.parse_args()
        # Add into bet_data relation
        connection_instance.execute("INSERT INTO bet_data (monetized_bet_slip_id, bet_slip_id) VALUES (%s, %s)", (monetized_bet_slip_id.__str__(), args['bet_slip_id']))
        # Add into waged_on relation
        connection_instance.execute("INSERT INTO waged_on (customer_id, monetized_bet_slip_id) VALUES (%s, %s)", (args['customer_id'], monetized_bet_slip_id.__str__()))

        return "Success"