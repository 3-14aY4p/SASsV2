import mysql.connector
from datetime import datetime, timedelta, time, date


# FUNCTION TEMPLATE
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
            return False
        
        return value

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return False

    finally: 
        conn.close()
'''


# connect to database
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
        print(f"ERR: {e}")
        return None


#* QUERIES FOR VALIDATING EXISTENCE OF RECORDS

# validate existence of student_id
def query_student_id(student_id: str) -> dict:
    conn = get_connection()
    if not conn:
        return False
    
    try:
        curs = conn.cursor()

        # validate student existence
        curs.execute("""
            SELECT first_name, middle_name, last_name
            FROM student
            WHERE student_id = %s
            """,
            (student_id)
        )
        row = curs.fetchone()

        if not row:
            return {"status": False}

        first, middle, last = row
        full_name = " ".join(filter(None, [first, middle, last]))
        
        return {"status": True, "name": full_name}

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return False

    finally: 
        conn.close()

# validates if student is enrolled in a subject
def query_subject_enrollment(student_id: str, subject_id: str, instructor_id: str) -> bool:
    conn = get_connection()
    if not conn:
        return False
    
    try:
        curs = conn.cursor()
        curs.execute("""
            SELECT 1
            FROM enrollment e
            INNER JOIN subject_enrollment se ON se.enrollment_id = e.enrollment_id
            WHERE e.student_id   = %s
              AND se.subject_id  = %s
              AND se.instructor_id = %s
            LIMIT 1
            """,
            (student_id, subject_id, instructor_id)
        )
        return curs.fetchone() is not None

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return False

    finally: 
        conn.close()

# validates if student has has already recorded PRESENT or LATE for the session
def query_attendance(student_id: str, subject_id: str, session_date: date, session_start: time) -> bool:
    conn = get_connection()
    if not conn:
        return False
    
    try:
        curs = conn.cursor()

        curs.execute("""
            SELECT 1
            FROM attendance
            WHERE student_id   = %s
              AND subject_id   = %s
              AND date         = %s
              AND session_start = %s
              AND status IN ('on time', 'late')
            LIMIT 1
            """,
            (student_id, subject_id, session_date, session_start)
        )
        return curs.fetchone() is not None

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return False

    finally: 
        conn.close()