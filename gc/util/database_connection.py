import psycopg2
from .constants import CONNECTION_STRING

def get_db_cursor():
    conn = psycopg2.connect(host="localhost", port="5432", )