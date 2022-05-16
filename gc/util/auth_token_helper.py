import psycopg2
import uuid
from datetime import datetime as dt, timedelta, tzinfo

from pytz import timezone
import pytz

def get_auth_token(user_id: int):
    auth_token_found = False
    token_valid = False
    auth_token = None
    conn = psycopg2.connect(host="localhost", port=5432, database="cs353DB", user="gcagiran")
    cursor = conn.cursor()
    cursor.execute(f'SELECT auth_token, valid_until FROM user_auth_tokens WHERE user_id={user_id}')
    row = cursor.fetchone()
    row_count = cursor.rowcount

    print('user_tokens row count: ', row_count)
    if row is not None:
        print('user_tokens row: ', row)
        auth_token_found = True
        valid_until = row[1]
        if valid_until > dt.now(pytz.timezone('Europe/Istanbul')):
            auth_token = row[0]
            token_valid = True
        
    conn.close()
    return {
        'auth_token_found': auth_token_found,
        'token_valid': token_valid,
        'auth_token': auth_token
    }

def save_new_token(user_id: int):
    print('Saving New Token userId: ', user_id)
    conn = psycopg2.connect(host="localhost", port=5432, database="cs353DB", user="gcagiran")
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM user_auth_tokens WHERE user_id=\'{user_id}\'')
    row_count = cursor.rowcount
    new_uuid = uuid.uuid4()
    valid_until_dt = dt.now() + timedelta(days=2)
    dt_str = f'{str(valid_until_dt.year)}-{str(valid_until_dt.month)}-{str(valid_until_dt.day)} {str(valid_until_dt.hour)}:{str(valid_until_dt.minute)}:{str(valid_until_dt.second)}+03'
    if row_count > 0:
        print('User Token Found userId: ', user_id)
        sql_statement = f'UPDATE user_auth_tokens SET auth_token=\'{str(new_uuid)}\', valid_until=\'{dt_str}\' WHERE user_id={user_id};'
    else:
        print('User Token Not Found userId: ', user_id)
        sql_statement = f'INSERT INTO user_auth_tokens(user_id, auth_token, valid_until) VALUES ({user_id}, \'{str(new_uuid)}\', \'{dt_str}\');'
    
    cursor.execute(sql_statement)
    conn.commit()

    conn.close()

    return {
        'user_id': user_id,
        'auth_token': str(new_uuid),
        'valid_until': valid_until_dt
    }


def revoke_token(user_id: int):
    print('Revoking Auth Token for userId: ', user_id)
    token_revoked = False
    conn = None
    try:
        conn = psycopg2.connect(host="localhost", port=5432, database="cs353DB", user="gcagiran")
        cursor = conn.cursor()
        cursor.execute(f'DELETE FROM user_auth_tokens WHERE user_id=\'{user_id}\'')
        conn.commit()
        token_revoked = True
    except Exception as e:
        print(e)
    if conn:
        conn.close()
    return token_revoked


def check_if_token_valid(auth_token: str):
    print("Checking Auth Token: ", auth_token)
    conn = None
    token_valid = False
    try:
        conn = psycopg2.connect(host="localhost", port=5432, database="cs353DB", user="gcagiran")
        cursor = conn.cursor()
        cursor.execute(f'SELECT valid_until FROM user_auth_tokens WHERE auth_token=\'{auth_token}\';')
        row = cursor.fetchone()
        if row is not None:
            valid_until = row[0]
            if valid_until > dt.now(pytz.timezone('Europe/Istanbul')):
                token_valid = True
    except Exception as e:
        print(e)
    
    if conn:
        conn.close()
    
    return token_valid
