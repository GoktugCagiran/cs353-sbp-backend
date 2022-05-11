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

class Team(Resource):
    def get(self, team_id):
        connection_instance.execute("SELECT * FROM team WHERE team_id = %s", (team_id,))
        team = connection_instance.fetchone()
        if team:
            # Parsing the account data to a JSON format with columns as keys
            team_data = {}
            for i in range(len(team)):
                team_data[connection_instance.description[i][0]] = team[i].__str__()
            return team_data


    def post(self, team_id):
        # Parsing the arguments
        parser = reqparse.RequestParser()

        # Team Title
        parser.add_argument('title', type=str, required=True)

        # Networth
        parser.add_argument('networth', type=int, required=True)

        # President Name
        parser.add_argument('president_name', type=str, required=True)

        # Coach
        parser.add_argument('coach', type=str, required=True)

        # Logo
        parser.add_argument('logo', type=str, required=True)

        # Origin Country
        parser.add_argument('origin_country', type=str, required=True)

        # Description
        parser.add_argument('description', type=str, required=True)

        # Category
        parser.add_argument('category', type=str, required=True)

        # Changing to args
        args = parser.parse_args()

        # Getting the cursor
        cursor = connection_instance.execute("INSERT INTO teams (title, networth, president_name, coach, logo, origin_country, description, category) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (args['title'], args['networth'], args['president_name'], args['coach'], args['logo'], args['origin_country'], args['description'], args['category']))



class TeamBase(Resource):
    def get(self, team_id):
        connection_instance.execute("SELECT * FROM team_base INNER JOIN home_base_of ON home_base_of.base_id = team_base.base_id WHERE team_id = {}".format(team_id.__str__(),))
        team_base = connection_instance.fetchone()       
       
        if team_base:
            # Parsing the team data to a JSON format with columns as keys
            team_base_data = {}
            for i in range(len(team_base)):
                team_base_data[connection_instance.description[i]
                             [0]] = team_base[i].__str__()
            return team_base_data

        else:
            abort(404, message="Team {} does not have base or doesn't exist".format(team_id))
         


    def post(self, team_id):
        # Parsing the arguments
        parser = reqparse.RequestParser()

        # Title
        parser.add_argument('title', type=str, required=True)

        # Type
        parser.add_argument('type', type=str, required=True)

        # Seating Capacity
        parser.add_argument('seating_capacity', type=int, required=True)
        
        # Description
        parser.add_argument('description', type=str, required=True)


        # Changing to args
        args = parser.parse_args()

        # Last inserted id
        connection_instance.execute("SELECT MAX(base_id) FROM team_base")
        base_id = connection_instance.fetchone()[0]
        if base_id is None:
            base_id = 1
        else:
            base_id += 1

        # Getting the cursor
        cursor = connection_instance.execute("INSERT INTO team_bases (title, type, seating_capacity, description) VALUES (%s, %s, %s, %s)", (args['title'], args['type'], args['seating_capacity'], args['description']))
        cursor = connection_instance.execute("INSERT INTO home_base_of (team_id, base_id) VALUES (%s, %s)", (team_id, base_id.__str__()))


class Player(Resource):
    def get(self, player_id):
        abort

    def post(self, player_id):
        # Parsing the arguments
        parser = reqparse.RequestParser()

        # Age
        parser.add_argument('age', type=int, required=True)

        # Networth
        parser.add_argument('networth', type=int, required=True)

        # Score
        parser.add_argument('score', type=int, required=True)

        # Name
        parser.add_argument('name', type=str, required=True)

        # Logo
        parser.add_argument('logo', type=str, required=True)

        # Origin Country
        parser.add_argument('origin_country', type=str, required=True)

        # Description
        parser.add_argument('description', type=str, required=True)

        # Injuries And Penalties
        parser.add_argument('injuries_and_penalties', type=str, required=True)

        # Team Id
        parser.add_argument('team_id', type=int, required=True)

        # Joined At
        parser.add_argument('joined_at', type=str, required=True)

        # Changing to args
        args = parser.parse_args()

        # Last inserted id
        connection_instance.execute("SELECT MAX(player_id) FROM player")
        player_id = connection_instance.fetchone()[0]
        if player_id is None:
            player_id = 1
        else:
            player_id += 1

        # Getting the cursor
        cursor = connection_instance.execute("INSERT INTO players (age, networth, score, name, logo, origin_country, description, injuries_and_penalties) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (args['age'], args['networth'], args['score'], args['name'], args['logo'], args['origin_country'], args['description'], args['injuries_and_penalties']))
        cursor = connection_instance.execute("INSERT INTO player_of (team_id, player_id, joined_at) VALUES (%s, %s, %s)", (args['team_id'], player_id.__str__(), args['joined_at']))