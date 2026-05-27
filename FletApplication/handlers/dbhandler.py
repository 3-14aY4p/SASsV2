import mysql.connector
from datetime import timedelta
from datetime import date
from datetime import time
from datetime import datetime
import pandas as pd

# FUNCTION TEMPLATE -- Use this, please
'''
def func_name(func_args):
    conn = get_connection()
    if not conn:
        return None
    
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
        return None

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
        print(f"ERR: {e}")
        return None



#* QUERIES FOR RECORD EXISTENCE VALIDATION

# for instructors login
def query_login_credentials(instructor_id: str, password: str):
    conn = get_connection()
    if not conn:
        return None

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
            return None

        return {"id": instructor_id, "name": username[0]}

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return None

    finally:
        conn.close()

# for attendance recording    
def query_student_id(student_id: str):
    conn = get_connection()
    if not conn:
        return None
 
    try:
        curs = conn.cursor()
        curs.execute("""
            SELECT first_name, middle_name, last_name
            FROM student
            WHERE student_id = %s
            LIMIT 1
            """,
            (student_id,)
        )
        row = curs.fetchone()
        if not row:
            return None
        first, middle, last = row
        return " ".join(filter(None, [first, middle, last]))
 
    except mysql.connector.Error as e:
        print(f"ERR [query_student_id]: {e}")
        return None
 
    finally:
        conn.close()
 
def query_enrollment(student_id: str, class_id: int):
    conn = get_connection()
    if not conn:
        return None
 
    try:
        curs = conn.cursor()
        curs.execute("""
            SELECT 1
            FROM enrollment e
            INNER JOIN class c ON e.block_id = c.block_id
            WHERE e.student_id = %s
              AND c.class_id = %s
            LIMIT 1
            """,
            (student_id, class_id)
        )
        return curs.fetchone() is not None
 
    except mysql.connector.Error as e:
        print(f"ERR [query_enrollment]: {e}")
        return None
 
    finally:
        conn.close()
 
def query_attendance(student_id: str, class_id: int, session_end: time):
    conn = get_connection()
    if not conn:
        return None
 
    date_now = date.today()
    try:
        curs = conn.cursor()
        curs.execute("""
            SELECT 1
            FROM attendance
            WHERE student_id = %s
              AND class_id = %s
              AND date = %s
              AND session_end = %s
              AND status IN ('on time', 'late')
            LIMIT 1
            """,
            (student_id, class_id, date_now, session_end)
        )
        return curs.fetchone()
 
    except mysql.connector.Error as e:
        print(f"ERR [query_attendance]: {e}")
        return None
 
    finally:
        conn.close()
 
def record_attendance(student_id: str, class_id: int, session_type: str, session_start: time, session_end: time):
    conn = get_connection()
    if not conn:
        return "error"
 
    try:
        curs = conn.cursor()

        date_now = datetime.now().date()
        time_now = datetime.now().time()
        grace = (datetime.combine(date_now, session_start) + timedelta(minutes=15)).time()

        if time_now <= grace:
            status = 'on time'
        else:
            status = 'late'

        curs.execute("""
            INSERT INTO attendance
                (student_id, class_id, session_type, session_start, session_end, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (student_id, class_id, session_type, session_start, session_end, status)
        )
        conn.commit()
        
        return status
 
    except mysql.connector.Error as e:
        print(f"ERR [record_attendance]: {e}")
        return "error"
 
    finally:
        conn.close()



#* RETRIEVALS FOR UI COMPONENTS

# for new session components selection
def get_sections(instructor_id: str):
    conn = get_connection()
    if not conn:
        return None
    
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
        rows = curs.fetchall()

        if not rows:
            return None
        
        blocks = []
        for blk_id, crs_id, yr_lvl, sect in rows:
            block = {
                "blk_id": blk_id,
                "crs_id": crs_id,
                "yr_lvl": yr_lvl,
                "sect": sect
            }
            blocks.append(block)
        
        return blocks

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return None

    finally: 
        conn.close()

# specific to the block/section only
def get_subjects(instructor_id: str, block_id: int):
    conn = get_connection()
    if not conn:
        return None
    
    try:
        curs = conn.cursor()

        curs.execute("""
                SELECT DISTINCT c.subject_id
                FROM class c
                WHERE c.instructor_id = %s
                    AND c.block_id = %s
            """,
            (instructor_id, block_id)
        )
        rows = curs.fetchall()

        if not rows:
            return None
        
        subjects = []
        for subj in rows:
            subjects.append(subj[0])
        
        return subjects

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return None

    finally: 
        conn.close()

# for attendance recording
def get_class_id(instructor_id: str, subject_id: str, block_id: int):
    conn = get_connection()
    if not conn:
        return None
    
    try:
        curs = conn.cursor()

        curs.execute("""
                SELECT c.class_id
                FROM class c
                WHERE c.instructor_id = %s
                    AND c.subject_id = %s
                    AND c.block_id = %s
            """,
            (instructor_id, subject_id, block_id)
        )
        c_id = curs.fetchone()

        if not c_id:
            return None
        
        return c_id[0]

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return None

    finally: 
        conn.close()


# convert timedelta to time
def _td_to_time(td) -> time:
    if isinstance(td, timedelta):
        total = int(td.total_seconds())
        return time(total // 3600, (total % 3600) // 60, total % 60)
    return td

# specific to the block/section only
def get_day_schedules(instructor_id: str, subject_id: str, block_id: int):
    dow_map = {
        1: "monday", 2: "tuesday", 3: "wednesday",
        4: "thursday", 5: "friday", 6: "saturday",
        7: "sunday"
    }
    today_str = dow_map[datetime.now().isoweekday()]
    
    conn = get_connection()
    if not conn:
        return None
    
    try:
        curs = conn.cursor()

        curs.execute("""
                SELECT sc.sched_start, sc.sched_end
                FROM schedule sc
                INNER JOIN class c ON sc.class_id = c.class_id
                INNER JOIN block b ON c.block_id = b.block_id
                WHERE sc.day_of_week = %s
                    AND c.instructor_id = %s
                    AND c.subject_id = %s
                    AND b.block_id = %s
            """,
            (today_str, instructor_id, subject_id, block_id)
        )
        rows = curs.fetchall()

        if not rows:
            return None
        
        slots = []
        for raw_bgn, raw_fin in rows:
            bgn = _td_to_time(raw_bgn)
            fin = _td_to_time(raw_fin)
            label = f"{bgn.strftime('%I:%M %p')} – {fin.strftime('%I:%M %p')}"
            slot = {
                'sched_bgn': bgn,
                'sched_fin': fin,
                'label': label,
            }
            slots.append(slot)
        
        return slots

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return None

    finally: 
        conn.close()

# all schedule data
def get_all_schedules(instructor_id: str):
    conn = get_connection()
    if not conn:
        return None
    
    try:
        curs = conn.cursor()

        curs.execute("""
                SELECT s.subject_id, s.subject_title,
                   b.course_id, b.year_level, b.section,
                   sc.day_of_week, sc.sched_start, sc.sched_end
                FROM schedule sc
                INNER JOIN class c ON c.class_id = sc.class_id
                INNER JOIN subject s ON s.subject_id = c.subject_id
                INNER JOIN block b ON b.block_id = c.block_id
                WHERE c.instructor_id = %s
                ORDER BY FIELD(sc.day_of_week,
                    'monday','tuesday','wednesday',
                    'thursday','friday','saturday',
                    'sunday'),
                    sc.sched_start
            """,
            (instructor_id,)
        )
        rows = curs.fetchall()

        if not rows:
            return None

        schedules = []
        for sub_id, sub_tt, crs_id, yr_lvl, sect, day, raw_bgn, raw_fin in rows:
            bgn = _td_to_time(raw_bgn)
            fin = _td_to_time(raw_fin)
            label = f"{bgn.strftime('%I:%M %p')} – {fin.strftime('%I:%M %p')}"
            schedule= {
                "sub_id": sub_id,
                "sub_tt": sub_tt,
                "crs_id": crs_id,
                "yr_lvl": yr_lvl,
                "sect": sect,
                "day": day, 
                'sched_bgn': bgn,
                'sched_fin': fin,
                "label": label
            }
            schedules.append(schedule)
        
        return schedules

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return None

    finally: 
        conn.close()


# get attendance log for the current day or session
def get_attendance_log(class_id: int = None, session_end: time = None):
    conn = get_connection()
    if not conn:
        return None
    
    try:
        curs = conn.cursor()

        filters = ["a.date = CURDATE()"]
        params = []

        # the toggle for it being the day or session
        if class_id:
            filters.append("c.class_id = %s")
            params.append(class_id)
        if session_end:
            filters.append("a.session_end = %s")
            params.append(str(session_end))

        filters.append("a.status NOT IN ('absent')")            

        where = " AND ".join(filters)

        curs.execute(f"""
                SELECT a.time, a.status,
                    CONCAT_WS(' ', s.first_name, s.middle_name, s.last_name) AS student_name,
                    s.student_id,
                    b.course_id, b.year_level, b.section
                FROM attendance a
                INNER JOIN student s ON a.student_id = s.student_id
                INNER JOIN class c ON a.class_id = c.class_id
                INNER JOIN block b ON c.block_id = b.block_id
                WHERE {where}
                ORDER BY a.time DESC
            """,
            params
        )
        logs = curs.fetchall()
        
        if not logs:
            return None

        cols = [column[0] for column in curs.description]
        rows = [dict(zip(cols, row)) for row in logs]

        return rows

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return None

    finally: 
        conn.close()

# get list of all classes
def get_class_log(instructor_id: str, session_date: date = None, session_start: time = None,
                  block_id: int = None, subject_id: str = None):
    conn = get_connection()
    if not conn:
        return None
    
    try:
        curs = conn.cursor()

        filters = ["c.instructor_id = %s"]
        params = [instructor_id]

        # optional filters
        if session_date:
            filters.append("a.date = %s")
            params.append(str(session_date))
        if session_start:
            filters.append("a.session_start = %s")
            params.append(str(session_start))
        if block_id:
            filters.append("c.block_id = %s")
            params.append((block_id))
        if subject_id:
            filters.append("c.subject_id = %s")
            params.append(subject_id)

        where = " AND ".join(filters)

        curs.execute(f"""
                SELECT DISTINCT a.date, a.session_start, a.session_end, a.session_type,
                    s.subject_id,
                    b.course_id, b.year_level, b.section,
                    c.class_id
                FROM attendance a
                INNER JOIN class c ON a.class_id = c.class_id
                INNER JOIN subject s ON c.subject_id = s.subject_id
                INNER JOIN block b ON c.block_id = b.block_id
                WHERE {where}
                ORDER BY a.date DESC, a.session_start DESC
            """,
            params
        )
        rows = curs.fetchall()
        
        if not rows:
            return None

        logs = []
        for date, raw_bgn, raw_fin, stype, subj, crs_id, yr_lvl, sect, c_id in rows:
            bgn = _td_to_time(raw_bgn)
            fin = _td_to_time(raw_fin)
            label = f"{bgn.strftime('%I:%M %p')} – {fin.strftime('%I:%M %p')}"
            log = {
                'date': date,
                'sched_bgn': bgn,
                'sched_fin': fin,
                'time_label': label,
                'type': stype,
                'subj': subj,
                'c_id': c_id,
                "crs_id": crs_id,
                "yr_lvl": yr_lvl,
                "sect": sect
            }
            logs.append(log)

        return logs

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return None

    finally: 
        conn.close()

# get specific session attendance (prepare for export)
def get_session_log(class_id: int, session_date: date, session_end: time):
    conn = get_connection()
    if not conn:
        return None
    
    try:
        curs = conn.cursor()

        curs.execute("""
                SELECT a.time, a.status,
                    CONCAT_WS(' ', s.last_name, s.first_name, s.middle_name) AS student_name,
                    s.student_id
                FROM attendance a
                INNER JOIN class c ON a.class_id = c.class_id
                INNER JOIN student s ON a.student_id = s.student_id
                WHERE a.class_id = %s
                    AND a.date = %s
                    AND a.session_end = %s
                ORDER BY s.last_name ASC, s.first_name ASC
            """,
            (class_id, session_date, session_end)
        )
        logs = curs.fetchall()
        
        if not logs:
            return None

        cols = [column[0] for column in curs.description]
        rows = [dict(zip(cols, row)) for row in logs]

        return rows

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return None

    finally: 
        conn.close()

#* ADDED: analytics for each session
# returns total enrolled, counts of on time, late, and absent, and their respective percentages
def get_session_analytics(class_id: int, session_date: date, session_end: time):
    conn = get_connection()
    if not conn:
        return None
    
    try:
        curs = conn.cursor()

        # get total enrolled for this class
        curs.execute("""
                SELECT COUNT(*)
                FROM enrollment e
                INNER JOIN class c ON e.block_id = c.block_id
                WHERE c.class_id = %s
            """,
            (class_id,)
        )
        total_row = curs.fetchone()
        total = total_row[0] if total_row else 0

        # get per-status counts for this specific session
        curs.execute("""
                SELECT a.status, COUNT(*) as count
                FROM attendance a
                WHERE a.class_id = %s
                    AND a.date = %s
                    AND a.session_end = %s
                GROUP BY a.status
            """,
            (class_id, session_date, session_end)
        )
        status_rows = curs.fetchall()

        counts = {'on time': 0, 'late': 0, 'absent': 0}
        for status, count in (status_rows or []):
            if status in counts:
                counts[status] = count

        # absent = enrolled but no record
        counts['absent'] = max(0, total - counts['on time'] - counts['late'])

        # calculating for %
        ontime_pct = round(counts['on time'] / total * 100, 1) if total else 0.0
        late_pct   = round(counts['late']    / total * 100, 1) if total else 0.0
        absent_pct = round(counts['absent']  / total * 100, 1) if total else 0.0

        return {
            'total':       total,
            'on_time':     counts['on time'],
            'late':        counts['late'],
            'absent':      counts['absent'],
            'on_time_pct': ontime_pct,
            'late_pct':    late_pct,
            'absent_pct':  absent_pct,
        }

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return None

    finally: 
        conn.close()

# get all students in a class and their attendance status 
def get_all_students_in_class(class_id: int):
    conn = get_connection()
    if not conn:
        return None
    
    try:
        curs = conn.cursor()

        curs.execute("""
                SELECT s.student_id,
                    CONCAT_WS(' ', s.first_name, s.middle_name, s.last_name) AS student_name
                FROM enrollment e
                INNER JOIN student s ON e.student_id = s.student_id
                INNER JOIN class c ON e.block_id = c.block_id
                WHERE c.class_id = %s
                ORDER BY s.last_name ASC
            """,
            (class_id,)
        )
        recs = curs.fetchall()
        
        if not recs:
            return None

        cols = [column[0] for column in curs.description]
        rows = [dict(zip(cols, row)) for row in recs]

        return rows

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return None

    finally: 
        conn.close()

# combined present, late, and absent students
def get_students_of_status(class_id: int, session_date: date = datetime.today().date(), status: str = None):
    conn = get_connection()
    if not conn:
        return None
    
    try:
        curs = conn.cursor()

        if status:
            curs.execute("""
                    SELECT s.student_id,
                        CONCAT_WS(' ', s.first_name, s.middle_name, s.last_name) AS student_name
                    FROM attendance a
                    INNER JOIN student s ON a.student_id = s.student_id
                    WHERE a.class_id = %s
                        AND a.date = %s
                        AND a.status = %s
                    ORDER BY s.last_name ASC
                """,
                (class_id, session_date, status)
            )
        else:
            # logic here is to get all students that doesn't have an attendance record (or I guess, absent?)
            curs.execute("""
                    SELECT s.student_id,
                        CONCAT_WS(' ', s.first_name, s.middle_name, s.last_name) AS student_name
                    FROM enrollment e
                    INNER JOIN student s ON e.student_id = s.student_id
                    INNER JOIN class c ON e.block_id = c.block_id
                    WHERE c.class_id = %s
                        AND s.student_id NOT IN (
                            SELECT student_id FROM attendance
                            WHERE class_id = %s
                                AND date = %s
                                AND status IN ('on time', 'late')
                        )
                    ORDER BY s.last_name ASC
                """,
                (class_id, class_id, session_date)
            )

        value = curs.fetchall()

        if not value:
            return None
        
        return value

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return None

    finally: 
        conn.close() 


#* FILE EXPORT

# export attendance into .xlsx (excel sheet)
def export_sheet(class_id: int, session_date: date, session_start: time, session_end: time):
    conn = get_connection()
    if not conn:
        return None
    
    try:
        curs = conn.cursor()

        curs.execute("""
            SELECT s.student_id,
                CONCAT_WS(' ', s.first_name, s.middle_name, s.last_name) AS student_name,
                a.time, a.status
            FROM attendance a
            INNER JOIN class c ON a.class_id = c.class_id
            INNER JOIN student s ON a.student_id = s.student_id
            WHERE c.class_id = %s
                AND a.date = %s
                AND a.session_start = %s
                AND a.session_end = %s
            ORDER BY a.date DESC, a.time DESC
            """,
            (class_id, session_date, session_start, session_end)
        )
        rows = curs.fetchall()
        
        if not rows:
            return None
        
        file_path = f"attendance_{session_date}_{session_start}-{session_end}.xlsx"
        
        sheet_data = []
        for s_id, name, time, status in rows:
            sd = {
                "ID NO.": s_id, 
                "NAME": name, 
                "TIMESTAMP": _td_to_time(time).strftime('%I:%M %p'), 
                "STATUS": status.capitalize()
            }
            sheet_data.append(sd)
            
        df = pd.DataFrame(sheet_data)
        df.to_excel(f"attendance_{session_date}_{session_start}-{session_end}.xlsx", sheet_name=f"{session_date}")
        
        return file_path

    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return None

    finally: 
        conn.close()
