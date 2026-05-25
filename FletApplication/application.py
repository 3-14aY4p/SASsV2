# Module/Library imports
import threading
import time as t
from datetime import date
from datetime import time
from datetime import datetime
import flet as ft


# Custom imports for handler files
import handlers.dbhandler as db
import handlers.cvhandler as cv



#* MAIN FUNCTION
def main(page: ft.Page):
    ft.context.enable_auto_update()
    
    # Page settings
    page.title = "SASs: Smart Attendance System"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(font_family="Mono")
    
    WIDTH, HEIGHT = 1280, 720
    page.width = WIDTH
    page.height = HEIGHT
    
    page.window.min_width = WIDTH
    page.window.min_height = HEIGHT
    page.window.max_width = WIDTH
    page.window.max_height = HEIGHT
    
    page.window.resizable = False
    page.window.minimizable = False
    page.window.maximizable = False
    
    
    # UI pop-ups
    def alert_snackbar(text: str):
        page.show_dialog(ft.SnackBar(ft.Text(text,
                                             color=ft.Colors.ON_SURFACE_VARIANT),
                                     bgcolor=ft.Colors.SURFACE_CONTAINER))

    def confirmation_popup(title_text: str, subtitle_text: str, on_confirm):
        page.show_dialog(ft.AlertDialog(
            modal=True,
            title=ft.Text(title_text),
            content=ft.Text(subtitle_text),
            actions=[
                ft.TextButton("Yes", on_click=lambda e: (
                        page.pop_dialog(),
                        on_confirm()
                    )),
                ft.TextButton("No", on_click=lambda e: page.pop_dialog()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        ))

    # Convert strings into datetime objects
    def convert_time(time_str: str) -> time | None:
        format = "%H:%M"
        try:
            time = datetime.strptime(time_str, format).time()
            return time
        except ValueError as e:
            alert_snackbar("ERR: Invalid format.")
            return None
        
    def convert_date(date_str: str) -> date | None:
        format = "%Y/%m/%d"
        try:
            date = datetime.strptime(date_str, format).date()
            return date
        except ValueError as e:
            alert_snackbar("ERR: Invalid format.")
            return None


    #* PAGE 0 COMPONENTS
    
    # Login information
    current_user = ""
    current_u_id = ""
    
    userid_field = ft.TextField(
            border_color=ft.Colors.SURFACE_BRIGHT,
            width=325, height=50,
            border_radius=10,
            label=ft.Text("ID Number"),
        )
    passwd_field = ft.TextField(
            border_color=ft.Colors.SURFACE_BRIGHT,
            width=325, height=50,
            border_radius=10,
            label=ft.Text("Password"),
            password=True,
        )
    
    def login():
        nonlocal current_user, current_u_id
        
        if userid_field.value == "" or passwd_field == "":
            alert_snackbar("ERR [ID/Password Field]: Input field empty.")
            return

        userid: str = userid_field.value
        passwd: str = passwd_field.value
        
        usernm = db.query_login_credentials(userid, passwd)
        if not usernm:
            alert_snackbar("ERR: Incorrect ID or Password.")
            return
        
        current_user = usernm.get('name')
        current_u_id = userid

        setattr(userid_field, 'value', "")
        setattr(passwd_field, 'value', "")
        
        update_user_details()
        update_recent_activity()
        update_day_schedule()
        start_dashb_time_thread()
        
        current_navi.content = navbar
        current_page.content = page_1
        
    def logout():
        nonlocal current_user, current_u_id

        current_user = ""
        current_u_id = ""
        
        current_navi.content = None
        current_page.content = page_0
    
    
    #* PAGE 1 COMPONENTS
    
    camera_active_status = False
    camera_active = False
    session_active = False
    
    cam_status_1 = ft.Text(value="Scanner active" if camera_active_status else "Scanner inactive",
                            style=ft.TextStyle(
                                weight=ft.FontWeight.NORMAL,
                                size=12,
                                color=ft.Colors.ON_SURFACE_VARIANT
                            )
                        )
    cam_status_2 = ft.Text(value="Camera connected" if camera_active_status else "Camera disconnected",
                            style=ft.TextStyle(
                                weight=ft.FontWeight.NORMAL,
                                size=12,
                                color=ft.Colors.ON_SURFACE_VARIANT
                            ),
                        )

    recent_activity_column = ft.Column(controls=[])
    day_schedule_column = ft.Column(controls=[])

    user_greeting = ft.Text(value=f"Welcome, {current_user}",
            style=ft.TextStyle(
                weight=ft.FontWeight.BOLD,
                size=28,
                color=ft.Colors.ON_SURFACE_VARIANT
            )
        )

    date_today = ft.Text(value=f"{datetime.now().strftime("%b %d, %Y || %A")}",
            style=ft.TextStyle(
                weight=ft.FontWeight.BOLD,
                size=24,
                color=ft.Colors.ON_SURFACE_VARIANT
            )
        )
    time_today = ft.Text(value=f"{datetime.now().strftime("%I:%M %p")}",
            style=ft.TextStyle(
                weight=ft.FontWeight.BOLD,
                size=24,
                color=ft.Colors.ON_SURFACE_VARIANT
            )
        )
    
    db_session_details = [
        ft.Text(value="No active session",
                style=ft.TextStyle(
                    weight=ft.FontWeight.NORMAL,
                    size=14,
                    color=ft.Colors.ON_SURFACE_VARIANT
                )
            ),
        ft.Text(value="No active session",
                style=ft.TextStyle(
                    weight=ft.FontWeight.NORMAL,
                    size=14,
                    color=ft.Colors.ON_SURFACE_VARIANT
                )
            ),
        ft.Text(value="No active session",
                style=ft.TextStyle(
                    weight=ft.FontWeight.NORMAL,
                    size=14,
                    color=ft.Colors.ON_SURFACE_VARIANT
                )
            ),
        ]
    
    def update_user_details():
        user_greeting.value = f"Welcome, {current_user}"
    
    def update_cam_status():
        nonlocal cam_status_1, cam_status_2
        
        cam_status_1.value = "Scanner active" if camera_active_status else "Scanner inactive"
        cam_status_2.value = "Camera connected" if camera_active_status else "Camera disconnected"

    def update_recent_activity():
        recent_activity_column.controls.clear()
        
        rows = db.get_attendance_log(current_u_id)
        if rows:
            index = 0
            for r in rows:
                index += 1
                recent_activity_column.controls.append(
                    ft.Text(f"[{r['time']}] : {r['student_id']}\n{r['student_name']}", size=11)
                )
                if index == 5:
                    break

    def update_day_schedule():
        day_schedule_column.controls.clear()
        schedules = db.get_all_schedules(current_u_id)
        
        if not schedules:
            day_schedule_column.controls.append(
                    ft.Text(value="+ You have no schedule lined up for today.")
                )
        else:
            today_str = datetime.now().strftime("%A").lower()
            is_today: bool
            
            for s in schedules:
                is_today = s.get('day').lower() == today_str
                if is_today:
                    day_schedule_column.controls.append(
                        ft.Container(
                            bgcolor=ft.Colors.SURFACE_CONTAINER if not is_today else ft.Colors.SURFACE_CONTAINER_HIGH,
                            border_radius=15,
                            padding=15,
                            content=ft.Row([
                                ft.Column([
                                    ft.Text(f"{s.get('sub_id','')} — {s.get('sub_tt','')}",
                                            style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=15,
                                                            color=ft.Colors.ON_SURFACE_VARIANT)),
                                    ft.Text(f"{s.get('crs_id','')} {s.get('yr_lvl','')}{s.get('sect','')}  |  {s.get('day','').capitalize()}  |  {s.get('label','')}",
                                            style=ft.TextStyle(size=13, color=ft.Colors.ON_SURFACE_VARIANT)),
                                ], spacing=4),
                            ])
                        )
                    )
            
                else:
                    day_schedule_column.controls.clear()
                    day_schedule_column.controls.append(
                            ft.Text(value="+ You have no schedule lined up for today.")
                        )
                
    
    #* PAGE 2 COMPONENTS
    
    # Session information
    session_details ={
            "bgn": None,
            "fin": None,
            "sect": "",
            "subj": "",
            "type": "",
            "b_id": -1,     # block id
            "c_id": -1      # class id
        }
    session_details_ui = [
        ft.Text(value="+  SESSION:     None",
                style=ft.TextStyle(
                    weight=ft.FontWeight.NORMAL,
                    size=14,
                    color=ft.Colors.ON_SURFACE_VARIANT
                )
            ),
        ft.Text(value="+  SECTION:     None",
                style=ft.TextStyle(
                    weight=ft.FontWeight.NORMAL,
                    size=14,
                    color=ft.Colors.ON_SURFACE_VARIANT
                )
            ),
        ft.Text(value="+  SUBJECT:     None",
                style=ft.TextStyle(
                    weight=ft.FontWeight.NORMAL,
                    size=14,
                    color=ft.Colors.ON_SURFACE_VARIANT
                )
            ),
        ]
    
    def new_session():
        update_sect_options()
        subject_options.clear()
        timeslot_options.clear()
        
        nsession_bgn_field.value = datetime.now().strftime("%H:%M")
        
        current_page.content = page_5
    
    def cancel_current_session():
        def on_confirm():
            nonlocal session_details, session_active
            
            if camera_active:
                kill_scanner_thread()
                
                session_details ={
                        "bgn": None,
                        "fin": None,
                        "sect": "",
                        "subj": "",
                        "type": "",
                        "b_id": -1,     # block id
                        "c_id": -1      # class id
                    }
                update_session_ui_comp(True)
                session_active = False
                
                page.update()
                
        confirmation_popup("Confirm", "Do you want to cancel current session?", on_confirm)
    
    # ID scanner input fields
    camera_preview = ft.Image(
            src="FletApplication/empty.jpg",
            width=760,
            height=495,
            fit=ft.BoxFit.COVER,
        )
    camera_preview.src_base64 = ""
    video_container = ft.Container(
            bgcolor=ft.Colors.BLACK,
            expand=True,
            width=716, height=415,
            border_radius=20,
            content=None
        )
    manual_id_input = ft.TextField(
            width=716, height = 60,
            label = "Manual ID Input",
            hint_text= "xxxx-xxxx-x",
            border_color = ft.Colors.SURFACE_BRIGHT,
            on_submit=lambda e: on_manual_log(e)
        )
    
    # Scanned object details
    scanned_id = ft.Text(
            value="\t\t\tNone",
            style=ft.TextStyle(
                weight=ft.FontWeight.NORMAL,
                size=12,
                color=ft.Colors.ON_SURFACE_VARIANT
            )
        )
    scanned_name = ft.Text(
            value="\t\t\tNone",
            style=ft.TextStyle(
                weight=ft.FontWeight.NORMAL,
                size=12,
                color=ft.Colors.ON_SURFACE_VARIANT
            )
        )
    scan_status = ft.Text(
            value="\t\t\tNone",
            style=ft.TextStyle(
                weight=ft.FontWeight.NORMAL,
                size=12,
                color=ft.Colors.ON_SURFACE_VARIANT
            )
        )
    
    def update_scanner_output_ui():
        scanned_id.update()
        scanned_name.update()
        scan_status.update()
    
    def on_manual_log(e: ft.Event[ft.TextField]):
        student_id = e.control.value.strip()
        if not student_id:
            alert_snackbar("ERR [ID Input Field]: Input field empty.")
            return
        
        manual_id_input.value = ""
        manual_id_input.update()
        
        log_attendance(student_id, "manual")
    
    def on_scan(ret_string: str, is_valid: bool):
        if not is_valid:          
            scanned_id.value = "\t\t\tNone"
            scanned_name.value = "\t\t\tNone"
            scan_status.value = "\t\t\tNone"
            update_scanner_output_ui()
            
            return

        log_attendance(ret_string)
        
    # FIXME: The UI updates are inconsistent despite having a ret_string
    def log_attendance(student_id: str, input_type: str = "scan"):
        if not all(session_details.values()):
            alert_snackbar("ERR: No active session.")
            return
        
        full_name = db.query_student_id(student_id)
        if not full_name:
            scanned_id.value = f"\t\t\t{student_id}"
            scanned_name.value = "\t\t\tNOT FOUND"
            scan_status.value = "\t\t\tERR: Invalid ID"
            update_scanner_output_ui()
            
            if input_type != "scan":
                alert_snackbar("ERR: Student not found.")
            return
            
        is_enrolled = db.query_enrollment(student_id, session_details['c_id'])
        if not is_enrolled:
            scanned_id.value = f"\t\t\t{student_id}"
            scanned_name.value = f"\t\t\t{full_name}"
            scan_status.value = "\t\t\tERR: Not Enrolled"
            update_scanner_output_ui()
            
            if input_type != "scan":
                alert_snackbar("ERR: Student not enrolled in subject.")
            return

        has_record = db.query_attendance(student_id, session_details['c_id'], session_details['fin'])
        if has_record:
            scanned_id.value = f"\t\t\t{student_id}"
            scanned_name.value = f"\t\t\t{full_name}"
            scan_status.value = "\t\t\ttERR: Prior record Found"
            update_scanner_output_ui()
            
            if input_type != "scan":
                alert_snackbar("ERR: Prior record found.")
            return
        
        status = db.record_attendance(
                student_id, 
                session_details['c_id'], 
                session_details['type'], 
                session_details['bgn'], 
                session_details['fin']
            )
        scanned_id.value = f"\t\t\t{student_id}"
        scanned_name.value = f"\t\t\t{full_name}"
        scan_status.value = f"\t\t\tRecorded: {status.upper()}" if status != "error" else "ERROR recording"
        update_scanner_output_ui()
        alert_snackbar("SUCCESS: Attendance Recorded.")
            
    
    #* PAGE 3 COMPONENTS
    
    dt_attendance_log = ft.DataTable(
            align=ft.Alignment.TOP_CENTER,
            width=WIDTH, expand=True,
            border=ft.Border.all(2, ft.Colors.SURFACE_BRIGHT),
            horizontal_lines=ft.border.BorderSide(1, ft.Colors.SURFACE_BRIGHT),
            heading_row_color=ft.Colors.SURFACE_CONTAINER_LOW,
            columns=[
                ft.DataColumn(label=ft.Text("TIME")),
                ft.DataColumn(label=ft.Text("NAME")),
                ft.DataColumn(label=ft.Text("SECTION")),
                ft.DataColumn(label=ft.Text("STATUS")),
            ],
            rows=[],
        )
    
    def update_attendance_log():
        dt_attendance_log.rows.clear()
        
        rows = db.get_attendance_log(current_u_id)
        if rows:
            for r in rows:
                dt_attendance_log.rows.append(
                    ft.DataRow(cells=[
                            ft.DataCell(ft.Text(str(r['time']))),
                            ft.DataCell(ft.Text(r['student_name'])),
                            ft.DataCell(ft.Text(f"{r['course_id']} {r['year_level']}{r['section']}")),
                            ft.DataCell(ft.Text(r['status'])),
                        ]
                    )
                )
    
    
    #* PAGE 4 COMPONENTS
    
    section_options = []
    subject_options = []
    timeslot_options = []
    
    filter_date_field = ft.TextField(
            border_color=ft.Colors.SURFACE_BRIGHT,
            expand=1, height=50, border_radius=10,
            label=ft.Text("Date"), hint_text="yyyy/mm/dd",
        )
    filter_time_field = ft.TextField(
            border_color=ft.Colors.SURFACE_BRIGHT,
            expand=1, height=50, border_radius=10,
            label=ft.Text("Time"), hint_text="00:00",
        )
    filter_sect_dropdown = ft.Container(
            height=50,
            content=ft.Dropdown(
                expand=True,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                border_color=ft.Colors.SURFACE_BRIGHT,
                label=ft.Text("Section"),
                options=section_options,
                on_select=lambda e: update_subj_options(int(e.data))
            )
        )
    filter_subj_dropdown = ft.Container(
            height=50,
            content=ft.Dropdown(
                expand=True,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                border_color=ft.Colors.SURFACE_BRIGHT,
                label=ft.Text("Subject"),
                options=subject_options,
                # on_select=
            )
        )
    
    dt_class_log = ft.DataTable(
            align=ft.Alignment.TOP_CENTER,
            width=WIDTH, expand=True,
            border=ft.Border.all(2, ft.Colors.SURFACE_BRIGHT),
            horizontal_lines=ft.border.BorderSide(1, ft.Colors.SURFACE_BRIGHT),
            heading_row_color=ft.Colors.SURFACE_CONTAINER_LOW,
            columns=[
                ft.DataColumn(label=ft.Text("DATE")),
                ft.DataColumn(label=ft.Text("START TIME")),
                ft.DataColumn(label=ft.Text("SUBJECT CODE")),
                ft.DataColumn(label=ft.Text("SECTION")),
                ft.DataColumn(label=ft.Text("")),
            ],
            rows=[],
        )
    
    
    #* PAGE 5 COMPONENTS -- New session page
    
    nsession_details ={
        "subj": "",
        "b_id": -1
    }
    
    nsession_type_toggle = ft.SegmentedButton(
            width=WIDTH, height=30,
            selected=["regular"],
            segments=[
                ft.Segment(value="regular", label=ft.Text("Regular")),
                ft.Segment(value="makeup", label=ft.Text("Makeup"))
            ],
            on_change=lambda e: on_nsession_type_change(e)
        )
    nsession_sect_dropdown = ft.Container(
            height=50,
            content=ft.Dropdown(
                expand=True,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                border_color=ft.Colors.SURFACE_BRIGHT,
                label=ft.Text("Section"),
                options=section_options,
                on_select=lambda e: (
                    nsession_details.update({"subj": nsession_details['subj'],"b_id": e.data}),
                    update_subj_options(nsession_details['b_id']),
                    update_timeslot_options(nsession_details['subj'], nsession_details['b_id'])
                )
            )
        )
    nsession_subj_dropdown = ft.Container(
            height=50,
            content=ft.Dropdown(
                expand=True,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                border_color=ft.Colors.SURFACE_BRIGHT,
                label=ft.Text("Subject"),
                options=subject_options,
                on_select=lambda e: (
                    nsession_details.update({"subj": e.data, "b_id": nsession_details['b_id']}),
                    update_timeslot_options(nsession_details['subj'], nsession_details['b_id'])
                )
            )
        )
    nsession_bgn_field = ft.TextField(
            border_color=ft.Colors.SURFACE_BRIGHT,
            expand=1, height=50, border_radius=10,
            label=ft.Text("Start Time"), hint_text="e.g. 13:00",
        )
    nsession_fin_field = ft.TextField(
            border_color=ft.Colors.SURFACE_BRIGHT,
            expand=1, height=50, border_radius=10,
            label=ft.Text("End Time"), hint_text="e.g. 14:30",
        )
    nsession_timeslot_fields = ft.Container(
        ft.Row([
            nsession_bgn_field,
            nsession_fin_field
        ], spacing=20)
    )
    nsession_timeslot_dropdown = ft.Container(
            height=50,
            content=ft.Dropdown(
                expand=True,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                border_color=ft.Colors.SURFACE_BRIGHT,
                label=ft.Text("Timeslot"),
                options=timeslot_options,
                # on_select=
            )
        )
    nsession_timeslot_select = ft.Container(content=nsession_timeslot_dropdown)
    
    def update_sect_options():
        section_options.clear()
        
        blocks = db.get_sections(current_u_id)
        if not blocks:
            return
        
        for b in blocks:
            section_options.append(
                    ft.DropdownOption(
                        text=f"{b['crs_id']} {b['yr_lvl']}{b['sect']}",
                        key=b['blk_id'], data=b
                    )
                )
    
    def update_subj_options(block_id: int):
        subject_options.clear()
        
        subjects = db.get_subjects(current_u_id, block_id)
        if not subjects:
            return
        
        for s in subjects:
            subject_options.append(
                    ft.DropdownOption(
                        text=s, key=s
                    )
                )
            
    def update_timeslot_options(subject_id: str, block_id: int):
        timeslot_options.clear()
        
        timeslots = db.get_day_schedules(current_u_id, subject_id, block_id)
        if not timeslots:
            return
        
        time_now = datetime.now().time()
        for ts in timeslots:
            if time_now <= ts['sched_bgn']:
                timeslot_options.append(
                    ft.DropdownOption(
                        text=ts['label'],
                        data=ts
                    )
                )
    
    def on_nsession_type_change(e: ft.Event[ft.SegmentedButton]):
        slot_types = {
            "regular": nsession_timeslot_dropdown,
            "makeup":  nsession_timeslot_fields
        }
        selected = list(e.data)[0] if e.data else "regular"
        
        nsession_timeslot_select.content = slot_types.get(selected)

    def on_confirm_session():
        nonlocal camera_active_status, session_active
        
        is_makeup = nsession_timeslot_select.content == nsession_timeslot_fields

        if nsession_sect_dropdown.content.value is None or nsession_subj_dropdown.content.value is None:
            alert_snackbar("ERR [Section/Subject Dropdown]: No selection.")
            return
        
        if is_makeup:
            if nsession_bgn_field.value.strip() == "":
                nsession_bgn_field.value = datetime.now().strftime("%H:%M")
            
            if nsession_fin_field.value.strip() == "":
                alert_snackbar("ERR [End Time Field]: Input field empty.")
                return
            
            session_details['bgn'] = convert_time(nsession_bgn_field.value.strip())
            session_details['fin'] = convert_time(nsession_fin_field.value.strip())            
            
        else:
            if nsession_timeslot_dropdown.content.value is None:
                alert_snackbar("ERR [Timeslot Dropdown]: No selection.")
                return
            
            selected = next((o.data for o in timeslot_options if o.text == nsession_timeslot_dropdown.content.value), None)
            if not selected:
                alert_snackbar("ERR [Timeslot Dropdown]: Invalid timeslot.")
                return
            
            session_details['bgn'] = datetime.now().time()
            session_details['fin'] = selected['sched_fin']
        
        session_details['sect'] = nsession_sect_dropdown.content.text
        session_details['subj'] = nsession_details['subj']
        session_details['b_id'] = nsession_details['b_id']
        session_details['type'] = "makeup" if is_makeup else "regular"
        
        session_details['c_id'] = db.get_class_id(current_u_id, session_details['subj'], session_details['b_id'])

        setattr(nsession_bgn_field, 'value', "")
        setattr(nsession_fin_field, 'value', "")
        setattr(nsession_sect_dropdown.content, 'value', "Default")
        setattr(nsession_subj_dropdown.content, 'value', "Default")
        setattr(nsession_timeslot_dropdown.content, 'value', "Default")

        nsession_details['subj'] = ""
        nsession_details['b_id'] = -1

        camera_active_status = True
        session_active = True
        current_page.content = page_2
        update_session_ui_comp()
        
        start_scanner_thread()
        
    def update_session_ui_comp(revert_to_default: bool = False):
        if not revert_to_default:
            session_details_ui[0].value = f"+  SESSION:     {session_details['bgn'].strftime('%I:%M %p')} - {session_details['fin'].strftime('%I:%M %p')}"
            session_details_ui[1].value = f"+  SECTION:     {session_details['sect']}"
            session_details_ui[2].value = f"+  SUBJECT:     {session_details['subj']}"
            
            db_session_details[0].value = f"{session_details['bgn'].strftime('%I:%M %p')} - {session_details['fin'].strftime('%I:%M %p')}"
            db_session_details[1].value = f"{session_details['sect']}"
            db_session_details[2].value = f"{session_details['subj']}"
        
        else:
            session_details_ui[0].value = f"+  SESSION:     None"
            session_details_ui[1].value = f"+  SECTION:     None"
            session_details_ui[2].value = f"+  SUBJECT:     None"
            
            db_session_details[0].value = "No active session"
            db_session_details[1].value = "No active session"
            db_session_details[2].value = "No active session"

    
    #* PAGE 6 COMPONENTS -- Expand session
    # dt_session_log = ft.DataTable()
    
    
    
    
    #* PAGE SETUP; UI/UX
    
    # Login Page
    page_0 = ft.Container(
        bgcolor=ft.Colors.SURFACE_CONTAINER,
        width=420, height=300,
        align=ft.Alignment.CENTER,
        border_radius=20,
        content=ft.Column([
            ft.Text(value="USER LOGIN",
                    style=ft.TextStyle(
                        weight=ft.FontWeight.BOLD,
                        size=20,
                        color=ft.Colors.ON_SURFACE_VARIANT
                    )
                ),
            ft.Row([
                ft.Icon(ft.Icons.PERSON),
                userid_field
            ]),
            ft.Row([
                ft.Icon(ft.Icons.LOCK),
                passwd_field
            ]),
            ft.Button(
                    width=160, height=50,
                    align=ft.Alignment.BOTTOM_RIGHT,
                    content="LOG IN",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH
                    ),
                    on_click=lambda e: login(),
                ),
            ], align=ft.Alignment.TOP_LEFT, margin=30, spacing=20,
        )
    )
        
    # Dashboard Page
    page_1 = ft.Container(
        align=ft.Alignment.TOP_CENTER,
        margin=30,
        content=ft.Row([
            ft.Column([
                    ft.Container(
                        align=ft.Alignment.TOP_CENTER,
                        bgcolor=ft.Colors.SURFACE_CONTAINER,
                        expand=2, width=280,
                        border_radius=20,
                        content=ft.Column([
                                ft.Text(value="SCANNER STATUS",
                                        style=ft.TextStyle(
                                            weight=ft.FontWeight.BOLD,
                                            size=20,
                                            color=ft.Colors.ON_SURFACE_VARIANT
                                        )
                                    ),
                                ft.Row([
                                    ft.Icon(icon=ft.Icons.REMOVE_RED_EYE, size=14),
                                    cam_status_1
                                ]),
                                ft.Row([
                                    ft.Icon(icon=ft.Icons.CAMERA_ALT_OUTLINED, size=14),
                                    cam_status_2
                                ]),
                            ], margin=ft.Margin(20, 15, 20, 15)
                        )
                    ),
                    ft.Container(
                        align=ft.Alignment.TOP_CENTER,
                        bgcolor=ft.Colors.SURFACE_CONTAINER,
                        expand=3, width=280,
                        border_radius=20,
                        content=ft.Column([
                                ft.Text(value="SESSION INFO",
                                        style=ft.TextStyle(
                                            weight=ft.FontWeight.BOLD,
                                            size=24,
                                            color=ft.Colors.ON_SURFACE_VARIANT
                                        )
                                    ),
                                ft.Row([
                                    ft.Icon(icon=ft.Icons.TIMER, size=14),
                                    db_session_details[0]
                                ]),
                                ft.Row([
                                    ft.Icon(icon=ft.Icons.PERSON_2_OUTLINED, size=14),
                                    db_session_details[1]
                                ]),
                                ft.Row([
                                    ft.Icon(icon=ft.Icons.RECEIPT_ROUNDED, size=14),
                                    db_session_details[2]
                                ]),
                            ], margin=ft.Margin(20, 15, 20, 15)
                        )
                    ),
                    ft.Container(
                        align=ft.Alignment.TOP_CENTER,
                        bgcolor=ft.Colors.SURFACE_CONTAINER,
                        expand=4, width=280,
                        border_radius=20,
                        content=ft.Column([
                            ft.Text(value="RECENT ACTIVITY",
                                    style=ft.TextStyle(
                                        weight=ft.FontWeight.BOLD,
                                        size=20,
                                        color=ft.Colors.ON_SURFACE_VARIANT
                                    )
                                ),
                            recent_activity_column,
                            ], margin=ft.Margin(20, 15, 20, 15),
                        )
                    ),
                ], spacing=20, expand=2
            ),
            ft.Column([
                ft.Row([
                    user_greeting,
                    ft.IconButton(
                            icon = ft.Icons.LOGOUT,
                            align = ft.Alignment.CENTER_RIGHT,
                            style = ft.ButtonStyle(
                                    bgcolor = ft.Colors.SURFACE_CONTAINER_HIGHEST,
                                    elevation=30,
                            ),
                            on_click=lambda e: logout()
                        )
                    ], spacing=20, alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(),
                ft.Row([
                        date_today,
                        time_today,
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Row([
                        ft.Container(
                                align=ft.Alignment.TOP_CENTER,
                                bgcolor=ft.Colors.SURFACE_CONTAINER,
                                width=280, height= 200,
                                border_radius=20,
                            ),
                        ft.Container(
                                align=ft.Alignment.TOP_CENTER,
                                bgcolor=ft.Colors.SURFACE_CONTAINER,
                                width=280, height= 200,
                                border_radius=20,
                            ),
                        ft.Container(
                                align=ft.Alignment.TOP_CENTER,
                                bgcolor=ft.Colors.SURFACE_CONTAINER,
                                width=280, height= 200,
                                border_radius=20,
                            ),
                        ft.Container(
                                align=ft.Alignment.TOP_CENTER,
                                bgcolor=ft.Colors.SURFACE_CONTAINER,
                                width=280, height= 200,
                                border_radius=20,
                            ),
                    ], scroll=ft.ScrollMode.AUTO, spacing=20
                ),
                ft.Divider(),
                ft.Text(value="TODAY'S SCHEDULE",
                        style=ft.TextStyle(
                            weight=ft.FontWeight.BOLD,
                            size=28,
                            color=ft.Colors.ON_SURFACE_VARIANT
                        )
                    ),
                day_schedule_column,
                ], spacing=20, expand=7, scroll=ft.ScrollMode.AUTO
            ),
        ], spacing=30
        )
    )
    
    # Scanner Page
    page_2 = ft.Container(
        align=ft.Alignment.TOP_CENTER,
        margin=30,
        content=ft.Column([
                ft.Row([
                    ft.Column([
                        video_container,
                        manual_id_input
                        ], spacing=20, align=ft.Alignment.TOP_CENTER
                    ),
                    ft.Column([
                        ft.Container(
                            bgcolor=ft.Colors.SURFACE_CONTAINER,
                            width=410, height=180,
                            border_radius=20,
                            content=ft.Column([
                                ft.Row([
                                        ft.Text(value="SCHEDULE DETAILS",
                                            style=ft.TextStyle(
                                                weight=ft.FontWeight.BOLD,
                                                size=20,
                                                color=ft.Colors.ON_SURFACE_VARIANT
                                            )
                                        ),
                                        ft.Row([
                                            ft.IconButton(
                                                    icon = ft.Icons.CLASS_OUTLINED,
                                                    align = ft.Alignment.CENTER_RIGHT,
                                                    style = ft.ButtonStyle(
                                                        bgcolor = ft.Colors.SURFACE_CONTAINER_HIGHEST,
                                                        elevation=30,
                                                    ),
                                                    on_click=lambda e: (
                                                        kill_scanner_thread(),
                                                        new_session(),
                                                    ),
                                                ),
                                            ft.IconButton(
                                                    icon = ft.Icons.CANCEL_OUTLINED,
                                                    align = ft.Alignment.CENTER_RIGHT,
                                                    style = ft.ButtonStyle(
                                                        bgcolor = ft.Colors.SURFACE_CONTAINER_HIGHEST,
                                                        elevation=30,
                                                    ),
                                                    on_click=lambda e: cancel_current_session(),
                                                ), 
                                            ],
                                        )
                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                ),
                                session_details_ui[0],
                                session_details_ui[1],
                                session_details_ui[2],
                                ], align=ft.Alignment.TOP_LEFT, margin=ft.Margin(30, 20, 30, 20), spacing=10
                            ),
                        ),
                        ft.Container(
                            bgcolor=ft.Colors.SURFACE_CONTAINER,
                            width=410, height=285,
                            border_radius=20,
                            content=ft.Column([
                                ft.Text(value="SCANNER OUTPUT",
                                        style=ft.TextStyle(
                                            weight=ft.FontWeight.BOLD,
                                            size=20,
                                            color=ft.Colors.ON_SURFACE_VARIANT
                                        )
                                    ),
                                ft.Text(value="+  STUDENT ID #",
                                        style=ft.TextStyle(
                                            weight=ft.FontWeight.BOLD,
                                            size=14,
                                            color=ft.Colors.ON_SURFACE_VARIANT
                                        )
                                    ),
                                scanned_id,
                                ft.Text(value="+  STUDENT NAME",
                                        style=ft.TextStyle(
                                            weight=ft.FontWeight.BOLD,
                                            size=14,
                                            color=ft.Colors.ON_SURFACE_VARIANT
                                        )
                                    ),
                                scanned_name,
                                ft.Text(value="+  STATUS",
                                        style=ft.TextStyle(
                                            weight=ft.FontWeight.BOLD,
                                            size=14,
                                            color=ft.Colors.ON_SURFACE_VARIANT
                                        )
                                    ),
                                scan_status,
                                ], align=ft.Alignment.TOP_LEFT, margin=ft.Margin(30, 20, 30, 20), spacing=15
                            ),
                        ),
                    ], spacing=30)
                ], spacing=30),
            ], margin=20, spacing=30, align=ft.Alignment.TOP_CENTER,
        ),
    )
    
    # Attendance Log Page
    page_3 = ft.Container(
        align=ft.Alignment.TOP_CENTER,
        margin=30,
        content=ft.Column([
                dt_attendance_log,
            ], scroll=ft.ScrollMode.AUTO, expand=True,
        )
    )
    
    # Class List Page
    page_4 = ft.Container(
        align=ft.Alignment.TOP_CENTER,
        margin=30,
        content=ft.Row([
                ft.Container(
                    align=ft.Alignment.TOP_CENTER,
                    bgcolor=ft.Colors.SURFACE_CONTAINER,
                    expand=2, height=340,
                    border_radius=20,
                    content=ft.Column([
                            ft.Row([
                                ft.Text(value="FILTERS",
                                    style=ft.TextStyle(
                                        weight=ft.FontWeight.BOLD,
                                        size=20,
                                        color=ft.Colors.ON_SURFACE_VARIANT
                                    )),
                                ft.IconButton(
                                        icon=ft.Icons.RESTART_ALT,
                                        on_click=lambda e: (
                                            setattr(filter_date_field, 'value', ''),
                                            setattr(filter_time_field, 'value', ''),
                                            setattr(filter_sect_dropdown.content, 'value', None),
                                            setattr(filter_subj_dropdown.content, 'value', None),
                                        )
                                    )
                            ], spacing=180),
                            ft.Row([
                                filter_date_field,
                                filter_time_field,
                                ], spacing=20
                            ),
                            filter_sect_dropdown,
                            filter_subj_dropdown,
                            ft.Button(
                                expand=True, width=310, height=50,
                                align=ft.Alignment.BOTTOM_RIGHT,
                                content="APPLY FILTER",
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH
                                )
                            )
                        ], margin=20, spacing=15
                    )
                ),
                ft.Column([
                        dt_class_log,
                    ], scroll=ft.ScrollMode.AUTO, expand=5
                ),
            ], spacing=30
        )
    )
    
    # New session page
    page_5 = ft.Container(
        align=ft.Alignment.TOP_CENTER,
        width=WIDTH/3, height=HEIGHT/2,
        margin=75,
        border_radius=20,
        bgcolor=ft.Colors.SURFACE_CONTAINER,
        content=ft.Column([
                ft.Row([
                    ft.Text(value="NEW SESSION",
                            style=ft.TextStyle(
                                weight=ft.FontWeight.BOLD,
                                size=20,
                                color=ft.Colors.ON_SURFACE_VARIANT
                            )
                        ),
                    ft.Row([
                        ft.IconButton(
                                icon=ft.Icons.REFRESH_OUTLINED,
                                on_click=lambda e: (
                                        setattr(nsession_bgn_field, 'value', ''),
                                        setattr(nsession_fin_field, 'value', ''),
                                        setattr(nsession_sect_dropdown.content, 'value', None),
                                        setattr(nsession_subj_dropdown.content, 'value', None),
                                    )
                                ),
                        ft.IconButton(
                                icon=ft.Icons.CANCEL_OUTLINED,
                                on_click=lambda e: (
                                        start_scanner_thread() if all(session_details.values()) else None,
                                        setattr(current_page, "content", page_2),
                                    )
                                )
                            ]
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                nsession_type_toggle,
                nsession_sect_dropdown,
                nsession_subj_dropdown,
                nsession_timeslot_select,
                ft.Button(
                    width=WIDTH, height=50,
                    align=ft.Alignment.BOTTOM_RIGHT,
                    content="CONFIRM",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH
                    ),
                    on_click=lambda e: on_confirm_session()
                )
            ], margin=ft.Margin(30, 20, 30, 20), align=ft.Alignment.TOP_CENTER, 
        )
    )
    
    # TODO: Expanded previous sessions page
    # TODO: Expanded session analytics page
    
    
    
     #* THREADING FUNCTIONS

    # For updating date and time in dashboard
    def update_time(stop_event: threading.Event):
        while not stop_event.is_set():
            async def run_update():
                date_today.value = f"{datetime.now().strftime("%b %d, %Y || %A")}"
                time_today.value = f"{datetime.now().strftime("%I:%M %p")}"
                
                date_today.update()
                time_today.update()
            
            page.run_task(run_update)
            
            t.sleep(1/30)
    
    _dashb_time_stop_event = threading.Event()
    
    def start_dashb_time_thread(): # TODO: Add this function upon login success
        _dashb_time_stop_event.clear()
        threading.Thread(
            target=update_time,
            args=[_dashb_time_stop_event],
            daemon=True
        ).start()
    
    def kill_dashb_time_thread():
        _dashb_time_stop_event.set()
    

    # Switch for controlling camera thread
    _scanner_stop_event = threading.Event()

    # Start camera thread
    def start_scanner_thread():
        nonlocal camera_active
        
        if session_details['bgn'] == None or session_details['fin'] == None or session_details['subj'] == None or session_details['sect'] == None:
            return

        video_container.content = camera_preview    
        camera_active = True
        _scanner_stop_event.clear()  # Clear and reset threading
        threading.Thread(
            target=cv.capture_frames,
            args=(page, camera_preview, on_scan, _scanner_stop_event),
            daemon=True,
        ).start()

    # End thread
    def kill_scanner_thread():
        nonlocal camera_active
        
        video_container.content = None
        camera_active = False
        _scanner_stop_event.set()  # Signal the thread to stop
    
    
    #* Main Navigation Components
    
    def set_page(e: ft.Event[ft.NavigationBar]):
        i = e.control.selected_index
        if i == 0:
            start_dashb_time_thread()
            update_cam_status()
            update_recent_activity()
            kill_scanner_thread()
            current_page.content = page_1
        elif i == 1:
            kill_dashb_time_thread()
            if not camera_active and session_active:
                start_scanner_thread()
            current_page.content = page_2
        elif i == 2:
            kill_dashb_time_thread()
            kill_scanner_thread()
            update_attendance_log()
            current_page.content = page_3
        elif i == 3:
            kill_dashb_time_thread()
            kill_scanner_thread()
            current_page.content = page_4
            update_sect_options()
    
    # For navigation
    navbar = ft.NavigationBar(destinations=[
        ft.NavigationBarDestination(
                icon=ft.Icons.ANALYTICS,
                label="Dashboard"
            ),
        ft.NavigationBarDestination(
                icon=ft.Icons.CAMERA_ALT,
                label="ID Scanner"
            ),
        ft.NavigationBarDestination(
                icon=ft.Icons.ASSIGNMENT,
                label="Attendance Log"
            ),
        ft.NavigationBarDestination(
                icon=ft.Icons.CLASS_,
                label="Class List"
            ),
        ],
        on_change=lambda e: set_page(e),
        selected_index=0,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH
    )
    
    # Navbar and Page Containers (updateable)
    current_navi = ft.Container(content=None)
    current_page = ft.Container(content=page_0) # TODO: Revert to defaults after setup
    

    def close_app():
        try:
            kill_scanner_thread()
            if cv.camera:
                cv.camera.release()

        except Exception as e:
            print(e)
            
        
    page.add(
        # Changeable content
        current_navi,
        ft.SafeArea(
            align=ft.Alignment.TOP_CENTER,
            expand=True,
            
            # Changeable content
            content=current_page
        )
    )
    
    page.on_close = close_app



# Run Flet app
if __name__ == "__main__":
    ft.run(main)