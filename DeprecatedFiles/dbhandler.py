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
            print("Connected successfully!")
            return conn

    except mysql.connector.Error as e:
        print("ERROR:", e)
        return None


# * QUERIES FOR VALIDATING EXISTENCE OF RECORDS

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

        return {"id": instructor_id, "name": username[0]}

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return False

    finally:
        conn.close()


# validate existence of student_id
def query_student_id(student_id: str) -> str | bool:
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


# validates if student has already recorded PRESENT or LATE for the session
def query_attendance(student_id: str, class_id: int, session_date: date,
                     session_start: time) -> bool:
    conn = get_connection()
    if not conn:
        return False

    try:
        curs = conn.cursor()

        curs.execute("""
            SELECT 1
            FROM attendance
            WHERE student_id = %s
                AND class_id = %s
                AND date = %s
                AND session_start = %s
                AND status IN ('on time', 'late')
            LIMIT 1
            """,
                     (student_id, class_id, session_date, session_start,)
                     )
        return curs.fetchone() is not None

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return False

    finally:
        conn.close()






# * QUERIES FOR DATA RETRIEVALS

# Retrieve sections under the instructor
def get_instructor_sections(instructor_id: str):
    conn = get_connection()
    if not conn:
        return False

    try:
        curs = conn.cursor()

        curs.execute("""
            SELECT DISTINCT b.block_id, b.course_id, b.year_level, b.section 
            FROM block b
            INNER JOIN class c ON c.block_id = b.block_id
            WHERE c.instructor_id = %s
            ORDER BY b.course_id, b.year_level, b.section
            """,
                     (instructor_id,)
                     )
        row = curs.fetchall()

        if not row:
            return False

        blocks = []
        for block_id, course, year, section in row:
            block = {
                "block_id": block_id,
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


# Retrieve instructor's subjects for a specific section
def get_instructor_subjects(instructor_id: str, section: dict = None):
    conn = get_connection()
    if not conn:
        return False

    try:
        curs = conn.cursor()

        if section:
            curs.execute("""
                SELECT DISTINCT c.subject_id
                FROM class c
                INNER JOIN block b ON c.block_id = b.block_id
                WHERE c.instructor_id = %s
                    AND b.course_id = %s
                    AND b.year_level = %s
                    AND b.section = %s
                """,
                (instructor_id, section['course'], section['year'], section['section'])
            )
        else:
            curs.execute("""
                SELECT DISTINCT c.subject_id
                FROM class c
                WHERE c.instructor_id = %s
                """,
                (instructor_id,)
            )
        row = curs.fetchall()

        if not row:
            return False

        subjects = []
        for subject in row:
            subjects.append(subject[0])

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
        1: "monday", 2: "tuesday", 3: "wednesday",
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
                SELECT sc.sched_start, sc.sched_end, sc.day_of_week, c.class_id
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
                     (instructor_id, subject_id, section['course'], section['year'], section['section'], today_str)
                     )
        rows = curs.fetchall()

        if not rows:
            return False

        slots = []
        for raw_start, raw_end, day, class_id in rows:
            start = _td_to_time(raw_start)
            end = _td_to_time(raw_end)
            label = f"{start.strftime('%I:%M %p')} – {end.strftime('%I:%M %p')}"
            slots.append({"start": start, "end": end, "class_id": class_id, "label": label})

        return slots

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return False

    finally:
        conn.close()


# TODO: Retrieve all schedules of the Instructor
def get_instructor_all_schedules(instructor_id: str):
    conn = get_connection()
    if not conn:
        return False

    try:
        curs = conn.cursor()

        curs.execute("""
            SELECT s.subject_id, s.subject_title,
                   b.course_id, b.year_level, b.section,
                   sc.day_of_week, sc.sched_start, sc.sched_end
            FROM schedule sc
            INNER JOIN class c  ON c.class_id  = sc.class_id
            INNER JOIN subject s ON s.subject_id = c.subject_id
            INNER JOIN block b   ON b.block_id   = c.block_id
            WHERE c.instructor_id = %s
            ORDER BY FIELD(sc.day_of_week,
                'monday','tuesday','wednesday',
                'thursday','friday','saturday','sunday'),
                sc.sched_start
            """,
                     (instructor_id,)
                     )
        rows = curs.fetchall()

        if not rows:
            return False

        schedules = []
        for subject_id, subject_title, course, year, section, day, raw_start, raw_end in rows:
            schedules.append({
                "subject_id": subject_id,
                "subject_title": subject_title,
                "course": course,
                "year": year,
                "section": section,
                "day": day,
                "start": _td_to_time(raw_start),
                "end": _td_to_time(raw_end),
                "label": f"{_td_to_time(raw_start).strftime('%I:%M %p')} – {_td_to_time(raw_end).strftime('%I:%M %p')}"
            })

        return schedules

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return False

    finally:
        conn.close()


def get_attendance_log(instructor_id: str = None, session_date: date = None):
    # Returns list of row dicts for the attendance log table
    conn = get_connection()
    if not conn:
        return []

    try:
        curs = conn.cursor()

        filters = []
        params  = []
        if instructor_id:
            filters.append("c.instructor_id = %s")
            params.append(instructor_id)
        if session_date:
            filters.append("a.date = %s")
            params.append(session_date)

        where = ("WHERE " + " AND ".join(filters)) if filters else ""

        curs.execute(
            f"""
            SELECT
                a.date,
                a.time,
                CONCAT_WS(' ', s.first_name, s.middle_name, s.last_name) AS student_name,
                b.course_id,
                b.year_level,
                b.section,
                c.subject_id,
                a.status
            FROM attendance a
            INNER JOIN student s ON s.student_id = a.student_id
            INNER JOIN class   c ON c.class_id   = a.class_id
            INNER JOIN block   b ON b.block_id   = c.block_id
            {where}
            ORDER BY a.date DESC, a.time DESC
            """,
            params,
        )
        rows_raw = curs.fetchall()
        cols = [col[0] for col in curs.description]
        return [dict(zip(cols, row)) for row in rows_raw]

    except mysql.connector.Error as e:
        print(f"ERR [get_attendance_log]: {e}")
        return []

    finally:
        conn.close()


# TODO: Populate Class datatables
def get_class_list(instructor_id: str, subject_id: str = None,
                   session_date: date = None, session_start: time = None,
                   section: dict = None):
    conn = get_connection()
    if not conn:
        return False

    try:
        curs = conn.cursor()

        filters = ["c.instructor_id = %s"]
        params  = [instructor_id]

        # ADDED: Optional filters
        if subject_id:
            filters.append("c.subject_id = %s")
            params.append(subject_id)
        if session_date:
            filters.append("a.date = %s")
            params.append(str(session_date))
        if session_start:
            filters.append("a.session_start = %s")
            params.append(session_start)
        if section:
            filters.append("b.course_id = %s AND b.year_level = %s AND b.section = %s")
            params.extend([section['course'], section['year'], section['section']])

        where = " AND ".join(filters)

        curs.execute(f"""
            SELECT DISTINCT
                a.date,
                a.session_start,
                a.session_end,
                sub.subject_id,
                sub.subject_title,
                b.course_id,
                b.year_level,
                b.section,
                a.session_type
            FROM attendance a
            INNER JOIN class c      ON c.class_id     = a.class_id
            INNER JOIN subject sub  ON sub.subject_id = c.subject_id
            INNER JOIN block b      ON b.block_id     = c.block_id
            WHERE {where}
            ORDER BY a.date DESC, a.session_start ASC
            """,
                     params
                     )
        rows = curs.fetchall()

        if not rows:
            return False

        cols = [col[0] for col in curs.description]
        return [dict(zip(cols, row)) for row in rows]

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return False

    finally:
        conn.close()

# TODO: Retrieve specific class/session attendance
def get_session_attendance(instructor_id: str, subject_id: str, session_date: date, session_start: time):
    conn = get_connection()
    if not conn:
        return False

    try:
        curs = conn.cursor()

        curs.execute("""
            SELECT
                CONCAT_WS(' ', s.last_name, s.first_name, s.middle_name) AS student_name,
                s.student_id,
                a.time      AS time_in,
                a.status
            FROM attendance a
            INNER JOIN class c    ON c.class_id   = a.class_id
            INNER JOIN student s  ON s.student_id = a.student_id
            WHERE c.instructor_id  = %s
              AND c.subject_id     = %s
              AND a.date           = %s
              AND a.session_start  = %s
            ORDER BY s.last_name ASC, s.first_name ASC
            """,
                     (instructor_id, subject_id, session_date, session_start)
                     )
        rows = curs.fetchall()

        if not rows:
            return False

        cols = [col[0] for col in curs.description]
        return [dict(zip(cols, row)) for row in rows]

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return False

    finally:
        conn.close()

# Record attendance entry
def record_attendance(student_id: str, class_id: int,
                      session_date: date, session_start: time, session_end: time,
                      session_type: str = 'regular') -> str:
    conn = get_connection()
    if not conn:
        return "error"

    try:
        curs = conn.cursor()

        now = datetime.now().time()
        grace = (datetime.combine(session_date, session_start)
                 + timedelta(minutes=15)).time()

        if now <= grace:
            status = 'on time'
        else:
            status = 'late'

        curs.execute("""
            INSERT INTO attendance
                (student_id, class_id, date, time, session_start, session_end, session_type, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (student_id, class_id, session_date, now,
             session_start, session_end, session_type, status)
        )
        conn.commit()
        return status

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return "error"

    finally:
        conn.close()