# list of every attendance record 
def get_attendance_log(c_id: int):
    conn = get_connection()
    if not conn:
        return None
    try:
        curs = conn.cursor()

        curs.execute("""
                SELECT s.student_id, s.student_name, a.date, a.time, a.status, a.session_type, a.session_start, a.session_end
                FROM enrollment e
                INNER JOIN student s ON s.student_id = e.student_id
                INNER JOIN class c on c.block_id = e.block_id
                LEFT JOIN attendance a ON a.student_id = s.student_id AND a.class_id = c.class_id
                WHERE c.class_id = %s
                ORDER BY a.date DESC, s.student_name
            """,
            (c_id,)
        )
        rows = curs.fetchall()

        if not rows:
            return None
        
        log = []
        for stud_id, stud_name, date, time, status, session_type, session_start, session_end in rows:
            record = {
                "stud_id": stud_id,
                "stud_name": stud_name,
                "date": date,
                "time": time,
                "status": status,
                "session_type": session_type,
                "session_start": session_start,
                "session_end": session_end
            }
            log.append(record)
        
        return log
    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return None
    finally: 
        conn.close()
    
# get the class schedule details by class id
def get_class_log(c_id: int):
    conn = get_connection()
    if not conn:
        return None
    try:
        curs = conn.cursor()

        curs.execute("""
                SELECT c.class_id, s.subject_id, s.subject_title,
                   b.course_id, b.year_level, b.section,
                   sc.day_of_week, sc.sched_start, sc.sched_end
                FROM schedule sc
                INNER JOIN class c ON c.class_id = sc.class_id
                INNER JOIN subject s ON s.subject_id = c.subject_id
                INNER JOIN block b ON b.block_id = c.block_id
                WHERE c.class_id = %s
            """,
            (c_id,)
        )
        rows = curs.fetchone()

        if not rows:
            return None
        c_id, sub_id, sub_tt, crs_id, yr_lvl, sect, day, raw_bgn, raw_fin = rows
        bgn = _td_to_time(raw_bgn)
        fin = _td_to_time(raw_fin)
        label = f"{bgn.strftime('%I:%M %p')} - {fin.strftime('%I:%M %p')}"
        log = {
            "c_id": c_id,         
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
        return log
    except mysql.connector.Error as e:
        print(f"ERR: {e}")
        return None
    finally:
        conn.close()