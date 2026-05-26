# Module/Library imports
import flet as ft
import threading
import time as t
from datetime import datetime, time, date

# Custom files for handling
import dbhandler as db
# import handlers.cvhandler as cv


# Main structure; We gotta put it all here!!
def main(page: ft.Page):
    # Page settings
    page.title = "SASs: Smart Attendance System"
    page.theme_mode = ft.ThemeMode.DARK

    WIDTH, HEIGHT = 1280, 780

    page.window.resizable = False
    page.window.minimizable = False
    page.window.maximizable = False
    page.window.width = WIDTH
    page.window.height = HEIGHT

    page.window.min_height = HEIGHT
    page.window.min_width = WIDTH
    page.window.max_height = HEIGHT
    page.window.max_width = WIDTH

    # Convert strings into datetime objects
    def convert_time(time_str: str) -> time:
        format = "%H:%M"
        try:
            time = datetime.strptime(time_str, format).time()
            return time

        except ValueError as e:
            error_snackbar("ERROR: Invalid format.")
            return False

    def convert_date(date_str: str) -> date:
        format = "%Y/%m/%d"
        try:
            date = datetime.strptime(date_str, format).date()
            return date

        except ValueError as e:
            error_snackbar("ERROR: Invalid format.")
            return False

    # * VARIABLES FOR THE CURRENT USER (Instructor details)

    current_user_id: str = ""
    current_user_name: str = ""

    # * VARIABLES FOR LOGIN PAGE

    user_id_field = ft.TextField(
        border_color=ft.Colors.SURFACE_BRIGHT,
        width=315,
        height=50,
        border_radius=10,
        label=ft.Text("ID Number"),
    )
    password_field = ft.TextField(
        border_color=ft.Colors.SURFACE_BRIGHT,
        width=315,
        height=50,
        border_radius=10,
        label=ft.Text("Password"),
        password=True,
        on_submit=lambda e: login_user()
    )

    # * DYNAMIC VARIABLES FOR ATTENDANCE LOGGING

    schedule: dict = {
        "start":        None,
        "end":          None,
        "sub":          None,
        "sect":         None,
        "class_id":     None,
        "session_type": "regular"
    }
    schedule_selection: dict = {
        "start": None,
        "end": None,
        "sub": None,
        "sect": {}
    }
    schedule_details: list = [
        ft.Text(
            value=f"START OF SESSION:      {schedule["start"]}",
            style=ft.TextStyle(
                weight=ft.FontWeight.BOLD,
                size=15,
                color=ft.Colors.ON_SURFACE_VARIANT
            )
        ),
        ft.Text(
            value=f"END OF SESSION:      {schedule["end"]}",
            style=ft.TextStyle(
                weight=ft.FontWeight.BOLD,
                size=15,
                color=ft.Colors.ON_SURFACE_VARIANT
            )
        ),
        ft.Text(
            value=f"SUBJECT:      {schedule["sub"]}",
            style=ft.TextStyle(
                weight=ft.FontWeight.BOLD,
                size=15,
                color=ft.Colors.ON_SURFACE_VARIANT
            )
        ),
        ft.Text(
            value=f"SECTION:       {schedule["sect"]}",
            style=ft.TextStyle(
                weight=ft.FontWeight.BOLD,
                size=15,
                color=ft.Colors.ON_SURFACE_VARIANT
            )
        ),
    ]

    # * SCANNER PAGE VARIABLES
    # FIXME: Constant flickering of camera

    # Dynamic variables for Scanner
    scan_status = ft.Text(
        value="waiting for scan...",
        align=ft.Alignment.CENTER,
        style=ft.TextStyle(
            size=20,
            color=ft.Colors.SURFACE_BRIGHT
        )
    )
    scanned_name = ft.Text(
        value="waiting for scan...",
        align=ft.Alignment.CENTER,
        style=ft.TextStyle(
            size=20,
            color=ft.Colors.SURFACE_BRIGHT
        )
    )
    scanned_id = ft.Text(
        value="waiting for scan...",
        align=ft.Alignment.CENTER,
        style=ft.TextStyle(
            size=20,
            color=ft.Colors.SURFACE_BRIGHT
        )
    )
    manual_input_field = ft.TextField(
        label="",
        expand=True,
        height=40,
        border_color=ft.Colors.SURFACE_BRIGHT,
        on_submit=lambda e: manual_attendance(e)
    )

    # Camera/Video variables
    camera_preview = ft.Image(
        src="FletApplication/test.jpg",
        width=760,
        height=495,
        fit=ft.BoxFit.COVER,
    )
    camera_preview.src_base64 = ""
    video_container = ft.Container(
        content=camera_preview,
        margin=ft.Margin(0, 0, 0, 60),
        bgcolor=ft.Colors.SURFACE_CONTAINER,
        border_radius=30,
        width=760,
        height=495
    )

    # * FOR DATABASE RETRIEVED CONTENT

    # TODO: Add functionality to expand on class item
    selected_class: dict = {}

    # Database Tables
    dt_attendance = ft.DataTable(
        align=ft.Alignment.CENTER,
        width=WIDTH,
        expand=True,
        border=ft.Border.all(2, ft.Colors.SURFACE_BRIGHT),
        horizontal_lines=ft.border.BorderSide(1, ft.Colors.SURFACE_BRIGHT),
        heading_row_color=ft.Colors.SURFACE_CONTAINER_LOW,
        columns=[
            ft.DataColumn(ft.Text("DATE")),
            ft.DataColumn(ft.Text("TIME")),
            ft.DataColumn(ft.Text("NAME")),
            ft.DataColumn(ft.Text("SECTION")),
            ft.DataColumn(ft.Text("STATUS")),
        ],
        rows=[],
    )
    dt_classes = ft.DataTable(
        align=ft.Alignment.CENTER,
        width=860,
        expand=True,
        border=ft.Border.all(2, ft.Colors.SURFACE_BRIGHT),
        horizontal_lines=ft.border.BorderSide(1, ft.Colors.SURFACE_BRIGHT),
        heading_row_color=ft.Colors.SURFACE_CONTAINER_LOW,
        columns=[
            ft.DataColumn(ft.Text("DATE")),
            ft.DataColumn(ft.Text("START TIME")),
            ft.DataColumn(ft.Text("SUBJECT CODE")),
            ft.DataColumn(ft.Text("SECTION")),
            ft.DataColumn(ft.Text("")),
        ],
        rows=[],
    )
    # ADDED: DataTable for session-specific attendance
    dt_session = ft.DataTable(
        align=ft.Alignment.CENTER,
        expand=True,
        border=ft.Border.all(2, ft.Colors.SURFACE_BRIGHT),
        horizontal_lines=ft.border.BorderSide(1, ft.Colors.SURFACE_BRIGHT),
        heading_row_color=ft.Colors.SURFACE_CONTAINER_LOW,
        columns=[
            ft.DataColumn(ft.Text("NAME")),
            ft.DataColumn(ft.Text("STUDENT ID")),
            ft.DataColumn(ft.Text("TIME IN")),
            ft.DataColumn(ft.Text("STATUS")),
        ],
        rows=[],
    )
    # ADDED: Header labels
    session_info_labels: list = [
        ft.Text(value="DATE:      —", style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=15, color=ft.Colors.ON_SURFACE_VARIANT)),
        ft.Text(value="START TIME:      —", style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=15, color=ft.Colors.ON_SURFACE_VARIANT)),
        ft.Text(value="SUBJECT:      —", style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=15, color=ft.Colors.ON_SURFACE_VARIANT)),
        ft.Text(value="SECTION:      —", style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=15, color=ft.Colors.ON_SURFACE_VARIANT)),
        ft.Text(value="TYPE:      —", style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=15, color=ft.Colors.ON_SURFACE_VARIANT)),
    ]
    # * ATTENDANCE SHEETS CONTENT VARIABLES

    # TODO: Retrieve from database instead of manually listing
    # TODO: Retrieve schedule for specific section and subject
    # For dropdown options
    subject_options = []
    section_options = []
    timeslot_options = []

    filter_date_field = ft.TextField(
        border_color=ft.Colors.SURFACE_BRIGHT,
        width=140, height=50, border_radius=10,
        label=ft.Text("Date"), hint_text="yyyy/mm/dd",
    )
    filter_time_field = ft.TextField(
        border_color=ft.Colors.SURFACE_BRIGHT,
        width=140, height=50, border_radius=10,
        label=ft.Text("Time"), hint_text="00:00",
    )
    filter_section_dropdown = ft.Container(
        width=290, height=50,
        content=ft.Dropdown(
            expand=True,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
            border_color=ft.Colors.SURFACE_BRIGHT,
            label=ft.Text("Section"),
            options=section_options,
        )
    )
    filter_subject_dropdown = ft.Container(
        width=290, height=50,
        content=ft.Dropdown(
            expand=True,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
            border_color=ft.Colors.SURFACE_BRIGHT,
            label=ft.Text("Subject"),
            options=subject_options,
        )
    )
    session_start_field = ft.TextField(
        border_color=ft.Colors.SURFACE_BRIGHT,
        width=200,
        height=50,
        border_radius=10,
        label=ft.Text("Start Time"),
        hint_text="07:30",
    )
    session_end_field = ft.TextField(
        border_color=ft.Colors.SURFACE_BRIGHT,
        width=200,
        height=50,
        border_radius=10,
        label=ft.Text("End Time"),
        hint_text="09:30",
    )
    session_type_toggle = ft.SegmentedButton(
        width=420,
        height=30,
        margin=ft.Margin(0, 0, 0, 10),
        align=ft.Alignment.CENTER,
        allow_multiple_selection=False,
        allow_empty_selection=False,
        selected=["regular"],
        segments=[
            ft.Segment(value="regular", label=ft.Text("Regular")),
            ft.Segment(value="makeup", label=ft.Text("Makeup")),
        ],
        on_change=lambda e: on_session_type_change(e),
    )
    section_dropdown = ft.Container(
        width=420,
        height=50,
        content=ft.Dropdown(
            expand=True,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
            border_color=ft.Colors.SURFACE_BRIGHT,
            label=ft.Text("Section"),
            options=section_options,
            on_select=lambda e: on_section_select(e),
        )
    )
    subject_dropdown = ft.Container(
        width=420,
        height=50,
        content=ft.Dropdown(
            expand=True,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
            border_color=ft.Colors.SURFACE_BRIGHT,
            label=ft.Text("Subject"),
            options=subject_options,
            on_select=lambda e: on_subject_select(e)
        )
    )
    timeslot_dropdown = ft.Container(
        width=420,
        height=50,
        content=ft.Dropdown(
            expand=True,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
            border_color=ft.Colors.SURFACE_BRIGHT,
            label=ft.Text("Timeslot"),
            options=timeslot_options,
            on_select=lambda e: on_timeslot_select(e)
        )
    )
    manual_timeslots = ft.Container(
        ft.Row([
            session_start_field,
            session_end_field
        ], spacing=20),
    )
    timeslot_field = ft.Container(content=timeslot_dropdown)

    def error_snackbar(error_text: str):
        page.show_dialog(ft.SnackBar(ft.Text(error_text,
                                             color=ft.Colors.ON_SURFACE_VARIANT),
                                     bgcolor=ft.Colors.SURFACE_CONTAINER))

    # * LOGIN PAGE FUNCTIONS

    def clear_login_fields():
        user_id_field.value = ""
        password_field.value = ""

    def login_user():
        nonlocal current_user_id, current_user_name

        if user_id_field.value == "" or password_field.value == "":
            error_snackbar("ERROR: Empty fields found.")
            return

        userid: str = user_id_field.value
        passwd: str = password_field.value

        usernm = db.query_instructor_id(userid, passwd)
        if not usernm:
            error_snackbar("Incorrect USER ID or PASSWORD.")
            return
        else:
            clear_login_fields()

            current_user_id = userid
            current_user_name = usernm

            navigator.content = navbar
            current_page.content = page_1

    def logout_user():
        nonlocal current_user_id, current_user_name

        current_user_id = ""
        current_user_name = ""

        navigator.content = None
        current_page.content = page_0

    # * SCANNER PAGE FUNCTIONS
    # FIXME: Cater scanning to database changes

    # CV Logic for when ID template is detected
    def on_scan(ret_string: str, is_valid: bool):
        if not is_valid or not ret_string:
            return
        process_attendance(ret_string)

    # Recording of attendance through text fields
    def manual_attendance(e):
        student_id = manual_input_field.value.strip()
        if not student_id:
            return
        manual_input_field.value = ""
        manual_input_field.update()
        process_attendance(student_id)

    # Shared attendance logic for both scan and manual
    def process_attendance(student_id: str):
        if schedule['start'] is None or schedule['sub'] is None or schedule['sect'] is None:
            error_snackbar("ERROR: No active session.")
            return

        # check student exists
        full_name = db.query_student_id(student_id)
        if not full_name:
            scanned_id.value   = student_id
            scanned_name.value = "NOT FOUND"
            scan_status.value  = "Invalid ID"
            page.update()
            return

        # check enrollment
        enrolled = db.query_subject_enrollment(student_id, schedule['sub'], current_user_id)
        if not enrolled:
            scanned_id.value   = student_id
            scanned_name.value = full_name
            scan_status.value  = "Not Enrolled"
            page.update()
            return

        # check duplicate
        today = date.today()
        already = db.query_attendance(student_id, schedule['class_id'], today, schedule['start'])
        if already:
            scanned_id.value   = student_id
            scanned_name.value = full_name
            scan_status.value  = "Already Recorded"
            page.update()
            return

        # record attendance
        status = db.record_attendance(
            student_id, schedule['class_id'],
            today, schedule['start'], schedule['end'],
            schedule.get('session_type', 'regular')
        )

        scanned_id.value   = student_id
        scanned_name.value = full_name
        scan_status.value  = f"Recorded: {status.upper()}" if status != "error" else "ERROR recording"
        page.update()

    # * CAMERA THREAD FUNCTIONS

    # Switch for controlling camera thread
    _scanner_stop_event = threading.Event()

    # Start camera thread
    def start_scanner_thread():
        if schedule['start'] == None or schedule['end'] == None or schedule['sub'] == None or schedule['sect'] == None:
            return

        _scanner_stop_event.clear()  # Clear and reset threading
        threading.Thread(
            target=cv.capture_frames,
            args=(page, camera_preview, on_scan, _scanner_stop_event),
            daemon=True,
        ).start()

    # End thread
    def kill_scanner_thread():
        _scanner_stop_event.set()  # Signal the thread to stop

    # Update displayed schedule in scanner page
    def update_schedule_values():
        schedule_details[0].value = f"START OF SESSION:      {schedule['start']}"
        schedule_details[1].value = f"END OF SESSION:      {schedule['end']}"
        schedule_details[2].value = f"SUBJECT:      {schedule['sub']}"
        schedule_details[3].value = f"SECTION:      {schedule['sect']}"

        page.update()

    # * FUNCTIONS INVOLVING DATABASE RETRIEVALS
    # FIXME: Cater retrievals to database changes

    def update_attendance_log():
        rows = db.get_attendance_log(current_user_id)
        dt_attendance.rows = []
        if rows:
            for r in rows:
                dt_attendance.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(r.get("date", "")))),
                    ft.DataCell(ft.Text(str(r.get("time", "")))),
                    ft.DataCell(ft.Text(r.get("student_name", ""))),
                    ft.DataCell(ft.Text(f"{r.get('course_id','')} {r.get('year_level','')}{r.get('section','')}")),
                    ft.DataCell(ft.Text(r.get("status", ""))),
                ]))
        page.update()

    def update_class_list():    
        rows = db.get_class_list(current_user_id)
        dt_classes.rows = []
        if rows:
            for r in rows:
                # ADDED: Per-row button
                row_data = r
                btn = ft.IconButton(
                    icon=ft.Icons.ARROW_OUTWARD,
                    on_click=lambda e, d=row_data: expand_class_item(d)
                )
                dt_classes.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(r.get("date", "")))),
                    ft.DataCell(ft.Text(str(r.get("session_start", "")))),
                    ft.DataCell(ft.Text(r.get("subject_id", ""))),
                    ft.DataCell(ft.Text(f"{r.get('course_id','')} {r.get('year_level','')}{r.get('section','')}")),
                    ft.DataCell(btn),
                ]))
        page.update()

    # ADDED: Populates the dashboard with today's schedules for the logged-in instructor
    def update_dashboard():
        schedules = db.get_instructor_all_schedules(current_user_id)
        schedule_col = page_4.controls[2]  # the ft.Column inside page_4
        schedule_col.controls = []

        if not schedules:
            schedule_col.controls.append(
                ft.Text("No schedules found.", color=ft.Colors.ON_SURFACE_VARIANT)
            )
        else:
            today_str = datetime.now().strftime("%A").lower()
            for s in schedules:
                is_today = s.get("day", "").lower() == today_str
                schedule_col.controls.append(
                    ft.Container(
                        bgcolor=ft.Colors.SURFACE_CONTAINER if not is_today else ft.Colors.PRIMARY_CONTAINER,
                        border_radius=15,
                        padding=15,
                        content=ft.Row([
                            ft.Column([
                                ft.Text(f"{s.get('subject_id','')} — {s.get('subject_title','')}",
                                        style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=15,
                                                           color=ft.Colors.ON_SURFACE_VARIANT)),
                                ft.Text(f"{s.get('course','')} {s.get('year','')}{s.get('section','')}  |  {s.get('day','').capitalize()}  |  {s.get('label','')}",
                                        style=ft.TextStyle(size=13, color=ft.Colors.ON_SURFACE_VARIANT)),
                            ], spacing=4),
                        ])
                    )
                )
        page.update()

    # TODO: Add filtering and sorting for class list
    def filter_class_list():
        # ADDED: Reads filter panel fields and queries db with optional filters
        filter_date   = convert_date(filter_date_field.value)   if filter_date_field.value.strip()   else None
        filter_start  = convert_time(filter_time_field.value)   if filter_time_field.value.strip()   else None
        filter_subj   = filter_subject_dropdown.content.value   if filter_subject_dropdown.content.value not in (None, "Default") else None
        filter_sect   = next((o.data for o in section_options if o.text == filter_section_dropdown.content.value), None)

        rows = db.get_class_list(
            current_user_id,
            subject_id   = filter_subj,
            session_date = filter_date,
            session_start = filter_start,
            section      = filter_sect,
        )
        dt_classes.rows = []
        if rows:
            for r in rows:
                row_data = r
                btn = ft.IconButton(
                    icon=ft.Icons.ARROW_OUTWARD,
                    on_click=lambda e, d=row_data: expand_class_item(d)
                )
                dt_classes.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(r.get("date", "")))),
                    ft.DataCell(ft.Text(str(r.get("session_start", "")))),
                    ft.DataCell(ft.Text(r.get("subject_id", ""))),
                    ft.DataCell(ft.Text(f"{r.get('course_id','')} {r.get('year_level','')}{r.get('section','')}")),
                    ft.DataCell(btn),
                ]))
        page.update()

    # TODO: Expand and view specific class items
    def expand_class_item(row_data: dict):
        # ADDED: Loads session details and attendance into page_6 then navigates to it
        nonlocal selected_class
        selected_class = row_data

        subject_id    = row_data.get("subject_id", "")
        session_date  = row_data.get("date")
        session_start = row_data.get("session_start")
        course_id     = row_data.get("course_id", "")
        year_level    = row_data.get("year_level", "")
        section       = row_data.get("section", "")
        session_type  = row_data.get("session_type", "regular")

        session_info_labels[0].value = f"DATE:      {session_date}"
        session_info_labels[1].value = f"START TIME:      {session_start}"
        session_info_labels[2].value = f"SUBJECT:      {subject_id}"
        session_info_labels[3].value = f"SECTION:      {course_id} {year_level}{section}"
        session_info_labels[4].value = f"TYPE:      {session_type.upper()}"

        dt_session.rows = []
        rows = db.get_session_attendance(
            current_user_id, subject_id, session_date, session_start
        )
        if rows:
            for r in rows:
                dt_session.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(r.get("student_name", ""))),
                    ft.DataCell(ft.Text(str(r.get("student_id", "")))),
                    ft.DataCell(ft.Text(str(r.get("time_in", "")))),
                    ft.DataCell(ft.Text(r.get("status", ""))),
                ]))

        current_page.content = page_6
        page.update()

    def update_sections_list():
        section_options.clear()

        blocks = db.get_instructor_sections(current_user_id)
        if not blocks:
            page.update()
            return

        # FIXME: Stored as string,
        for block in blocks:
            section_options.append(
                ft.DropdownOption(
                    text=f"{block['course']} {block['year']}{block['section']}",
                    data=block
                )
            )
        page.update()

    def update_subjects_list(section: dict = None):
        subject_options.clear()

        subjects = db.get_instructor_subjects(current_user_id, section)
        if not subjects:
            page.update()
            return

        for subject in subjects:
            subject_options.append(
                ft.DropdownOption(text=subject, key=subject)
            )
        page.update()

    def update_schedules_list():
        timeslot_options.clear()

        timeslots = db.get_instructor_schedules(current_user_id, schedule_selection['sub'], schedule_selection['sect'])
        if not timeslots:
            page.update()
            return

        for slot in timeslots:
            timeslot_options.append(
                ft.DropdownOption(
                    text=slot['label'],
                    data={
                        "start":    slot['start'],
                        "end":      slot['end'],
                        "class_id": slot.get('class_id')
                    }
                )
            )
        page.update()

    # * FUNCTIONS FOR CREATING NEW SESSIONS

    # New session based on current schedule
    def quick_add_session():
        # ADDED: Opens new session page
        update_sections_list()
        current_page.content = page_5
        page.update()

    # New Sheet button
    def new_session():
        update_sections_list()

        current_page.content = page_5

    # For session_type_toggle
    def on_session_type_change(e):
        slot_types = {
            "regular": timeslot_dropdown,
            "makeup":  manual_timeslots
        }
        selected = list(e.data)[0] if e.data else "regular"
        timeslot_field.content = slot_types.get(selected, timeslot_dropdown)
        timeslot_field.update()

        # ADDED: For makeup classes, sections are irrelevant so we update subjects list with no section filter. For regular classes, we update based on selected section (if any)
        if selected == "makeup":
            update_subjects_list(section=None)
        else:
            update_subjects_list(section=schedule_selection.get('sect') or None)

    # Clear attendance sheet's current selection
    def clear_sheet_values():
        if timeslot_field.content == timeslot_dropdown:
            timeslot_dropdown.content.value = "Default"
        else:
            session_start_field.value = ""
            session_end_field.value = ""
        subject_dropdown.content.value = "Default"
        section_dropdown.content.value = "Default"

    # Refresh selection
    def refresh_sheet():
        clear_sheet_values()

    # Cancel selection
    def cancel_new_sheet():
        current_page.content = page_3
        clear_sheet_values()

    # Select section
    def on_section_select(e: ft.ControlEvent):
        sect_dict = next((o.data for o in section_options if o.text == e.data), e.data)

        schedule_selection['sect'] = sect_dict
        update_subjects_list(sect_dict)
        update_schedules_list()

    # Select subject
    def on_subject_select(e: ft.ControlEvent):
        schedule_selection['sub'] = e.data
        update_schedules_list()

    # Select timeslot
    def on_timeslot_select(e: ft.ControlEvent):
        if section_dropdown.content.value == None or subject_dropdown.content.value == None:
            error_snackbar("Please select Section and Subject first.")
            return

        selected = next((o.data for o in timeslot_options if o.text == e.data), None)
        if selected:
            schedule_selection['start']    = selected['start']
            schedule_selection['end']      = selected['end']
            schedule_selection['class_id'] = selected.get('class_id')

    # Confirm new schedule
    def confirm_schedule():
        is_makeup = timeslot_field.content == manual_timeslots

        if subject_dropdown.content.value is None or section_dropdown.content.value is None:
            error_snackbar("ERROR: Empty fields found.")
            return

        if is_makeup:
            # ADDED: Auto-fill session_start with current time if left blank
            if session_start_field.value.strip() == "":
                session_start_field.value = datetime.now().strftime("%H:%M")
                session_start_field.update()

            if session_end_field.value == "":
                error_snackbar("ERROR: Please enter an end time.")
                return
            if convert_time(session_start_field.value) is False or convert_time(session_end_field.value) is False:
                return
            schedule['start'] = convert_time(session_start_field.value)
            schedule['end']   = convert_time(session_end_field.value)
        else:
            if timeslot_dropdown.content.value is None:
                error_snackbar("ERROR: Please select a timeslot.")
                return
            selected = next((o.data for o in timeslot_options if o.text == timeslot_dropdown.content.value), None)
            if not selected:
                error_snackbar("ERROR: Invalid timeslot.")
                return
            # ADDED: Auto-fill session_start with current time when creating a regular session
            schedule['start'] = datetime.now().time()
            schedule['end']   = selected['end']

        schedule['sub']          = subject_dropdown.content.value
        schedule['sect']         = section_dropdown.content.value
        schedule['session_type'] = "makeup" if is_makeup else "regular"
        schedule['class_id']     = schedule_selection.get('class_id') if not is_makeup else None

        clear_sheet_values()
        current_page.content = page_3
        page.update()

    # * APPLICATION PAGE SETUPS

    # Navigation buttons
    def set_page(e):
        i = e.control.selected_index
        if i == 0:
            start_scanner_thread()
            current_page.content = page_1
            update_schedule_values()
        elif i == 1:
            kill_scanner_thread()
            current_page.content = page_2
            update_attendance_log()
        elif i == 2:
            kill_scanner_thread()
            current_page.content = page_3
            update_class_list()
        elif i == 3:
            kill_scanner_thread()
            current_page.content = page_4
            update_dashboard()
        page.update()

    # Login page
    page_0 = ft.Container(
        bgcolor=ft.Colors.SURFACE_CONTAINER,
        border_radius=20,
        align=ft.Alignment.CENTER,
        width=440,
        height=360,
        content=ft.Column([
            ft.Text(value="USER LOGIN",
                    style=ft.TextStyle(
                        weight=ft.FontWeight.BOLD,
                        size=20,
                        color=ft.Colors.ON_SURFACE_VARIANT
                    )),
            ft.Row([
                ft.Icon(ft.Icons.PERSON),
                user_id_field,
            ]),
            ft.Row([
                ft.Icon(ft.Icons.LOCK),
                password_field,
            ]),
            ft.Button(
                # icon = ft.Icons.KEY,
                content="LOG IN",
                width=160,
                height=50,
                align=ft.Alignment.BOTTOM_RIGHT,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=10),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                    elevation=10
                ),
                on_click=lambda e: login_user()
            ),
        ], align=ft.Alignment.TOP_LEFT, margin=ft.Margin(45, 45, 45, 45), spacing=30)
    )

    # ID Scanner page
    page_1 = ft.Container(
        ft.Column([
            ft.Row([
                ft.Container(
                    align=ft.Alignment.TOP_CENTER,
                    alignment=ft.Alignment.CENTER,
                    width=WIDTH - 150,
                    height=70,
                    bgcolor=ft.Colors.SURFACE_CONTAINER,
                    border_radius=20,
                    content=ft.Row([
                        schedule_details[0],
                        schedule_details[1],
                        schedule_details[2],
                        schedule_details[3],
                    ], spacing=90, alignment=ft.CrossAxisAlignment.CENTER)
                ),
                ft.IconButton(
                    icon=ft.Icons.CLASS_OUTLINED,
                    align=ft.Alignment.CENTER_LEFT,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH
                    ),
                    on_click=lambda e: quick_add_session()
                ),
            ], spacing=25),
            ft.Row([
                video_container,
                ft.Container(
                    width=410,
                    height=580,
                    content=ft.Container(
                        ft.Column([
                            ft.Text(
                                value="STUDENT INFORMATION",
                                align=ft.Alignment.CENTER,
                                style=ft.TextStyle(
                                    weight=ft.FontWeight.BOLD,
                                    size=25,
                                    color=ft.Colors.ON_SURFACE_VARIANT
                                )
                            ),
                            ft.Container(
                                bgcolor=ft.Colors.SURFACE_CONTAINER,
                                border_radius=30,
                                width=410,
                                height=200,
                                content=ft.Column([
                                    ft.Text(
                                        value="STUDENT NAME",
                                        align=ft.Alignment.CENTER,
                                        style=ft.TextStyle(
                                            weight=ft.FontWeight.BOLD,
                                            size=22,
                                            color=ft.Colors.ON_SURFACE_VARIANT
                                        )
                                    ),
                                    scanned_name,

                                    ft.Text(
                                        margin=ft.Margin(0, 30, 0, 0),
                                        value="STUDENT ID",
                                        align=ft.Alignment.CENTER,
                                        style=ft.TextStyle(
                                            weight=ft.FontWeight.BOLD,
                                            size=22,
                                            color=ft.Colors.ON_SURFACE_VARIANT
                                        )
                                    ),
                                    scanned_id,
                                ], spacing=-3, alignment=ft.MainAxisAlignment.CENTER),
                            ),
                            ft.Container(
                                bgcolor=ft.Colors.SURFACE_CONTAINER,
                                border_radius=30,
                                width=410,
                                height=100,
                                content=ft.Column([
                                    ft.Text(
                                        value="SCAN STATUS",
                                        align=ft.Alignment.CENTER,
                                        style=ft.TextStyle(
                                            weight=ft.FontWeight.BOLD,
                                            size=22,
                                            color=ft.Colors.ON_SURFACE_VARIANT
                                        )
                                    ),
                                    scan_status
                                ], spacing=-3, alignment=ft.MainAxisAlignment.CENTER),
                            ),

                            ft.Container(
                                width = 410,
                                height = 100,
                                content = ft.Column([
                                    ft.Text(
                                        value = "Manual ID Input: ",
                                        style = ft.TextStyle(
                                        size = 15,
                                        color = ft.Colors.ON_SURFACE_VARIANT
                                    )),
                                    manual_input_field
                                ], margin = ft.Margin(20, 10, 20, 10), alignment = ft.MainAxisAlignment.CENTER)
                            )
                        ], spacing=20)
                    )
                )
            ], spacing=30, vertical_alignment=ft.CrossAxisAlignment.START, align=ft.Alignment.CENTER)
        ], margin=ft.Margin(30, 10, 30, 30), spacing=30, align=ft.Alignment.CENTER, )
    )

    # Attendance Log page
    page_2 = ft.Container(
        content=ft.Column([
            dt_attendance,
        ], scroll=ft.ScrollMode.AUTO, expand=2),
        margin=20,
        alignment=ft.Alignment.TOP_CENTER
    )

    # Class List page
    page_3 = ft.Column([
            ft.Row([
                ft.Container(
                    bgcolor=ft.Colors.SURFACE_CONTAINER,
                    border_radius=30,
                    width=330,
                    height=360,
                    content=ft.Column([  
                        ft.Row([
                            ft.Text(value="FILTERS",
                                    style=ft.TextStyle(
                                        weight=ft.FontWeight.BOLD,
                                        size=20,
                                        color=ft.Colors.ON_SURFACE_VARIANT
                                    )),
                            # ADDED: Reset button
                            ft.IconButton(
                                icon=ft.Icons.RESTART_ALT,
                                on_click=lambda e: (
                                    setattr(filter_date_field, 'value', ''),
                                    setattr(filter_time_field, 'value', ''),
                                    setattr(filter_section_dropdown.content, 'value', None),
                                    setattr(filter_subject_dropdown.content, 'value', None),
                                    update_class_list(),
                                    page.update()
                                )
                            )
                        ], spacing=180),
                        ft.Row([filter_date_field, filter_time_field]),
                        filter_section_dropdown,
                        filter_subject_dropdown,
                        ft.Button(
                            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                            width=290,
                            height=50,
                            content=ft.Text("CONFIRM"),
                            on_click=lambda e: filter_class_list(),
                        ),
                    ], margin=20, spacing=20),         
                ),
                ft.Column([
                    ft.Button(
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                        width=250,
                        height=40,
                        content=ft.Text("NEW SESSION"),
                        on_click=lambda e: new_session(),
                        align=ft.Alignment.TOP_RIGHT
                    ),
                    dt_classes
                ], spacing=20, scroll=ft.ScrollMode.AUTO, expand=2)
            ],
                vertical_alignment=ft.CrossAxisAlignment.START,
                margin=20,
                spacing=30,
            )],
        )

    # TODO: Dashboard page
    # ADDED: Summary dashboard showing today's schedule pulled from db
    page_4 = ft.Column([
        ft.Text(
            value="DASHBOARD",
            style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=25, color=ft.Colors.ON_SURFACE_VARIANT)
        ),
        ft.Text(
            value="Today's Schedule",
            style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=18, color=ft.Colors.ON_SURFACE_VARIANT)
        ),
        ft.Column(
            controls=[],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=10,
        )
    ], margin=ft.Margin(30, 20, 30, 20), spacing=15)


    # New sheet page
    page_5 = ft.Column([
        ft.Row([
            ft.Text(value="NEW SESSION",
                    style=ft.TextStyle(
                        weight=ft.FontWeight.BOLD,
                        size=25,
                        color=ft.Colors.ON_SURFACE_VARIANT
                    ), margin=ft.Margin(0, 0, 200, 0)),
            ft.IconButton(
                icon=ft.Icons.REFRESH_OUTLINED,
                icon_size=28,
                on_click=lambda e: refresh_sheet()
            ),
            ft.IconButton(
                icon=ft.Icons.CANCEL_OUTLINED,
                icon_size=28,
                on_click=lambda e: cancel_new_sheet()
            )
        ], alignment=ft.CrossAxisAlignment.CENTER),
        ft.Container(
            bgcolor=ft.Colors.SURFACE_CONTAINER,
            border_radius=20,
            width=480,
            height=370,
            content=ft.Column([
                session_type_toggle,
                section_dropdown,
                subject_dropdown,
                timeslot_field,
                ft.Button(
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                    width=240,
                    height=50,
                    content=ft.Text("CREATE"),
                    margin=ft.Margin(240, 0, 0, 0),
                    on_click=lambda e: confirm_schedule()
                )
            ], alignment=ft.Alignment.TOP_CENTER, margin=30, spacing=20)
        ), ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        margin=ft.Margin(0, 60, 0, 0), spacing=20)

    # TODO: Class item page
    # ADDED: Session detail view
    page_6 = ft.Column([
        ft.Row([
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK_OUTLINED,
                icon_size=28,
                tooltip="Back to Class List",
                on_click=lambda e: (
                    setattr(current_page, 'content', page_3),
                    update_class_list(),
                    page.update()
                )
            ),
            ft.Text(
                value="SESSION DETAILS",
                style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=25, color=ft.Colors.ON_SURFACE_VARIANT)
            ),
        ], spacing=15),
        ft.Container(
            bgcolor=ft.Colors.SURFACE_CONTAINER,
            border_radius=20,
            width=860,
            height=80,
            content=ft.Row([
                session_info_labels[0],
                session_info_labels[1],
                session_info_labels[2],
                session_info_labels[3],
                session_info_labels[4],
            ], spacing=40, alignment=ft.CrossAxisAlignment.CENTER)
        ),
        ft.Column([dt_session], scroll=ft.ScrollMode.AUTO, expand=True),
    ], margin=ft.Margin(20, 20, 20, 20), spacing=20)

    # For navigation
    navbar = ft.NavigationBar(destinations=[
        ft.NavigationBarDestination(
            icon=ft.Icons.IMAGE,
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
        ft.NavigationBarDestination(
            icon=ft.Icons.ANALYTICS,
            label="Dashboard"
        ), ],
        on_change=lambda e: set_page(e),
        selected_index=0,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH
    )

    # Navbar and Page Container
    navigator = ft.Container(content=None)
    current_page = ft.Container(content=page_0)

    # Release camera before closing application
    def close_app(e):
        try:
            kill_scanner_thread()
            if cv.camera:
                cv.camera.release()

        except Exception as e:
            print(e)

    page.add(
        navigator,
        ft.SafeArea(
            align=ft.Alignment.TOP_CENTER,
            expand=True,

            # Changeable content
            content=current_page
        )
    )
    page.update()

    page.on_close = close_app


# Run Flet app (Flutter my beloved!!)
if __name__ == "__main__":
    ft.run(main)