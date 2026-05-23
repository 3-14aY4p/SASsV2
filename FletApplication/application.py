# Module/Library imports
import flet as ft
from datetime import date
from datetime import time
from datetime import datetime
import threading
import time as t

# Custom imports for handler files
import handlers.dbhandler as db
import handlers.cvhandler as cv




#* MAIN FUNCTION
def main(page: ft.Page):
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
    
    
    # Error pop-ups
    def error_snackbar(error_text: str):
        page.show_dialog(ft.SnackBar(ft.Text(error_text,
                                             color=ft.Colors.ON_SURFACE_VARIANT),
                                     bgcolor=ft.Colors.SURFACE_CONTAINER))

    # Convert strings into datetime objects
    def convert_time(time_str: str) -> time | None:
        format = "%H:%M"
        try:
            time = datetime.strptime(time_str, format).time()
            return time
        except ValueError as e:
            error_snackbar("ERROR: Invalid format.")
            return None
        
    def convert_date(date_str: str) -> date | None:
        format = "%Y/%m/%d"
        try:
            date = datetime.strptime(date_str, format).date()
            return date
        except ValueError as e:
            error_snackbar("ERROR: Invalid format.")
            return None

    
    #* PAGE 0 COMPONENTS
    
    # Login information
    current_user = None
    current_u_id = None
    
    userid_field = ft.TextField(
            border_color=ft.Colors.SURFACE_BRIGHT,
            width=315, height=50,
            border_radius=10,
            label=ft.Text("ID Number"),
        )
    passwd_field = ft.TextField(
            border_color=ft.Colors.SURFACE_BRIGHT,
            width=315, height=50,
            border_radius=10,
            label=ft.Text("Password"),
            password=True,
        )
    
    
    #* PAGE 1 COMPONENTS
    
    camera_active = False
    cam_status_1 = ft.Text(value="Scanner active" if camera_active else "Scanner inactive",
                            style=ft.TextStyle(
                                weight=ft.FontWeight.NORMAL,
                                size=12,
                                color=ft.Colors.ON_SURFACE_VARIANT
                            )
                        )
    cam_status_2 = ft.Text(value="Camera connected" if camera_active else "Camera disconnected",
                            style=ft.TextStyle(
                                weight=ft.FontWeight.NORMAL,
                                size=12,
                                color=ft.Colors.ON_SURFACE_VARIANT
                            ),
                        )

    def update_cam_status():
        nonlocal cam_status_1, cam_status_2
        cam_status_1.value = "Scanner active" if camera_active else "Scanner inactive"
        cam_status_2.value = "Camera connected" if camera_active else "Camera disconnected"

        page.update()
        
    
    recent_activity_column = ft.Column(controls=[
        
    ])
    day_schedule_column = ft.Column(controls=[
        
    ])
    # HOW TO APPEND
    # column.controls.insert(0, ft.Text("test"))

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
    
    def update_time():
        while True:
            date_today.value = f"{datetime.now().strftime("%b %d, %Y || %A")}"
            time_today.value = f"{datetime.now().strftime("%I:%M %p")}"
            page.update()
            
            t.sleep(1)
    
    dashb_time_th = threading.Thread(
            target=update_time,
            args=[],
            daemon=True
        )
    dashb_time_th.start()
    
    
    #* PAGE 2 COMPONENTS
    
    # Session information
    session_details ={
            "bgn": None,
            "fin": None,
            "subj": None,
            "sect": None,
            "type": None,
            "c_id": None
        }
    session_details_ui = [
        ft.Text(value=f"+  SESSION:     {session_details['bgn']} - {session_details['fin']}" if session_details['bgn'] and session_details['fin'] != None else "+  SESSION:     None",
                style=ft.TextStyle(
                    weight=ft.FontWeight.NORMAL,
                    size=14,
                    color=ft.Colors.ON_SURFACE_VARIANT
                )
            ),
        ft.Text(value=f"+  SECTION:     {session_details['sect']}",
                style=ft.TextStyle(
                    weight=ft.FontWeight.NORMAL,
                    size=14,
                    color=ft.Colors.ON_SURFACE_VARIANT
                )
            ),
        ft.Text(value=f"+  SUBJECT:     {session_details['subj']}",
                style=ft.TextStyle(
                    weight=ft.FontWeight.NORMAL,
                    size=14,
                    color=ft.Colors.ON_SURFACE_VARIANT
                )
            ),
        ]
    
    # ID scanner input fields
    camera_preview = ft.Image(
            src="FletApplication/empty.jpg",
            width=760,
            height=495,
            fit=ft.BoxFit.COVER,
        )
    # camera_preview.src_base64 = ""
    video_container = ft.Container(
            bgcolor=ft.Colors.SURFACE_CONTAINER,
            expand=True,
            width=716, height=415,
            border_radius=20,
            content=camera_preview
        )
    manual_id_input = ft.TextField(
            width=716, height = 60,
            label = "Manual ID Input",
            hint_text= "xxxx-xxxx-x",
            border_color = ft.Colors.SURFACE_BRIGHT,
        )
    
    # Scanned object details
    scanner_output = {
            "s_id": None,
            "name": None,
            "stat": None
        }
    scanned_id = ft.Text(
            value=f"    {scanner_output['s_id']}",
            style=ft.TextStyle(
                weight=ft.FontWeight.NORMAL,
                size=12,
                color=ft.Colors.ON_SURFACE_VARIANT
            )
        )
    scanned_name = ft.Text(
            value=f"    {scanner_output['name']}",
            style=ft.TextStyle(
                weight=ft.FontWeight.NORMAL,
                size=12,
                color=ft.Colors.ON_SURFACE_VARIANT
            )
        )
    scanned_status = ft.Text(
            value=f"    {scanner_output['stat']}",
            style=ft.TextStyle(
                weight=ft.FontWeight.NORMAL,
                size=12,
                color=ft.Colors.ON_SURFACE_VARIANT
            )
        )
    
    def on_scan(ret_string: str, is_valid: bool):
        pass
    
    
    
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
            expand=True, height=50,
            content=ft.Dropdown(
                expand=True,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                border_color=ft.Colors.SURFACE_BRIGHT,
                label=ft.Text("Section"),
                options=section_options,
            )
        )
    filter_subj_dropdown = ft.Container(
            expand=True, height=50,
            content=ft.Dropdown(
                expand=True,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                border_color=ft.Colors.SURFACE_BRIGHT,
                label=ft.Text("Subject"),
                options=subject_options,
            )
        )
    
    dt_classes_log = ft.DataTable(
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
    
    
    #* PAGE 5 COMPONENTS
    #* PAGE 6 COMPONENTS
    # dt_session_log = ft.DataTable()
    
    
    #* PAGE SETUP; UI/UX
    
    # Login Page
    page_0 = ft.Container(
        bgcolor=ft.Colors.SURFACE_CONTAINER,
        width=440, height=360,
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
                )
            ),
            ], align=ft.Alignment.TOP_LEFT, margin=45, spacing=30,
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
                                    ft.Text(value=f"{session_details['bgn']} - {session_details['fin']}" if session_details['bgn'] and session_details['fin'] != None else "No active session",
                                        style=ft.TextStyle(
                                            weight=ft.FontWeight.NORMAL,
                                            size=14,
                                            color=ft.Colors.ON_SURFACE_VARIANT
                                        )
                                    ),
                                ]),
                                ft.Row([
                                    ft.Icon(icon=ft.Icons.PERSON_2_OUTLINED, size=14),
                                    ft.Text(value=f"{session_details['sect']}" if session_details['sect'] != None else "No active session",
                                        style=ft.TextStyle(
                                            weight=ft.FontWeight.NORMAL,
                                            size=14,
                                            color=ft.Colors.ON_SURFACE_VARIANT
                                        )
                                    ),
                                ]),
                                ft.Row([
                                    ft.Icon(icon=ft.Icons.RECEIPT_ROUNDED, size=14),
                                    ft.Text(value=f"{session_details['subj']}" if session_details['subj'] != None else "No active session",
                                        style=ft.TextStyle(
                                            weight=ft.FontWeight.NORMAL,
                                            size=14,
                                            color=ft.Colors.ON_SURFACE_VARIANT
                                        )
                                    ),
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
                            recent_activity_column if len(recent_activity_column.controls) != 0 else ft.Text(value="+ No recent activity."),
                            ], margin=ft.Margin(20, 15, 20, 15),
                        )
                    ),
                ], spacing=20, expand=2
            ),
            ft.Column([
                    ft.Row([
                            date_today,
                            time_today
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
                    ft.Text(value="TODAY'S SCHEDULE",
                            style=ft.TextStyle(
                                weight=ft.FontWeight.BOLD,
                                size=28,
                                color=ft.Colors.ON_SURFACE_VARIANT
                            )
                        ),
                    day_schedule_column if len(day_schedule_column.controls) != 0 else ft.Text(value="+ You have no schedule lined up for today."),
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
                                        ft.IconButton(
                                            icon = ft.Icons.CLASS_OUTLINED,
                                            align = ft.Alignment.CENTER_RIGHT,
                                            style = ft.ButtonStyle(
                                                bgcolor = ft.Colors.SURFACE_CONTAINER_HIGH
                                            ),
                                        ),
                                    ], spacing=118
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
                                ft.Text(value="+  STUDENT ID",
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
                                ft.Text(value="+  ATTENDANCE",
                                        style=ft.TextStyle(
                                            weight=ft.FontWeight.BOLD,
                                            size=14,
                                            color=ft.Colors.ON_SURFACE_VARIANT
                                        )
                                    ),
                                scanned_status,
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
                        dt_classes_log,
                    ], scroll=ft.ScrollMode.AUTO, expand=5
                ),
            ], spacing=30
        )
    )
    
    # TODO: New session page
    # TODO: Expanded previous sessions page
    # TODO: Expanded session analytics page
    
    
    
    
     # * CAMERA THREAD FUNCTIONS

    # Switch for controlling camera thread
    _scanner_stop_event = threading.Event()

    # Start camera thread
    def start_scanner_thread():
        nonlocal camera_active
        
        if session_details['bgn'] == None or session_details['fin'] == None or session_details['subj'] == None or session_details['sect'] == None:
            return

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
        
        camera_active = False
        _scanner_stop_event.set()  # Signal the thread to stop
    
    
    def set_page(e):
        i = e.control.selected_index
        if i == 0:
            update_cam_status()
            current_page.content = page_1
        elif i == 1:
            start_scanner_thread()
            current_page.content = page_2
        elif i == 2:
            kill_scanner_thread()
            current_page.content = page_3
        elif i == 3:
            kill_scanner_thread()
            current_page.content = page_4
        page.update()
    
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
    current_navi = ft.Container(content=navbar)
    current_page = ft.Container(content=page_1) # TODO: Revert to defaults after setup
    

    def close_app():
        try:
            kill_scanner_thread()
            if cv.camera:
                cv.camera.release()

        except Exception as e:
            print(e)
            
        
    page.add(
        current_navi,
        ft.SafeArea(
            align=ft.Alignment.TOP_CENTER,
            expand=True,
            
            # Changeable content
            content=current_page
        )
    )
    page.update()
    
    page.on_close = close_app



# Run Flet app
if __name__ == "__main__":
    ft.run(main)