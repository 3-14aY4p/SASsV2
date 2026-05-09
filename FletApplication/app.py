# Module/Library imports
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

    page.window.resizable = False
    page.window.minimizable = False
    page.window.maximizable = False
    page.window.width  = WIDTH
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
 
 
    #* VARIABLES FOR THE CURRENT USER (Instructor details)
    
    current_user_name: str = None
    current_user_id: str = None
 
 
    #* VARIABLES FOR LOGIN PAGE
    
    user_id_field = ft.TextField(
        border_color = ft.Colors.SURFACE_BRIGHT,
        width = 480,
        height = 50,
        border_radius = 10,
        label = ft.Text("ID Number"),
    )
    password_field = ft.TextField(
        border_color = ft.Colors.SURFACE_BRIGHT,
        width = 480,
        height = 50,
        border_radius = 10,
        label = ft.Text("Password"),
        password = True,
    )
 

    #* DYNAMIC VARIABLES FOR ATTENDANCE LOGGING

    schedule: dict = {
        "start": None,
        "end": None,
        "sub": None,
        "sect": None
    }
    schedule_details: list = [
        ft.Text(
            value = f"START OF SESSION:      {schedule["start"]}", 
            style = ft.TextStyle(
                weight = ft.FontWeight.BOLD,
                size = 15,
                color = ft.Colors.ON_SURFACE_VARIANT
            )
        ),
        ft.Text(
            value = f"END OF SESSION:      {schedule["end"]}", 
            style = ft.TextStyle(
                weight = ft.FontWeight.BOLD,
                size = 15,
                color = ft.Colors.ON_SURFACE_VARIANT
            )
        ),
        ft.Text(
            value = f"SUBJECT:      {schedule["sub"]}", 
            style = ft.TextStyle(
                weight = ft.FontWeight.BOLD,
                size = 15,
                color = ft.Colors.ON_SURFACE_VARIANT
            )
        ),
        ft.Text(
            value = f"SECTION:       {schedule["sect"]}", 
            style = ft.TextStyle(
                weight = ft.FontWeight.BOLD,
                size = 15,
                color = ft.Colors.ON_SURFACE_VARIANT
            )
        ),
    ]


    #* SCANNER PAGE VARIABLES
    # FIXME: Constant flickering of camera
    
    # Dynamic variables for Scanner
    scan_status = ft.Text(
        value = "waiting for scan...", 
        align = ft.Alignment.CENTER,
        style = ft.TextStyle(
            size = 20,
            color = ft.Colors.SURFACE_BRIGHT
        )
    )
    scanned_name = ft.Text(
        value = "waiting for scan...", 
        align = ft.Alignment.CENTER,
        style = ft.TextStyle(
            size = 20,
            color = ft.Colors.SURFACE_BRIGHT
        )
    )
    scanned_id = ft.Text(
        value = "waiting for scan...", 
        align = ft.Alignment.CENTER,
        style = ft.TextStyle(
            size = 20,
            color = ft.Colors.SURFACE_BRIGHT
        )
    )
    manual_input_field = ft.TextField(
        label = "",
        expand = True,
        height = 40,
        border_color = ft.Colors.SURFACE_BRIGHT,
        on_submit = lambda e: manual_attendance(e)
    )

    # Camera/Video variables
    camera_preview = ft.Image(
        src = "FletApplication/test.jpg",
        width = 760,
        height = 495,
        fit = ft.BoxFit.COVER,
    )
    camera_preview.src_base64 = ""
    video_container = ft.Container(
        content = camera_preview,
        margin = ft.Margin(0, 0, 0, 60),
        bgcolor = ft.Colors.SURFACE_CONTAINER,
        border_radius = 30,
        width = 760,
        height = 495
    )


    #* FOR DATABASE RETRIEVED CONTENT

    # TODO: Add functionality to expand on class item 
    expand_item_button = ft.IconButton(
        icon = ft.Icons.ARROW_OUTWARD,
        on_click = lambda e: expand_class_item()
    )
    
    # Database Tables
    dt_attendance = ft.DataTable(
        align = ft.Alignment.CENTER,
        width = WIDTH,
        expand = True,
        border = ft.Border.all(2, ft.Colors.SURFACE_BRIGHT),
        horizontal_lines = ft.border.BorderSide(1, ft.Colors.SURFACE_BRIGHT),
        heading_row_color = ft.Colors.SURFACE_CONTAINER_LOW,
        columns = [
            ft.DataColumn(ft.Text("DATE")),
            ft.DataColumn(ft.Text("TIME")),
            ft.DataColumn(ft.Text("NAME")),
            ft.DataColumn(ft.Text("SECTION")),
            ft.DataColumn(ft.Text("STATUS")),
        ],
        rows = [], 
    )
    dt_classes = ft.DataTable(
        align = ft.Alignment.CENTER,
        width = 860,
        expand = True,
        border = ft.Border.all(2, ft.Colors.SURFACE_BRIGHT),
        horizontal_lines = ft.border.BorderSide(1, ft.Colors.SURFACE_BRIGHT),
        heading_row_color = ft.Colors.SURFACE_CONTAINER_LOW,
        columns = [
            ft.DataColumn(ft.Text("DATE")),
            ft.DataColumn(ft.Text("START TIME")),
            ft.DataColumn(ft.Text("SUBJECT CODE")),
            ft.DataColumn(ft.Text("SECTION")),
            ft.DataColumn(ft.Text("")),
        ],
        rows = [], 
    )
    

    #* ATTENDANCE SHEETS CONTENT VARIABLES
    
    # TODO: Retrieve from database instead of manually listing
    # TODO: Retrieve schedule for specific section and subject
    # For dropdown options
    subject_options = [

    ]
    section_options = [
        
    ]
    timeslot_options = [ 

    ]
    
    session_start_field = ft.TextField(
        border_color = ft.Colors.SURFACE_BRIGHT,
        width = 200,
        height = 50,
        border_radius = 10,
        label = ft.Text("Start Time"),
        hint_text = "07:30",
    )
    session_end_field = ft.TextField(
        border_color = ft.Colors.SURFACE_BRIGHT,
        width = 200,
        height = 50,
        border_radius = 10,
        label = ft.Text("End Time"),
        hint_text = "09:30",
    )
    session_type_toggle = ft.SegmentedButton(
        width = 420,
        height = 30,
        margin = ft.Margin(0, 0, 0, 10),
        align = ft.Alignment.CENTER, 
        allow_multiple_selection = False,
        allow_empty_selection = False,
        selected = ["regular"],
        segments = [
            ft.Segment(value="regular", label=ft.Text("Regular")),
            ft.Segment(value="makeup",  label=ft.Text("Makeup")),
        ],
        on_change = lambda e: on_session_type_change(e),
    )
    subject_dropdown = ft.Container(
        width = 420,
        height = 50,
        content = ft.Dropdown(
            expand = True,
            bgcolor = ft.Colors.SURFACE_CONTAINER_HIGH,
            border_color = ft.Colors.SURFACE_BRIGHT,
            label = ft.Text("Subject"),
            options = subject_options,
        )
    )
    section_dropdown = ft.Container(
        width = 420,
        height = 50,
        content = ft.Dropdown(
            expand = True,
            bgcolor = ft.Colors.SURFACE_CONTAINER_HIGH,
            border_color = ft.Colors.SURFACE_BRIGHT,
            label = ft.Text("Section"),
            options = section_options,
        )
    )
    timeslot_dropdown = ft.Container(
        width = 420,
        height = 50,
        content = ft.Dropdown(
            expand = True,
            bgcolor = ft.Colors.SURFACE_CONTAINER_HIGH,
            border_color = ft.Colors.SURFACE_BRIGHT,
            label = ft.Text("Timeslot"),
            options = timeslot_options,
        )
    )
    manual_timeslots = ft.Container(
         ft.Row([
            session_start_field,
            session_end_field
        ], spacing = 20),
    )
    timeslot_field = ft.Container(content = timeslot_dropdown)


    def error_snackbar(error_text: str):
        page.show_dialog(ft.SnackBar(ft.Text(error_text, 
                color = ft.Colors.ON_SURFACE_VARIANT), 
                bgcolor = ft.Colors.SURFACE_CONTAINER))


    #* LOGIN PAGE FUNCTIONS
    
    def validate_user():
        if user_id_field.value == "" or password_field.value == "":
            error_snackbar("ERROR: Empty fields found.")
        
        # TODO: Detect incorrect user_id
        # TODO: Detect incorrect password
        
        navigator.content = navbar
        current_page.content = page_1


    #* SCANNER PAGE FUNCTIONS
    # FIXME: Cater scanning to database changes

    # CV Logic for when ID template is detected
    def on_scan(ret_string: str, is_valid: bool):
        pass
    
    # Recording of attendance through text fields
    def manual_attendance(e: str):
        pass
    
    # TODO: Start and End camera thread properly

    # Switch for controlling camera thread
    _scanner_stop_event = threading.Event()


    # Start camera thread
    def start_scanner_thread():
        _scanner_stop_event.clear()  # Clear and reset threading
        threading.Thread(
            target = cv.capture_frames,
            args = (page, camera_preview, on_scan, _scanner_stop_event),
            daemon = True, 
        ).start()

    def kill_scanner_thread():
        _scanner_stop_event.set() # Signal the thread to stop

    # Update displayed schedule in scanner page
    def update_schedule_values():
        schedule_details[0].value = f"START OF SESSION:      {schedule['start']}"
        schedule_details[1].value = f"END OF SESSION:      {schedule['end']}"
        schedule_details[2].value = f"SUBJECT:      {schedule['sub']}"
        schedule_details[3].value = f"SECTION:      {schedule['sect']}"
        
        page.update()


    #* FUNCTIONS INVOLVING DATABASE RETRIEVALS
    # FIXME: Cater retrievals to database changes

    def update_attendance_log():
        pass
    
    # TODO: Change 'instructor' to 'section'
    def update_class_list():
        pass
      
    # TODO: Add filtering and sorting for class list
    def filter_class_list():
        pass
    
    # TODO: Expand and view specific class items
    def expand_class_item():
        pass
    

    #* FUNCTIONS FOR CREATING NEW SESSIONS

    # New Sheet button
    def new_session():
        current_page.content = page_5
    
    # For session_type_toggle
    def on_session_type_change(e):
        slot_types = {
            "regular": timeslot_dropdown,
            "makeup": manual_timeslots
        }
        timeslot_field.content = slot_types.get(e.data[0])
    
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

    # Confirm new schedule
    def confirm_schedule():
        if session_start_field.value == "" or session_end_field.value == "" or subject_dropdown.content.value == None or section_dropdown.content.value == None:
            error_snackbar("ERROR: Empty fields found.")
            
        elif convert_time(session_start_field.value) == False or convert_time(session_end_field.value) == False:
            return
        
        else:
            schedule['start'] = convert_time(session_start_field.value)
            schedule['end'] = convert_time(session_end_field.value)
            schedule['sub'] = subject_dropdown.content.value
            schedule['sect'] = section_dropdown.content.text
            
            clear_sheet_values()
            
            current_page.content = page_3


    #* APPLICATION PAGE SETUPS
    
    # Navigation buttons
    def set_page(e):
        i = e.control.selected_index
        if i == 0:
            current_page.content = page_1
            update_schedule_values()
            start_scanner_thread()  # Start camera thread when entering scanner page
        elif i == 1:
            kill_scanner_thread() # Stop camera thread before leaving page
            current_page.content = page_2
            update_attendance_log()
        elif i == 2:
            kill_scanner_thread() # Stop camera thread before leaving page
            current_page.content = page_3
            update_class_list()
        elif i == 3:
            kill_scanner_thread() # Stop camera thread before leaving page
            current_page.content = page_4
        page.update()


    # TODO: Login page
    page_0 = ft.Container(
        bgcolor = ft.Colors.SURFACE_CONTAINER,
        border_radius = 20,
        align = ft.Alignment.CENTER,
        width = 440,
        height = 360,
        content = ft.Column([
            ft.Text(value = "USER LOGIN",
            style = ft.TextStyle(
                weight = ft.FontWeight.BOLD,
                size = 20,
                color = ft.Colors.ON_SURFACE_VARIANT
            )),
            user_id_field,
            password_field,
            ft.ElevatedButton(
                content = "Log In",
                width = 180,
                height = 50,
                align = ft.Alignment.BOTTOM_RIGHT,
                style = ft.ButtonStyle(
                    shape = ft.RoundedRectangleBorder(radius = 10),
                    bgcolor = ft.Colors.SURFACE_CONTAINER_HIGH
                ),
                on_click = lambda e: validate_user()
            ),
        ], align = ft.Alignment.TOP_LEFT, margin = ft.Margin(45, 45, 45, 45), spacing = 30)
    )

    # ID Scanner page
    page_1 = ft.Container(
        ft.Column([
            ft.Container(
                align = ft.Alignment.TOP_CENTER,
                width = WIDTH,
                height = 70,
                bgcolor = ft.Colors.SURFACE_CONTAINER,
                border_radius = 20,
                content = ft.Row([
                    schedule_details[0],
                    schedule_details[1],
                    schedule_details[2],
                    schedule_details[3],
                ], spacing = 90, alignment = ft.CrossAxisAlignment.CENTER)
            ),
            ft.Row([
                video_container,
                ft.Container(
                    width = 410,
                    height = 580,
                    content = ft.Container(
                        ft.Column([
                            ft.Text(
                                value = "STUDENT INFORMATION", 
                                align = ft.Alignment.CENTER,
                                style = ft.TextStyle(
                                    weight = ft.FontWeight.BOLD,
                                    size = 25,
                                    color = ft.Colors.ON_SURFACE_VARIANT
                                )
                            ),
                            ft.Container(
                                bgcolor = ft.Colors.SURFACE_CONTAINER,
                                border_radius = 30,
                                width = 410,
                                height = 200,
                                content = ft.Column([
                                    ft.Text(
                                        value = "STUDENT NAME", 
                                        align = ft.Alignment.CENTER,
                                        style = ft.TextStyle(
                                            weight = ft.FontWeight.BOLD,
                                            size = 22,
                                            color = ft.Colors.ON_SURFACE_VARIANT
                                        )
                                    ),
                                    scanned_name,
                                    
                                    ft.Text(
                                        margin = ft.Margin(0, 30, 0, 0),
                                        value = "STUDENT ID", 
                                        align = ft.Alignment.CENTER,
                                        style = ft.TextStyle(
                                            weight = ft.FontWeight.BOLD,
                                            size = 22,
                                            color = ft.Colors.ON_SURFACE_VARIANT
                                        )
                                    ),
                                    scanned_id,
                                ], spacing = -3, alignment = ft.MainAxisAlignment.CENTER),
                            ),
                            ft.Container(
                                bgcolor = ft.Colors.SURFACE_CONTAINER,
                                border_radius = 30,
                                width = 410,
                                height = 100,
                                content = ft.Column([
                                    ft.Text(
                                        value = "SCAN STATUS", 
                                        align = ft.Alignment.CENTER,
                                        style = ft.TextStyle(
                                            weight = ft.FontWeight.BOLD,
                                            size = 22,
                                            color = ft.Colors.ON_SURFACE_VARIANT
                                        )
                                    ),
                                    scan_status
                                ], spacing = -3, alignment = ft.MainAxisAlignment.CENTER),
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
                        ], spacing = 20)
                    )
                )
            ], spacing = 30, vertical_alignment = ft.CrossAxisAlignment.START, align = ft.Alignment.CENTER)
        ], margin = ft.Margin(30, 10, 30, 30), spacing = 30, align = ft.Alignment.CENTER,)
    )

    # Attendance Log page
    page_2 = ft.Container(
        content = ft.Column([
            dt_attendance, 
        ], scroll= ft.ScrollMode.AUTO, expand = 2),
        margin = 20,
        alignment = ft.Alignment.TOP_CENTER
    )

    # Class List page
    page_3 = ft.Column(
            ft.Row([
                ft.Container(
                    bgcolor = ft.Colors.SURFACE_CONTAINER,
                    border_radius = 30,
                    width = 330,
                    height = 360,
                    content = ft.Column([
                        ft.Row([
                            ft.Text(value = "FILTERS",
                            style = ft.TextStyle(
                                weight = ft.FontWeight.BOLD,
                                size = 20,
                                color = ft.Colors.ON_SURFACE_VARIANT
                            )),
                            ft.IconButton(
                                icon = ft.Icons.RESTART_ALT
                            )
                        ], spacing = 180),
                        ft.Row([
                            ft.TextField(
                                border_color = ft.Colors.SURFACE_BRIGHT,
                                width = 140,
                                height = 50,
                                border_radius = 10,
                                label = ft.Text("Date"),
                                hint_text = "yyyy/mm/dd",
                            ),
                            ft.TextField(
                                border_color = ft.Colors.SURFACE_BRIGHT,
                                width = 140,
                                height = 50,
                                border_radius = 10,
                                label = ft.Text("Time"),
                                hint_text = "00:00",
                            ),
                        ]),
                        ft.Container(
                            width = 290,
                            height = 50,
                            content = ft.Dropdown(
                                expand = True,
                                bgcolor = ft.Colors.SURFACE_CONTAINER_HIGH,
                                border_color = ft.Colors.SURFACE_BRIGHT,
                                label = ft.Text("Subject"),
                                options = subject_options,
                            )
                        ),
                        ft.Container(
                            width = 290,
                            height = 50,
                            content = ft.Dropdown(
                                expand = True,
                                bgcolor = ft.Colors.SURFACE_CONTAINER_HIGH,
                                border_color = ft.Colors.SURFACE_BRIGHT,
                                label = ft.Text("Section"),
                                options = section_options,
                            )
                        ),
                        ft.Button(
                            bgcolor = ft.Colors.SURFACE_CONTAINER_HIGH,
                            width = 290,
                            height = 50,
                            content = ft.Text("CONFIRM"),
                            on_click =  update_class_list,
                        ),], margin = 20, spacing = 20,
                    ), 
                ),
                ft.Column([
                    ft.Button(
                        bgcolor = ft.Colors.SURFACE_CONTAINER_HIGH,
                        width = 250,
                        height = 40,
                        content = ft.Text("NEW ATTENDANCE SHEET"),
                        on_click = lambda e: new_session(),
                        align = ft.Alignment.TOP_RIGHT
                    ),
                    dt_classes
                ], spacing = 20, scroll= ft.ScrollMode.AUTO, expand = 2)
            ], 
            vertical_alignment = ft.CrossAxisAlignment.START,
            margin = 20, 
            spacing = 30,
        ),
    )

    # TODO: Dashboard page
    page_4 = ft.Container()
    
    # New sheet page
    page_5 = ft.Column([
        ft.Row([
            ft.Text(value = "NEW SESSION",
            style = ft.TextStyle(
                weight = ft.FontWeight.BOLD,
                size = 25,
                color = ft.Colors.ON_SURFACE_VARIANT
            ), margin = ft.Margin(0, 0, 200, 0)),
            ft.IconButton(
                icon = ft.Icons.REFRESH_OUTLINED,
                icon_size = 28,
                on_click = lambda e: refresh_sheet()
            ),
            ft.IconButton(
                icon = ft.Icons.CANCEL_OUTLINED,
                icon_size = 28,
                on_click = lambda e: cancel_new_sheet()
            )
        ], alignment = ft.CrossAxisAlignment.CENTER),
        ft.Container(
            bgcolor = ft.Colors.SURFACE_CONTAINER,
            border_radius = 20,
            width = 480,
            height = 370,
            content = ft.Column([
                session_type_toggle,
                subject_dropdown,
                section_dropdown,
                timeslot_field,
                ft.Button(
                    bgcolor = ft.Colors.SURFACE_CONTAINER_HIGH,
                    width = 240,
                    height = 50,
                    content = ft.Text("CREATE"),
                    margin = ft.Margin(240, 0, 0, 0),
                    on_click = lambda e: confirm_schedule()
                )
            ], alignment = ft.Alignment.TOP_CENTER, margin = 30, spacing = 20)
        ),], 
        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
        margin = ft.Margin(0, 60, 0, 0), spacing = 20)
    
    # TODO: Class item page
    page_6 = ft.Column()
    
    # Page Container
    navbar = ft.NavigationBar(destinations = [
        ft.NavigationBarDestination(
            icon = ft.Icons.IMAGE,
            label = "ID Scanner"
        ),
        ft.NavigationBarDestination(
            icon = ft.Icons.ASSIGNMENT,
            label = "Attendance Log"
        ),
        ft.NavigationBarDestination(
            icon = ft.Icons.CLASS_,
            label = "Class List"
        ),
        ft.NavigationBarDestination(
            icon = ft.Icons.ANALYTICS,
            label = "Dashboard"
        ),],
        on_change = lambda e: set_page(e),
        selected_index = 0,
        bgcolor = ft.Colors.SURFACE_CONTAINER_HIGH
    )
    navigator = ft.Container(content = None)
    current_page = ft.Container(content = page_0)
    
    
    
    page.add(
        navigator,
        ft.SafeArea(
            align = ft.Alignment.TOP_CENTER,
            expand = True,
            
            # Changeable content
            content = current_page
        )
    )
    page.update()

    # moved camera release to a function to ensure it runs before app closes
    def close_app():
        kill_scanner_thread() # Camera thread stop before releasing camera
        cv.camera.release()

    page.on_close = close_app


# Run Flet app (Flutter my beloved!!)
if __name__ == "__main__":
    ft.run(main)
    