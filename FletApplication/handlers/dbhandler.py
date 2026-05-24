import mysql.connector
from datetime import timedelta
from datetime import date
from datetime import time
from datetime import datetime

# FUNCTION TEMPLATE -- Use this, please
'''
def func_name(func_args):
    conn = get_connection()
    if not conn:
        return False
    
    try:
        curs = conn.cursor()

        curs.execute("""

            """,
            (func_args)
        )
        value = curs.fetchall()

        if not value:
            return None
        
        return value

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return False

    finally: 
        conn.close()
'''

def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="Admin-110",
            password="attendance",
            database="db_SASs",
        )

        if conn.is_connected():
            return conn

    except mysql.connector.Error as e:
        print("ERROR:", e)
        return None



#* QUERIES FOR RECORD EXISTENCE VALIDATION

# for instructors login
def query_login_credentials(instructor_id: str, password: str):
    conn = get_connection()
    if not conn:
        return False

    try:
        curs = conn.cursor()

        # validate instructor existence
        curs.execute("""
            SELECT instructor_name
            FROM instructor
            WHERE instructor_id = %s
                AND password = MD5(%s)
            LIMIT 1
            """,
                     (instructor_id, password,)
                     )
        username = curs.fetchone()

        if not username:
            return False

        username = username[0]
        return {"id": instructor_id, "name": username}

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return False

    finally:
        conn.close()
        

