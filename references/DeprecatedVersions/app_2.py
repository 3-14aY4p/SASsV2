# Module/Library imports
from cmath import exp
import flet as ft
import threading
import time as t
from datetime import datetime, time, date

# Custom files for handling
import handlers.dbhandler as db
import handlers.cvhandler as cv


# Main structure; We gotta put it all here!!
def main(page: ft.Page):
    # Page settings
    page.title = "SASs: Smart Attendance System"
    page.theme_mode = ft.ThemeMode.DARK

    WIDTH, HEIGHT = 1280, 780

    page.window_resizable = False
    page.window.minimizable = False
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
            page.show_dialog(
                ft.SnackBar(ft.Text("Please enter the correct format.", color=ft.Colors.ON_SURFACE_VARIANT),
                            bgcolor=ft.Colors.SURFACE_CONTAINER))
            return False

    def convert_date(date_str: str) -> date:
        format = "%Y/%m/%d"
        try:
            date = datetime.strptime(date_str, format).date()
            return date

        except ValueError as e:
            page.show_dialog(
                ft.SnackBar(ft.Text("Please enter the correct format.", color=ft.Colors.ON_SURFACE_VARIANT),
                            bgcolor=ft.Colors.SURFACE_CONTAINER))
            return False

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

    # Dynamic variables for Attendance Logging
    schedule = {
        "start": None,
        "end": None,
        "sub": None,
        "prof": None,
        'prof_id': None,
    }
    schedule_details = [
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
            value=f"INSTRUCTOR:       {schedule["prof"]}",
            style=ft.TextStyle(
                weight=ft.FontWeight.BOLD,
                size=15,
                color=ft.Colors.ON_SURFACE_VARIANT
            )
        ),
    ]

    # FIXME: Camera Vision stuff; still broken; constant flickering
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

    # CV Logic for when ID template is detected
    def on_scan(ret_string: str, is_valid: bool):
        if not all(schedule.values()):
            scan_status.value = "Please create a schedule first!"
            scan_status.style.color = ft.Colors.RED
            page.update()

            return

        if is_valid:
            student = db.query_student_id(ret_string)

            if student.get('status'):
                scan_status.value = "Scanning ID..."
                scan_status.style.color = ft.Colors.GREEN
                scanned_name.value = student['name']
                scanned_name.style.color = ft.Colors.GREEN
                scanned_id.value = ret_string
                scanned_id.style.color = ft.Colors.GREEN

                if db.query_subject_enrollment(ret_string, schedule['sub'], schedule['prof_id']):
                    if db.query_attendance(ret_string, schedule['sub'], datetime.now().date(), schedule['start']):
                        scan_status.value = "Previous attendance record found!"
                        scan_status.style.color = ft.Colors.RED
                    else:
                        scan_status.value = "Attendance successfully recorded!"
                        scan_status.style.color = ft.Colors.GREEN
                        db.record_attendance(ret_string, schedule['sub'], schedule['prof_id'], schedule['session_type'],
                                             schedule['start'], schedule['end'])
                        page.show_dialog(ft.SnackBar(
                            ft.Text("Attendance successfully recorded!", color=ft.Colors.ON_SURFACE_VARIANT),
                            bgcolor=ft.Colors.SURFACE_CONTAINER))
                else:
                    scan_status.value = "Student not enrolled in class!"
                    scan_status.style.color = ft.Colors.RED
        else:
            scan_status.value = "Waiting for scan..."
            scan_status.style.color = ft.Colors.SURFACE_BRIGHT
            scanned_name.value = "Waiting for scan..."
            scanned_name.style.color = ft.Colors.SURFACE_BRIGHT
            scanned_id.value = "Waiting for scan..."
            scanned_id.style.color = ft.Colors.SURFACE_BRIGHT

        page.update()

        # Handle manual recording of attendance through text fields

    def manual_attendance(e: str):
        if not all(schedule.values()):
            page.show_dialog(ft.SnackBar(ft.Text("Please create schedule first!", color=ft.Colors.ON_SURFACE_VARIANT),
                                         bgcolor=ft.Colors.SURFACE_CONTAINER))
            return

        student = db.query_student_id(e.data)

        if student.get('status'):
            if db.query_subject_enrollment(e.data, schedule['sub'], schedule['prof_id']):
                if not db.query_attendance(e.data, schedule['sub'], datetime.now().date(), schedule['start']):
                    db.record_attendance(e.data, schedule['sub'], schedule['prof_id'], schedule['session_type'],
                                         schedule['start'], schedule['end'])
                    page.show_dialog(
                        ft.SnackBar(ft.Text("Attendance successfully recorded!", color=ft.Colors.ON_SURFACE_VARIANT),
                                    bgcolor=ft.Colors.SURFACE_CONTAINER))
                    manual_input_field.value = ""
                else:
                    page.show_dialog(
                        ft.SnackBar(ft.Text("Attendance already recorded.", color=ft.Colors.ON_SURFACE_VARIANT),
                                    bgcolor=ft.Colors.SURFACE_CONTAINER))
            else:
                page.show_dialog(
                    ft.SnackBar(ft.Text("Student not enrolled in class.", color=ft.Colors.ON_SURFACE_VARIANT),
                                bgcolor=ft.Colors.SURFACE_CONTAINER))
        else:
            page.show_dialog(ft.SnackBar(ft.Text("Invalid ID.", color=ft.Colors.ON_SURFACE_VARIANT),
                                         bgcolor=ft.Colors.SURFACE_CONTAINER))

        page.update()

    # Start camera thread
    threading.Thread(
        target=cv.capture_frames,
        args=(page, camera_preview, on_scan),
        daemon=True,
    ).start()

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
            ft.DataColumn(ft.Text("COURSE, YEAR, & SECTION")),
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
            ft.DataColumn(ft.Text("INSTRUCTOR")),
            ft.DataColumn(ft.Text("")),
        ],
        rows=[],
    )

    # TODO: Add functionality to expand on class item
    expand_item_button = ft.IconButton(
        icon=ft.Icons.ARROW_OUTWARD,
        on_click=lambda e: expand_class_item()
    )

    def expand_class_item():
        pass

    def update_attendance_log():
        dt_attendance.rows.clear()

        cols, rows = db.get_attendance_log()

        rows = reversed(rows)
        for row in rows:
            dt_attendance.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row['date']))),
                        ft.DataCell(ft.Text(str(row['time']))),
                        ft.DataCell(ft.Text(row['student_name'])),
                        ft.DataCell(ft.Text(f"{row['course_id']} {row['year_level']}{row['section']}")),
                        ft.DataCell(ft.Text(row['status'])),
                    ]
                )
            )
        page.update()

    def update_class_list():
        dt_classes.rows.clear()

        cols, rows = db.get_class_list()

        rows = reversed(rows)
        for row in rows:
            dt_classes.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row['date']))),
                        ft.DataCell(ft.Text(str(row['class_start']))),
                        ft.DataCell(ft.Text(row['subject_id'])),
                        ft.DataCell(ft.Text(row['instructor_name'])),
                        ft.DataCell(expand_item_button)
                    ]
                )
            )
        page.update()

    # TODO: Add filtering and sorting for class list
    def filter_class_list():
        pass

    # TODO: Retrieve from database instead of manually listing
    # For dropdown options
    subject_options = [
        ft.DropdownOption(key='ICT-111', text='ICT-111'),
        ft.DropdownOption(key='ICT-107', text='ICT-107'),
        ft.DropdownOption(key='ICT-114', text='ICT-114'),
        ft.DropdownOption(key='CS-101', text='CS-101'),
        ft.DropdownOption(key='ICT-110', text='ICT-110'),
        ft.DropdownOption(key='ICT-112', text='ICT-112'),
        ft.DropdownOption(key='PE-4', text='PE-4'),
        ft.DropdownOption(key='GE-ELEC-1', text='GE-ELEC-1'),
    ]
    instructor_options = [
        ft.DropdownOption(key='001', text='Mr. C.L. Gimeno'),
        ft.DropdownOption(key='002', text='Mr. E.A. Centina'),
        ft.DropdownOption(key='003', text='Mrs. M.F. Franco'),
        ft.DropdownOption(key='008', text='Mrs. J. Calfoforo'),  # CS-101
        ft.DropdownOption(key='005', text='Mr. L. Barrios'),
        ft.DropdownOption(key='004', text='Ms. M. Escriba'),     # ICT-112
        ft.DropdownOption(key='006', text='Prof. J. Marfil'),    # PE-4
        ft.DropdownOption(key='007', text='Dr. R.A. Torres'),    # GE-ELEC-1
    ]

    # Helper: get instructor display name from their key/id
    def get_instructor_name(key: str) -> str:
        return next((o.text for o in instructor_options if o.key == key), key)

    # new sheet variables
    # Session type toggle: "regular" auto-fills times from DB; "makeup" lets user type them
    session_type_state = {"value": "regular"}
    schedule_slots_cache = []  # holds list of {"start", "end", "label"} from DB

    sched_start_field = ft.TextField(
        border_color=ft.Colors.SURFACE_BRIGHT,
        width=200, height=50, border_radius=10,
        label=ft.Text("Start Time"), hint_text="07:30",
        visible=False,
    )
    sched_end_field = ft.TextField(
        border_color=ft.Colors.SURFACE_BRIGHT,
        width=200, height=50, border_radius=10,
        label=ft.Text("End Time"), hint_text="09:30",
        visible=False,
    )

    # Dropdown shown in Regular mode — populated dynamically from DB
    timeslot_dropdown = ft.Dropdown(
        width=420,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
        border_color=ft.Colors.SURFACE_BRIGHT,
        label="Time Slot",
        hint_text="Select subject & instructor first",
        options=[],
        visible=True,
    )

    session_type_toggle = ft.SegmentedButton(
        selected=["regular"],
        segments=[
            ft.Segment(value="regular", label=ft.Text("Regular")),
            ft.Segment(value="makeup",  label=ft.Text("Make-up")),
            ft.Segment(value="special", label=ft.Text("Special")),
        ],
        on_change=lambda e: _on_session_type_change(e),
    )

    def _on_session_type_change(e):
        selected = e.control.selected[0] if e.control.selected else "regular"
        session_type_state["value"] = selected
        is_manual = selected in ("makeup", "special")
        sched_start_field.visible  = is_manual
        sched_end_field.visible    = is_manual
        timeslot_dropdown.visible  = not is_manual
        timeslot_dropdown.options  = []
        timeslot_dropdown.value    = None
        page.update()
        if not is_manual:
            _refresh_timeslot_dropdown()

    def _refresh_timeslot_dropdown():
        nonlocal schedule_slots_cache
        if session_type_state["value"] != "regular":
            return

        subject_val = subject_dropdown.content.value
        prof_val    = instructor_dropdown.content.value

        if not subject_val or not prof_val:
            timeslot_dropdown.options   = []
            timeslot_dropdown.value     = None
            timeslot_dropdown.hint_text = "Select subject & instructor first"
            timeslot_dropdown.update()
            return

        slots = db.get_schedule(subject_val, prof_val)
        print(f"DEBUG get_schedule({subject_val}, {prof_val}) → {slots}")
        schedule_slots_cache = slots

        timeslot_dropdown.options   = [
            ft.DropdownOption(key=str(i), text=s["label"])
            for i, s in enumerate(slots)
        ]
        timeslot_dropdown.value     = None
        timeslot_dropdown.hint_text = "No slots today — use Make-up" if not slots else "Select a time slot"
        timeslot_dropdown.update()

    subject_dropdown = ft.Container(
        width=420,
        height=50,
        content=ft.Dropdown(
            expand=True,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
            border_color=ft.Colors.SURFACE_BRIGHT,
            label=ft.Text("Subject"),
            options=subject_options,
        )
    )
    instructor_dropdown = ft.Container(
        width=420,
        height=50,
        content=ft.Dropdown(
            expand=True,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
            border_color=ft.Colors.SURFACE_BRIGHT,
            label=ft.Text("Instructor"),
            options=instructor_options,
        )
    )
    subject_dropdown.content.on_change    = lambda e: _refresh_timeslot_dropdown()
    instructor_dropdown.content.on_change = lambda e: _refresh_timeslot_dropdown()

    # ID Scanner page
    page_1 = ft.Container(
        ft.Column([
            ft.Container(
                align=ft.Alignment.TOP_CENTER,
                width=WIDTH,
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
                                width=410,
                                height=100,
                                content=ft.Column([
                                    ft.Text(
                                        value="Manual ID Input: ",
                                        style=ft.TextStyle(
                                            size=15,
                                            color=ft.Colors.ON_SURFACE_VARIANT
                                        )),
                                    manual_input_field
                                ], margin=ft.Margin(20, 10, 20, 10), alignment=ft.MainAxisAlignment.CENTER)
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
    page_3 = ft.Column(
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
                        ft.IconButton(
                            icon=ft.Icons.RESTART_ALT
                        )
                    ], spacing=180),
                    ft.Row([
                        ft.TextField(
                            border_color=ft.Colors.SURFACE_BRIGHT,
                            width=140,
                            height=50,
                            border_radius=10,
                            label=ft.Text("Date"),
                            hint_text="yyyy/mm/dd",
                        ),
                        ft.TextField(
                            border_color=ft.Colors.SURFACE_BRIGHT,
                            width=140,
                            height=50,
                            border_radius=10,
                            label=ft.Text("Time"),
                            hint_text="00:00",
                        ),
                    ]),
                    ft.Container(
                        width=290,
                        height=50,
                        content=ft.Dropdown(
                            expand=True,
                            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                            border_color=ft.Colors.SURFACE_BRIGHT,
                            label=ft.Text("Subject"),
                            options=subject_options,
                        )
                    ),
                    ft.Container(
                        width=290,
                        height=50,
                        content=ft.Dropdown(
                            expand=True,
                            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                            border_color=ft.Colors.SURFACE_BRIGHT,
                            label=ft.Text("Instructor"),
                            options=instructor_options,
                        )
                    ),
                    ft.Button(
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                        width=290,
                        height=50,
                        content=ft.Text("CONFIRM"),
                        on_click=update_class_list,
                    ), ], margin=20, spacing=20,
                ),
            ),
            ft.Column([
                ft.Button(
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                    width=250,
                    height=40,
                    content=ft.Text("NEW ATTENDANCE SHEET"),
                    on_click=lambda e: new_sheet(),
                    align=ft.Alignment.TOP_RIGHT
                ),
                dt_classes
            ], spacing=20, scroll=ft.ScrollMode.AUTO, expand=2)
        ],
            vertical_alignment=ft.CrossAxisAlignment.START,
            margin=20,
            spacing=30,
        ),
    )

    # Dashboard page
    page_4 = ft.Container()

    # New sheet page
    page_5 = ft.Column([
        ft.Row([
            ft.Text(value="NEW ATTENDANCE SHEET",
                    style=ft.TextStyle(
                        weight=ft.FontWeight.BOLD,
                        size=25,
                        color=ft.Colors.ON_SURFACE_VARIANT
                    )),
            ft.IconButton(
                icon=ft.Icons.CANCEL_OUTLINED,
                icon_size=28,
                on_click=lambda e: cancel_new_sheet()
            )
        ], spacing=120, alignment=ft.CrossAxisAlignment.CENTER),
        ft.Container(
            bgcolor=ft.Colors.SURFACE_CONTAINER,
            border_radius=20,
            width=480,
            height=420,
            content=ft.Column([
                session_type_toggle,
                subject_dropdown,
                instructor_dropdown,
                timeslot_dropdown,
                ft.Row([
                    sched_start_field,
                    sched_end_field
                ], spacing=20),
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
    page_6 = ft.Column()

    # Page Container
    current_page = ft.Container(content=page_4)

    # New Sheet button
    def new_sheet():
        current_page.content = page_5

    def clear_sheet_values():
        sched_start_field.value     = ""
        sched_end_field.value       = ""
        sched_start_field.visible   = False
        sched_end_field.visible     = False
        timeslot_dropdown.options   = []
        timeslot_dropdown.value     = None
        timeslot_dropdown.visible   = True
        timeslot_dropdown.hint_text = "Select subject & instructor first"
        session_type_state["value"]       = "regular"
        session_type_toggle.selected      = ["regular"]
        subject_dropdown.content.value    = None
        instructor_dropdown.content.value = None

    # Cancel selection
    def cancel_new_sheet():
        clear_sheet_values()
        current_page.content = page_3

    # Confirm new schedule
    def confirm_schedule():
        subject_val = subject_dropdown.content.value
        prof_val    = instructor_dropdown.content.value

        if not subject_val or not prof_val:
            page.show_dialog(
                ft.SnackBar(ft.Text("Please don't leave fields empty.", color=ft.Colors.ON_SURFACE_VARIANT),
                            bgcolor=ft.Colors.SURFACE_CONTAINER))
            return

        is_makeup = session_type_state["value"] in ("makeup", "special")

        if is_makeup:
            start_val = sched_start_field.value
            end_val   = sched_end_field.value

            if not start_val or not end_val:
                page.show_dialog(
                    ft.SnackBar(ft.Text("Please enter start and end times for make-up class.",
                                        color=ft.Colors.ON_SURFACE_VARIANT),
                                bgcolor=ft.Colors.SURFACE_CONTAINER))
                return

            start_time = convert_time(start_val)
            end_time   = convert_time(end_val)

            if start_time is False or end_time is False:
                return

            session_kind = session_type_state["value"]  # "makeup" or "special"

        else:
            # Regular: read selected time slot index from dropdown
            slot_index = timeslot_dropdown.value
            if slot_index is None or not schedule_slots_cache:
                page.show_dialog(
                    ft.SnackBar(ft.Text("Please select a time slot.",
                                        color=ft.Colors.ON_SURFACE_VARIANT),
                                bgcolor=ft.Colors.SURFACE_CONTAINER))
                return

            selected_slot = schedule_slots_cache[int(slot_index)]
            start_time = selected_slot["start"]
            end_time   = selected_slot["end"]
            session_kind = "regular"

        schedule['start']        = start_time
        schedule['end']          = end_time
        schedule['sub']          = subject_val
        schedule['prof_id']      = prof_val
        schedule['prof']         = get_instructor_name(prof_val)
        schedule['session_type'] = session_kind

        clear_sheet_values()
        current_page.content = page_3
        update_schedule_values()
        page.update()

    # update displayed schedule in scanner page
    def update_schedule_values():
        schedule_details[0].value = f"START OF SESSION:      {schedule['start']}"
        schedule_details[1].value = f"END OF SESSION:      {schedule['end']}"
        schedule_details[2].value = f"SUBJECT:      {schedule['sub']}"
        schedule_details[3].value = f"INSTRUCTOR:      {schedule['prof']}"

        page.update()

    # Navigation buttons
    def set_page(e):
        i = e.control.selected_index
        if i == 0:
            current_page.content = page_1
            update_schedule_values()
        elif i == 1:
            current_page.content = page_2
            update_attendance_log()
        elif i == 2:
            current_page.content = page_3
            update_class_list()
        elif i == 3:
            current_page.content = page_4
        page.update()

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
        on_change=set_page,
        selected_index=3,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH
    )
    # page.navigation_bar = navbar

    page.add(
        navbar,

        ft.SafeArea(
            align=ft.Alignment.TOP_CENTER,
            expand=True,

            # Changeable content
            content=current_page
        )
    )
    page.update()


# Run Flet app (Flutter my beloved!!)
if __name__ == "__main__":
    ft.run(main)
    cv.camera.release()