from traceback import print_exc
import mysql.connector, csv
from mysql.connector import Error
from datetime import datetime, timedelta, time, date


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

    except Error as e:
        print_exc(f"ERR: {e}")
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
        print_exc(f"ERR: {e}")
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
        print_exc(f"ERR: {e}")
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
        print_exc(f"ERR: {e}")
        return False

    finally: 
        conn.close()


#* RECORD ADDING AND EXPORTATION

# insert attendance after each scan
def record_attendance(student_id: str, subject_id: str, instructor_id: str, class_start: time, class_end: time) -> None:
    conn = get_connection()
    if not conn:
        return False
    
    try:
        curs = conn.cursor()

        date = datetime.now().date()
        time = datetime.now().time()
        status: str = ""

        if time >= class_end:
            status = "Absent"
        elif time >= class_start:
            status = "Late"
        else:
            status = "On Time"

        # date and time is set to input current date and time upon recording
        sql = """
              INSERT INTO tbl_attendance (subject_id, instructor_id, student_id, class_start, class_end, attendance_status)
              VALUES (%s, %s, %s, %s, %s, %s)
              """

        curs.execute(sql, (subject_id, instructor_id, student_id, class_start, class_end, status,))
        conn.commit()

    except mysql.connector.Error as e:
        print_exc(f"ERR: {e}")
        return False

    finally: 
        conn.close()
        
# TODO: Get list of students and iterate through the absent students



#* QUERIES FOR DATA RETRIEVAL

def get_schedule(subject_id: str, instructor_id: str) -> list:
    conn = get_connection()
    if not conn:
        return []

    try:
        curs = conn.cursor()

        dow_map = {
            1: "monday", 2: "tuesday",  3: "wednesday",
            4: "thursday", 5: "friday", 6: "saturday", 
            7: "sunday"
        }
        today_str = dow_map[datetime.now().isoweekday()]

        # schedule has class_id FK; subject/instructor live on the class table
        curs.execute("""
            SELECT s.sched_start, s.sched_end
            FROM schedule s
            INNER JOIN class c ON c.class_id = s.class_id
            WHERE c.subject_id    = %s
              AND c.instructor_id = %s
              AND s.day_of_week   = %s
            ORDER BY s.sched_start ASC
            """,
            (subject_id, instructor_id, today_str)
        )
        rows = curs.fetchall()

        slots = []
        for raw_start, raw_end in rows:
            start = _td_to_time(raw_start)
            end   = _td_to_time(raw_end)
            label = f"{start.strftime('%I:%M %p')} – {end.strftime('%I:%M %p')}"
            slots.append({"start": start, "end": end, "label": label})

        return slots

    except Error as e:
        print(f"ERR [get_schedule]: {e}")
        return []

    finally:
        conn.close()





#* RETRIEVAL OF DATA FOR APPLICATION GUI

# fetch ALL ENTRIES for attendance log
def get_attendance_log():
    conn = get_connection()
    if not conn:
        return False
    
    try:
        curs = conn.cursor()

        sql = """
            SELECT   a.date, a.time, st.student_name, e.course, e.year_level, e.section, a.attendance_status
            FROM tbl_attendance a
            INNER JOIN tbl_student st ON a.student_id = st.student_id
            INNER JOIN tbl_enrollment e ON e.student_id = st.student_id
            WHERE a.attendance_status NOT IN ('Absent')
            ORDER BY date ASC, time ASC
        """
        
        curs.execute(sql)
        logs = curs.fetchall()
        
        # Store data into dictionary
        cols = [column[0] for column in curs.description]
        rows = [dict(zip(cols, row)) for row in logs]

        return cols, rows

    except mysql.connector.Error as e:
        print_exc(f"ERR: {e}")
        return False

    finally: 
        conn.close()

# TODO: Change 'instructor' to 'section'
# fetch ALL ENTRIES for class list
def get_class_list():
    conn = get_connection()
    if not conn:
        return False
    
    try:
        curs = conn.cursor()

        sql = """
            SELECT DISTINCT a.date, a.class_start, a.subject_id, i.instructor_name
            FROM tbl_attendance a, tbl_subjects_enrolled se
            JOIN tbl_instructor i ON i.instructor_id = se.instructor_id
            ORDER BY date ASC, class_start ASC
        """
        
        curs.execute(sql)
        logs = curs.fetchall()
        
        # Store data into dictionary
        cols = [column[0] for column in curs.description]
        rows = [dict(zip(cols, row)) for row in logs]

        return cols, rows

    except mysql.connector.Error as e:
        print_exc(f"ERR: {e}")
        return False

    finally: 
        conn.close()
        
# fetch records for a specific attendance sheet
# TODO: Fetch attendance sheet ordered alphabetically