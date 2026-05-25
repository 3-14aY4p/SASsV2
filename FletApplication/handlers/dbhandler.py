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
def query_student_id():
    pass

def query_enrollment():
    pass

def query_attendance():
    pass

def record_attendance():
    pass



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
                SELECT sc.sched_start, sc.sched_end, c.class_id
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
        for raw_bgn, raw_fin, cls_id in rows:
            bgn = _td_to_time(raw_bgn)
            fin = _td_to_time(raw_fin)
            label = f"{bgn.strftime('%I:%M %p')} - {fin.strftime('%I:%M %p')}"
            slot = {
                'sched_bgn': bgn,
                'sched_fin': fin,
                'label': label,
                'cls_id': cls_id
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
            ()
        )
        rows = curs.fetchall()

        if not rows:
            return None

        schedules = []
        for sub_id, sub_tt, crs_id, yr_lvl, sect, day, raw_bgn, raw_fin in rows:
            bgn = _td_to_time(raw_bgn)
            fin = _td_to_time(raw_fin)
            label = f"{bgn.strftime('%I:%M %p')} - {fin.strftime('%I:%M %p')}"
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

# for populating datatables