import mysql.connector
from mysql.connector import Error
from datetime import datetime, time, date


# ── connection ────────────────────────────────────────────────────────────────

def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            database="db_SmartAttendance",
            password="",
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"ERR [get_connection]: {e}")
        return None


# ── student ───────────────────────────────────────────────────────────────────

def query_student_id(student_id: str) -> dict:
    """
    Returns {"status": True, "name": "Juan Dela Cruz"} if the student exists,
    or {"status": False} if not found / on error.
    """
    conn = get_connection()
    if not conn:
        return {"status": False}

    try:
        curs = conn.cursor()
        curs.execute(
            """
            SELECT first_name, middle_name, last_name
            FROM student
            WHERE student_id = %s
            """,
            (student_id,),
        )
        row = curs.fetchone()

        if not row:
            return {"status": False}

        first, middle, last = row
        # build full name, skip middle if NULL
        full_name = " ".join(filter(None, [first, middle, last]))
        return {"status": True, "name": full_name}

    except Error as e:
        print(f"ERR [query_student_id]: {e}")
        return {"status": False}

    finally:
        conn.close()


# ── enrollment ────────────────────────────────────────────────────────────────

def query_subject_enrollment(student_id: str, subject_id: str, instructor_id: str) -> bool:
    """
    Returns True if the student is enrolled in the given subject under the given instructor.
    """
    conn = get_connection()
    if not conn:
        return False

    try:
        curs = conn.cursor()
        curs.execute(
            """
            SELECT 1
            FROM enrollment e
            INNER JOIN subject_enrollment se ON se.enrollment_id = e.enrollment_id
            WHERE e.student_id   = %s
              AND se.subject_id  = %s
              AND se.instructor_id = %s
            LIMIT 1
            """,
            (student_id, subject_id, instructor_id),
        )
        return curs.fetchone() is not None

    except Error as e:
        print(f"ERR [query_subject_enrollment]: {e}")
        return False

    finally:
        conn.close()


# ── schedule ──────────────────────────────────────────────────────────────────

def _td_to_time(td) -> time:
    """Convert a MariaDB timedelta (or plain time) to datetime.time."""
    from datetime import timedelta
    if isinstance(td, timedelta):
        total = int(td.total_seconds())
        return time(total // 3600, (total % 3600) // 60, total % 60)
    return td  # already a time object


def get_schedule(subject_id: str, instructor_id: str) -> list:
    """
    Returns all time slots for the given subject/instructor on today's day of week.
    Each item: {"start": time(...), "end": time(...), "label": "07:30 – 08:30"}
    Returns [] if none found or on error.
    """
    conn = get_connection()
    if not conn:
        return []

    try:
        curs = conn.cursor()

        dow_map = {
            1: "monday", 2: "tuesday",  3: "wednesday",
            4: "thursday", 5: "friday", 6: "saturday", 7: "sunday"
        }
        today_str = dow_map[datetime.now().isoweekday()]

        # schedule has class_id FK; subject/instructor live on the class table
        curs.execute(
            """
            SELECT s.sched_start, s.sched_end
            FROM schedule s
            INNER JOIN class c ON c.class_id = s.class_id
            WHERE c.subject_id    = %s
              AND c.instructor_id = %s
              AND s.day_of_week   = %s
            ORDER BY s.sched_start ASC
            """,
            (subject_id, instructor_id, today_str),
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


# ── attendance ────────────────────────────────────────────────────────────────

def query_attendance(student_id: str, subject_id: str, session_date: date, session_start: time) -> bool:
    """
    Returns True if an attendance record already exists for this student/subject/session.
    Prevents double-recording within the same session.
    """
    conn = get_connection()
    if not conn:
        return False

    try:
        curs = conn.cursor()
        curs.execute(
            """
            SELECT 1
            FROM attendance
            WHERE student_id   = %s
              AND subject_id   = %s
              AND date         = %s
              AND session_start = %s
              AND status IN ('on time', 'late')
            LIMIT 1
            """,
            (student_id, subject_id, session_date, session_start),
        )
        return curs.fetchone() is not None

    except Error as e:
        print(f"ERR [query_attendance]: {e}")
        return False

    finally:
        conn.close()


def record_attendance(
    student_id: str,
    subject_id: str,
    instructor_id: str,
    session_type: str,
    session_start: time,
    session_end: time,
    late_threshold_minutes: int = 15,
) -> bool:
    """
    Inserts an attendance row for a student.
    Status logic:
      - Before session_start + late_threshold  → 'on time'
      - After that but before session_end       → 'late'
      - At or after session_end                 → 'absent'
    Returns True on success, False on failure.
    """
    conn = get_connection()
    if not conn:
        return False

    try:
        curs = conn.cursor()

        now_dt   = datetime.now()
        now_date = now_dt.date()
        now_time = now_dt.time()

        # Convert times to comparable datetimes (same date)
        def to_dt(t: time):
            return datetime.combine(now_date, t)

        late_cutoff = to_dt(session_start) + __import__("datetime").timedelta(minutes=late_threshold_minutes)

        if now_dt >= to_dt(session_end):
            status = "absent"
        elif now_dt >= late_cutoff:
            status = "late"
        else:
            status = "on time"

        curs.execute(
            """
            INSERT INTO attendance
                (subject_id, instructor_id, student_id, date, time,
                 session_type, session_start, session_end, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                subject_id,
                instructor_id,
                student_id,
                now_date,
                now_time,
                session_type,
                session_start,
                session_end,
                status,
            ),
        )
        conn.commit()
        return True

    except Error as e:
        print(f"ERR [record_attendance]: {e}")
        return False

    finally:
        conn.close()


def mark_absents(subject_id: str, instructor_id: str, session_date: date, session_start: time, session_end: time, session_type: str = "regular") -> int:
    """
    After a session ends, insert 'absent' rows for every enrolled student
    who has no attendance record for this session yet.
    Returns the number of rows inserted.
    """
    conn = get_connection()
    if not conn:
        return 0

    try:
        curs = conn.cursor()

        # Find enrolled students with no record for this session
        curs.execute(
            """
            SELECT e.student_id
            FROM enrollment e
            INNER JOIN subject_enrollment se ON se.enrollment_id = e.enrollment_id
            WHERE se.subject_id    = %s
              AND se.instructor_id = %s
              AND e.student_id NOT IN (
                  SELECT student_id
                  FROM attendance
                  WHERE subject_id    = %s
                    AND date          = %s
                    AND session_start = %s
              )
            """,
            (subject_id, instructor_id, subject_id, session_date, session_start),
        )
        absent_students = curs.fetchall()

        count = 0
        for (student_id,) in absent_students:
            curs.execute(
                """
                INSERT INTO attendance
                    (subject_id, instructor_id, student_id, date, time,
                     session_type, session_start, session_end, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'absent')
                """,
                (
                    subject_id,
                    instructor_id,
                    student_id,
                    session_date,
                    session_end,   # time logged at session end
                    session_type,
                    session_start,
                    session_end,
                ),
            )
            count += 1

        conn.commit()
        return count

    except Error as e:
        print(f"ERR [mark_absents]: {e}")
        return 0

    finally:
        conn.close()


# ── GUI tables ────────────────────────────────────────────────────────────────

def get_attendance_log(subject_id: str = None, session_date: date = None):
    """
    Returns (cols, rows) for the attendance log table.
    Optionally filter by subject and/or date.
    """
    conn = get_connection()
    if not conn:
        return [], []

    try:
        curs = conn.cursor()

        filters = []
        params  = []
        if subject_id:
            filters.append("a.subject_id = %s")
            params.append(subject_id)
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
                c.course_id,
                b.year_level,
                b.section,
                sub.subject_title,
                a.status
            FROM attendance a
            INNER JOIN student     s   ON s.student_id     = a.student_id
            INNER JOIN enrollment  e   ON e.student_id     = s.student_id
            INNER JOIN block       b   ON b.block_id       = e.block_id
            INNER JOIN course      c   ON c.course_id      = b.course_id
            INNER JOIN subject     sub ON sub.subject_id   = a.subject_id
            {where}
            ORDER BY a.date ASC, a.time ASC
            """,
            params,
        )
        logs = curs.fetchall()
        cols = [col[0] for col in curs.description]
        rows = [dict(zip(cols, row)) for row in logs]
        return cols, rows

    except Error as e:
        print(f"ERR [get_attendance_log]: {e}")
        return [], []

    finally:
        conn.close()


def get_class_list():
    """
    Returns (cols, rows) of distinct sessions that have attendance records.
    """
    conn = get_connection()
    if not conn:
        return [], []

    try:
        curs = conn.cursor()
        curs.execute(
            """
            SELECT DISTINCT
                a.date,
                a.session_start  AS class_start,
                a.session_end,
                a.subject_id,
                sub.subject_title,
                i.instructor_name
            FROM attendance a
            INNER JOIN subject    sub ON sub.subject_id   = a.subject_id
            INNER JOIN instructor i   ON i.instructor_id  = a.instructor_id
            ORDER BY a.date ASC, a.session_start ASC
            """
        )
        logs = curs.fetchall()
        cols = [col[0] for col in curs.description]
        rows = [dict(zip(cols, row)) for row in logs]
        return cols, rows

    except Error as e:
        print(f"ERR [get_class_list]: {e}")
        return [], []

    finally:
        conn.close()


def get_attendance_sheet(subject_id: str, session_date: date, session_start: time):
    """
    Returns (cols, rows) for one session's full attendance sheet,
    including absent students, ordered alphabetically.
    """
    conn = get_connection()
    if not conn:
        return [], []

    try:
        curs = conn.cursor()
        curs.execute(
            """
            SELECT
                CONCAT_WS(' ', s.last_name, s.first_name, s.middle_name) AS student_name,
                s.student_id,
                a.time,
                a.status
            FROM attendance a
            INNER JOIN student s ON s.student_id = a.student_id
            WHERE a.subject_id    = %s
              AND a.date          = %s
              AND a.session_start = %s
            ORDER BY s.last_name ASC, s.first_name ASC
            """,
            (subject_id, session_date, session_start),
        )
        rows_raw = curs.fetchall()
        cols = [col[0] for col in curs.description]
        rows = [dict(zip(cols, row)) for row in rows_raw]
        return cols, rows

    except Error as e:
        print(f"ERR [get_attendance_sheet]: {e}")
        return [], []

    finally:
        conn.close()