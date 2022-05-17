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
        # Getting all teams in various categories
        if team_id <= 0:
            # Parsing the arguments
            parser = reqparse.RequestParser()
            # Get Type
            parser.add_argument('type', type=str, required=True)
            # Get Id
            parser.add_argument('id', type=str, required=True)
            # Get the arguments
            args = parser.parse_args()
            cursor = 0
            # Queries for different types
            if args['type'] == 'league':
                cursor = connection_instance.execute("SELECT * FROM team INNER JOIN plays_in ON team.team_id = plays_on.team_id WHERE league_id = %s ORDER BY standing ASC", (args['id'],))
            elif args['type'] == 'origin_country':
                cursor = connection_instance.execute("SELECT * FROM team WHERE origin_country = %s", (args['id'],))
            elif args['type'] == 'partakes_in':
                cursor = connection_instance.execute("SELECT * FROM team INNER JOIN partakes_in ON team.team_id = partakes_in.team_id WHERE game_id = %s", (args['id'],))
            elif args['type'] == 'category':
                cursor = connection_instance.execute("SELECT * FROM team WHERE category = %s", (args['id'],))
        else:
            connection_instance.execute("SELECT * FROM team WHERE team_id = %s", (team_id,))
        teams = connection_instance.fetchall()
        if teams:
            # Returning the data in a json format with column names as keys
            team_data = []
            for team in teams:
                team_data.append({})
                for i in range(len(team)):
                    team_data[-1][connection_instance.description[i][0]] = team[i].__str__()
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
        cursor = connection_instance.execute("INSERT INTO team (title, networth, president_name, coach, logo, origin_country, description, category) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (args['title'], args['networth'], args['president_name'], args['coach'], args['logo'], args['origin_country'], args['description'], args['category']))
        # Returning the data
        return {'title': args['title'], 'networth': args['networth'], 'president_name': args['president_name'], 'coach': args['coach'], 'logo': args['logo'], 'origin_country': args['origin_country'], 'description': args['description'], 'category': args['category']}


    # Method called when adding a team to a league
    def put(self, team_id):

        # Parsing the arguments
        parser = reqparse.RequestParser()

        # Putting team into league
        parser.add_argument('league_id', type=int, required=True)
        parser.add_argument('standing', type=int, required=True)
        args = parser.parse_args()
        # Getting the cursor
        cursor = connection_instance.execute("INSERT INTO plays_in (team_id, league_id, standing) VALUES (%s, %s, %s)", (team_id, args['league_id'], args['standing']))
        # Incrementing the number of teams in the league
        cursor = connection_instance.execute("UPDATE league SET team_count = team_count + 1 WHERE league_id = %s", (args['league_id'],))
        # Incrementing the value of the league

        # Getting the updating team
        cursor = connection_instance.execute("SELECT * FROM team WHERE team_id = %s", (team_id.__str__(),))
        team = connection_instance.fetchone()
        
        # Getting the team value of team networth column
        team_value = team[1]

        cursor = connection_instance.execute("UPDATE league SET total_worth = total_worth + %s WHERE league_id = %s", (team_value.__str__(), args['league_id']))
        # Returning the data
        return {'league_id': args['league_id'], 'standing': args['standing']}
        

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
        parser.add_argument('base_type', type=str, required=True)

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
        cursor = connection_instance.execute("INSERT INTO team_base (title, base_type, seating_capacity, description) VALUES (%s, %s, %s, %s)", (args['title'], args['base_type'], args['seating_capacity'], args['description']))
        cursor = connection_instance.execute("INSERT INTO home_base_of (team_id, base_id) VALUES (%s, %s)", (team_id, base_id.__str__()))


class Player(Resource):
    def get(self, player_id):
        
        if player_id > 0:
            connection_instance.execute("SELECT * FROM player WHERE player_id = %s", (player_id,))
            player = connection_instance.fetchone()
            # Parsing the account data to a JSON format with columns as keys
            player_data = {}
            for i in range(len(player)):
                player_data[connection_instance.description[i][0]] = player[i].__str__()
            return player_data
        else:
            parser = reqparse.RequestParser()
            parser.add_argument('team_id', type=int, required=True)
            args = parser.parse_args()
            team_id = args['team_id']

            connection_instance.execute("SELECT * FROM player INNER JOIN member_of ON player.player_id = member_of.player_id WHERE team_id = %s", (team_id,))
            players = connection_instance.fetchall()
            # Parsing the account data to a JSON format with columns as keys
            player_data = []
            for player in players:
                player_data.append({})
                for i in range(len(player)):
                    player_data[-1][connection_instance.description[i][0]] = player[i].__str__()
            return player_data

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
        cursor = connection_instance.execute("INSERT INTO player (age, networth, score, player_name, origin_country, description, injuries_and_penalties) VALUES (%s, %s, %s, %s, %s, %s, %s)", (args['age'], args['networth'], args['score'], args['name'], args['origin_country'], args['description'], args['injuries_and_penalties']))
        cursor = connection_instance.execute("INSERT INTO member_of (team_id, player_id, joined_at) VALUES (%s, %s, %s)", (args['team_id'].__str__(), player_id.__str__(), args['joined_at']))
        cursor = connection_instance.execute("UPDATE team SET networth = networth + %s WHERE team_id = %s", (args['networth'], args['team_id']))