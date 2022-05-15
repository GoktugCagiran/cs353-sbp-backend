from re import A
from socket import gaierror
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

class Game(Resource):
    def get(self, game_id):
        # Parse the arguments

        if(game_id == 0):
            connection_instance.execute("SELECT * FROM games")
            games = connection_instance.fetchall()
            # Returning the data in a json format with column names as keys
            games_data = []
            for game in games:
                games_data.append({})
                for i in range(len(game)):
                    games_data[-1][connection_instance.description[i][0]] = game[i].__str__()
            return games_data
        else:
        # Get the game
            connection_instance.execute("SELECT * FROM games WHERE id = %s", (game_id,))
            game = connection_instance.fetchone()
            if game is None:
                abort(404, message="Game {} doesn't exist".format(game_id))
            game_data = {}
            for i in range(len(game)):
                game_data[connection_instance.description[i][0]] = game[i].__str__()
            return game_data

    def post(self, team_id): 

        # Parsing the arguments
        parser = reqparse.RequestParser()
        # Played in country
        parser.add_argument('played_in_country', type=str, required=True)
        # Played in base
        parser.add_argument('played_in_base', type=str, required=True)
        # Game date
        parser.add_argument('game_date', type=str, required=True)
        # Duration
        parser.add_argument('duration', type=str, required=True)
        # Teams that will play in the game
        parser.add_argument('teams', type=str, required=True)
        # Type
        parser.add_argument('type', type=str, required=True)


        # Get the arguments
        args = parser.parse_args()

        # Last id
        connection_instance.execute("SELECT MAX(id) FROM games")
        id = connection_instance.fetchone()[0]
        if id is None:
            id = 1
        else:
            id += 1
        
        # Insert the game
        connection_instance.execute("INSERT INTO games (id, played_in_country, played_in_base, game_date, duration) VALUES (%s, %s, %s, %s, %s)", (id, args['played_in_country'], args['played_in_base'], args['game_date'], args['duration']))

        # Parsing the teams
        teams = args['teams'].split(',')
        for team in teams:
            connection_instance.execute("INSERT INTO partakes_in (team_id, game_id, type) VALUES (%s, %s, %s)", (team, id, args['type']))
        
        return args, 200
        
    def put(self, game_id):

        # Parsing the arguments
        parser = reqparse.RequestParser()
        # User id
        parser.add_argument('user_id', type=int, required=True)
        
        # Get the arguments
        args = parser.parse_args()
        # Insert into favourites relation
        connection_instance.execute("INSERT INTO favourites (user_id, game_id) VALUES (%s, %s)", (args['user_id'], game_id))

class League(Resource):
    def get(self, league_id):
        connection_instance.execute("SELECT * FROM league WHERE league_id = %s", (league_id,))
        league = connection_instance.fetchone()
        if league:
            league_data = {}
            for i in range(len(league)):
                league_data[connection_instance.description[i][0]] = league[i].__str__()
            return league_data
    def post(self, league_id):
        # Parsing the arguments
        parser = reqparse.RequestParser()
        # Country
        parser.add_argument('country', type=str, required=True)
        # Total Worth
        parser.add_argument('total_worth', type=int, required=True)
        # Team Count
        parser.add_argument('team_count', type=int, required=True) 
        # Country Rank
        parser.add_argument('country_rank', type=int, required=True)
        # Title
        parser.add_argument('title', type=str, required=True)

        # Get the arguments
        args = parser.parse_args()
        # Insert the data into the database
        connection_instance.execute("INSERT INTO league (country, total_worth, team_count, country_rank, title) VALUES (%s, %s, %s, %s, %s)", (args['country'], args['total_worth'], args['team_count'], args['country_rank'], args['title']))
    


