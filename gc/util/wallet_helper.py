import psycopg2
import uuid
from datetime import datetime as dt, timedelta
import pytz

def check_user_balance(user_id: int, required_amount: float):
    conn = psycopg2.connect(host="localhost", port=5432, database="testdb3", user="postgres", password="admin")
    cursor = conn.cursor()

    cursor.execute(f'SELECT balance FROM customer WHERE user_id=\'{user_id}\';')
    balance = cursor.fetchone()
    conn.close()
    if balance[0] > required_amount:
        return True
    else:
        return False


def add_to_user_balance(user_id: int, add_amount: float):
    conn = psycopg2.connect(host="localhost", port=5432, database="testdb3", user="postgres", password="admin")
    cursor = conn.cursor()

    cursor.execute(f'SELECT balance FROM customer WHERE user_id=\'{user_id}\';')
    balance = cursor.fetchone()
    
    new_balance = balance[0] + add_amount

    cursor.execute(f'UPDATE customer SET balance={new_balance} WHERE user_id=\'{user_id}\';')

    conn.commit()

    conn.close()
    return True


def reduce_user_balance(user_id: int, reduce_amount: float):
    conn = psycopg2.connect(host="localhost", port=5432, database="testdb3", user="postgres", password="admin")
    cursor = conn.cursor()

    cursor.execute(f'SELECT balance FROM customer WHERE user_id=\'{user_id}\';')
    balance = cursor.fetchone()
    
    new_balance = balance[0] - reduce_amount

    cursor.execute(f'UPDATE customer SET balance={new_balance} WHERE user_id=\'{user_id}\';')

    conn.commit()

    conn.close()

    return True
