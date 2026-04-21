import mysql.connector, csv
from mysql.connector import Error
from datetime import datetime, timedelta, time, date


# connect to database
def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="Admin-110",
            database="db_SmartAttendance",
            password="attendance",
        )
        if conn.is_connected():
            return conn

    except Error as e:
        print(f"ERR: {e}")
        return None


conn = get_connection()
curs = conn.cursor()

# close connection to the database
def close_connection():
    if 'conn' in locals() and conn.is_connected():
            conn.close()
            curs.close()



# validate existence of student_id
def query_student_id(student_id: str) -> dict:
    try:
        conn = get_connection()
        curs = conn.cursor()

        # validate student existence
        curs.execute("SELECT student_name FROM tbl_student WHERE student_id = %s", (student_id,))
        student = curs.fetchone()

        if not student:
            return {"status": False}
        else:
            return {"status": True, "name": student[0]}

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return {"success": False}

# validates if student is enrolled in a subject
def query_subject_enrollment(student_id: str, subject_id: str, instructor_id: str) -> bool:
    try:
        conn = get_connection()
        curs = conn.cursor()

        curs.execute("""
            SELECT s.student_name FROM tbl_enrollment e
            INNER JOIN tbl_student s ON e.student_id = s.student_id
            INNER JOIN tbl_subjects_enrolled se ON se.enrollment_id = e.enrollment_id
            WHERE se.subject_id = %s 
                AND se.instructor_id = %s
                AND e.student_id = %s
        """, (subject_id, instructor_id, student_id,))
        student = curs.fetchone()

        if not student:
            return False
        else:
            return True

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return False

# validates if student has has already recorded PRESENT or LATE for the session
def query_attendance(student_id: str, subject_id: str, date, class_start) -> bool:
    try:
        conn = get_connection()
        curs = conn.cursor()

        curs.execute("""
               SELECT a.attendance_id FROM tbl_attendance a
               INNER JOIN tbl_enrollment e ON a.student_id = e.student_id
               INNER JOIN tbl_subjects_enrolled se ON a.subject_id = se.subject_id
               WHERE a.student_id = %s
                    AND a.subject_id = %s
                    AND a.date = %s
                    AND a.class_start = %s
               """, (student_id,  subject_id, date, class_start))

        if curs.fetchone():
            return True

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return False

# insert attendance after each scan
def record_attendance(student_id: str, subject_id: str, instructor_id: str, class_start: time, class_end: time) -> None:
    try:
        conn = get_connection()
        curs = conn.cursor()

        date = datetime.now().date()
        time = datetime.now().time()
        status: str = ""

        if time >= class_end:
            status = "Absent"
        elif time >= class_start:
            status = "Late"
        else:
            status = "Present"

        # date and time is set to input current date and time upon recording
        sql = """
              INSERT INTO tbl_attendance (subject_id, instructor_id, student_id, class_start, class_end, attendance_status)
              VALUES (%s, %s, %s, %s, %s, %s)
              """

        curs.execute(sql, (subject_id, instructor_id, student_id, class_start, class_end, status,))
        conn.commit()

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return False

# TODO: Get list of students and iterate through the absent students





#* =====================
#* FOR THE GUI TABLES!!!
#* =====================

# fetch ALL ENTRIES for attendance log
def get_attendance_log():
    try:
        conn = get_connection()
        curs = conn.cursor()

        sql = """
            SELECT   a.date, a.time, st.student_name, e.course, e.year_level, e.section, a.attendance_status
            FROM tbl_attendance a
            INNER JOIN tbl_student st ON a.student_id = st.student_id
            INNER JOIN tbl_enrollment e ON e.student_id = st.student_id
            WHERE a.attendance_status NOT IN ('Absent')
        """
        
        curs.execute(sql)
        logs = curs.fetchall()
        
        # Store data into dictionary
        cols = [column[0] for column in curs.description]
        rows = [dict(zip(cols, row)) for row in logs]

        return cols, rows

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return False


# fetch ALL ENTRIES for class list
def get_class_list():
    try:
        conn = get_connection()
        curs = conn.cursor()

        sql = """
            SELECT DISTINCT a.date, a.class_start, a.subject_id, i.instructor_name
            FROM tbl_attendance a, tbl_subjects_enrolled se
            JOIN tbl_instructor i ON i.instructor_id = se.instructor_id 
        """
        
        curs.execute(sql)
        logs = curs.fetchall()
        
        # Store data into dictionary
        cols = [column[0] for column in curs.description]
        rows = [dict(zip(cols, row)) for row in logs]

        return cols, rows

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return False

# fetch records for a specific attendance sheet
# TODO: Fetch attendance sheet ordered alphabetically