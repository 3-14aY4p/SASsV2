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

# Retrieve USER LOGIN credentials
def query_instructor_id(instructor_id: str, password: str):
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

        return {"id": instructor_id, "name": username}

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return False

    finally: 
        conn.close()

# validate existence of student_id
def query_student_id(student_id: str):
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
            (student_id,)
        )
        row = curs.fetchone()

        if not row:
            return False

        first, middle, last = row
        full_name = " ".join(filter(None, [first, middle, last]))
        
        return full_name

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return False

    finally: 
        conn.close()

# validates if student is enrolled in a subject
def query_subject_enrollment(student_id: str, subject_id: str, instructor_id: str):
    conn = get_connection()
    if not conn:
        return False
    
    try:
        curs = conn.cursor()
        curs.execute("""
            SELECT 1
            FROM enrollment e
            INNER JOIN subject_enrollment se ON se.enrollment_id = e.enrollment_id
            WHERE e.student_id = %s
                AND se.subject_id = %s
                AND se.instructor_id = %s
            LIMIT 1
            """,
            (student_id, subject_id, instructor_id,)
        )
        return curs.fetchone() is not None

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return False

    finally: 
        conn.close()

# validates if student has has already recorded PRESENT or LATE for the session
def query_attendance(student_id: str, subject_id: str, instructor_id: str, session_date: date, session_start: time):
    conn = get_connection()
    if not conn:
        return False
    
    try:
        curs = conn.cursor()

        curs.execute("""
            SELECT 1
            FROM attendance a
            INNER JOIN class c ON a.class_id = c.class_id
            INNER JOIN student s ON a.student_id = s.student_id
            WHERE a.student_id = %s
                AND c.subject_id = %s
                AND c.instructor_id = %s
                AND date = %s
                AND session_start = %s
                AND status IN ('on time', 'late')
            LIMIT 1
            """,
            (student_id, subject_id, instructor_id, session_date, session_start,)
        )
        return curs.fetchone() is not None

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return False

    finally: 
        conn.close()



#* QUERIES FOR DATA RETRIEVALS

# Retrieve sections under the instructor
def get_instructor_sections(instructor_id: str):
    conn = get_connection()
    if not conn:
        return False
    
    try:
        curs = conn.cursor()

        curs.execute("""
            SELECT b.course_id, b.year_level, b.section 
            FROM block b
            INNER JOIN class c ON c.block_id = b.block_id
            INNER JOIN instructor i ON c.instructor_id = i.instructor_id
            WHERE c.instructor_id = %s
            """,
            (instructor_id,)
        )
        row = curs.fetchall()
        
        if not row:
            return False
        
        blocks = []
        for course, year, section in row:
            block = {
                "course": course,
                "year": year,
                "section": section
            }
            blocks.append(block)

        return blocks

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return False

    finally: 
        conn.close()

# Retrieve instructor's subjects
def get_instructor_subjects(instructor_id: str):
    conn = get_connection()
    if not conn:
        return False
    
    try:
        curs = conn.cursor()

        curs.execute("""
            SELECT UNIQUE se.subject_id
            FROM subject_enrollment se
            INNER JOIN enrollment e ON se.enrollment_id = e.enrollment_id
            INNER JOIN instructor i ON se.instructor_id = i.instructor_id
            WHERE se.instructor_id = %s
            """,
            (instructor_id,)
        )
        row = curs.fetchall()
        
        if not row:
            return False
        
        subjects = []
        for subject in row:
            subjects.append(subject)
        
        return subjects

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return False

    finally: 
        conn.close()

# Convert timedelta to time
def _td_to_time(td) -> time:
    if isinstance(td, timedelta):
        total = int(td.total_seconds())
        return time(total // 3600, (total % 3600) // 60, total % 60)
    return td

# TODO: Retrieve instructor schedule on subject for a specific section for the day
def get_instructor_schedules(instructor_id: str, subject_id: str, section: dict):
    dow_map = {
        1: "monday", 2: "tuesday",  3: "wednesday",
        4: "thursday", 5: "friday", 6: "saturday", 
        7: "sunday"
    }
    today_str = dow_map[datetime.now().isoweekday()]
    
    conn = get_connection()
    if not conn:
        return False
    
    try:
        curs = conn.cursor()

        curs.execute("""
                SELECT sc.sched_start, sc.sched_end
                FROM schedule sc
                INNER JOIN class c ON sc.class_id = c.class_id
                INNER JOIN block b ON c.block_id = b.block_id
                WHERE c.instructor_id = %s
                    AND c.subject_id = %s 
                    AND b.course_id = %s 
                    AND b.year_level = %s 
                    AND b.section = %s 
                    AND sc.day_of_week = %s
            """,
            (instructor_id, subject_id, section['course'], section['year'], section['section'], 'wednesday') # FIXME: change to today_str after testing
        )
        rows = curs.fetchall()

        if not rows:
            return False

        slots = []
        for raw_start, raw_end in rows:
            start = _td_to_time(raw_start)
            end   = _td_to_time(raw_end)
            label = f"{start.strftime('%I:%M %p')} – {end.strftime('%I:%M %p')}"
            slots.append({"start": start, "end": end, "label": label})

        return slots

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return False

    finally: 
        conn.close()



# TODO: Retrieve all schedules of the Instructor
# TODO: Populate Attendance datatables
# TODO: Populate Class datatables
# TODO: Retrieve specific class/session attendance