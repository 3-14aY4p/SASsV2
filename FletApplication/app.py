# Module/Library imports
import flet as ft
import threading
from datetime import datetime, time, date
import base64

# Custom files for handling
import handlers.dbhandler as db
import handlers.cvhandler as cv


#* Main structure; We gotta put it all here!!
def main(page: ft.Page):
    # Page settings
    page.title = "SASs: Smart Attendance System"
    page.theme_mode = ft.ThemeMode.DARK
    
    WIDTH, HEIGHT = 1280, 780

    page.window_resizable = False
    page.window.minimizable = False
    page.window.width  = WIDTH
    page.window.height = HEIGHT
    
    page.window.min_height = HEIGHT
    page.window.min_width = WIDTH
    page.window.max_height = HEIGHT
    page.window.max_width = WIDTH
    


    # FIXME: Camera Vision stuff; still broken
    frame_bytes = None
    camera_preview = ft.Image(
        src = "placeholder",
        width = 760,
        height = 540,
        fit = ft.BoxFit.FILL,
    )
    camera_preview.src_base64 = ""
    
    video_container = ft.Container(
        content = camera_preview,
        margin = ft.Margin(0, 0, 0, 60),
        bgcolor = ft.Colors.SURFACE_CONTAINER,
        border_radius = 30,
        width = 760,
        height = 540
    )
    
    def on_detect(student_id):
        pass

    threading.Thread(
        target=cv.update_frames,
        args=(page, camera_preview, on_detect),
        daemon=True
    ).start()
    
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
            ft.DataColumn(ft.Text("COURSE, YEAR, & SECTION")),
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
            ft.DataColumn(ft.Text("INSTRUCTOR")),
        ],
        rows = [], 
    )

    # Database Retrievals, Updates, and Sort
    a_cols, a_rows = db.get_attendance_log()
    c_cols, c_rows = db.get_class_list()
    
    
    def update_attendance_log():
        dt_attendance.rows.clear()
        
        cols, rows = a_cols, a_rows
        for row in rows:
            dt_attendance.rows.append(
                ft.DataRow(
                    cells = [
                        ft.DataCell(ft.Text(str(row['date']))),
                        ft.DataCell(ft.Text(str(row['time']))),
                        ft.DataCell(ft.Text(row['student_name'])),
                        ft.DataCell(ft.Text(f"{row['course']} {row['year_level']}{row['section']}")),
                        ft.DataCell(ft.Text(row['attendance_status'])),
                    ]
                )
            )
        
        page.update()
    
    # No filter applied
    def update_class_list():
        dt_classes.rows.clear()
        
        cols, rows = c_cols, c_rows
        for row in rows:
            dt_classes.rows.append(
                ft.DataRow(
                    cells = [
                        ft.DataCell(ft.Text(str(row['date']))),
                        ft.DataCell(ft.Text(str(row['class_start']))),
                        ft.DataCell(ft.Text(row['subject_id'])),
                        ft.DataCell(ft.Text(row['instructor_name'])),
                    ]
                )
            )
        
        page.update()
    
    # TODO: Add filtering and sorting for class list
    def filter_class_list():
        pass
    
    
    # Convert strings into datetime objects
    def convert_time(time_str: str) -> time:
        format = "%H:%M"
        time = datetime.strptime(time_str, format).time()

        return time
    
    def convert_time(date_str: str) -> date:
        format = "%Y/%m/%d"
        date = datetime.strptime(date_str, format).date()

        return date
    
    
    # TODO: Retrieve from database instead of manually listing
    # For dropdown options
    subject_options = [
        ft.DropdownOption(text = 'ICT-111'),
        ft.DropdownOption(text = 'ICT-107'),
        ft.DropdownOption(text = 'ICT-114'),
        ft.DropdownOption(text = 'CS-101'),
        ft.DropdownOption(text = 'ICT-110'),
        ft.DropdownOption(text = 'ICT-112'),
        ft.DropdownOption(text = 'PE-4'),
        ft.DropdownOption(text = 'GE-ELEC-1'),
    ]
    instructor_options = [
        ft.DropdownOption(text = 'Mr. C.L. Gimeno'),
        ft.DropdownOption(text = 'Mr. E.A. Centina'),
        ft.DropdownOption(text = 'Mrs. M.F. Franco'),
        ft.DropdownOption(text = 'Mrs. J. Calfoforo'),
        ft.DropdownOption(text = 'Mr. L. Barrios'),
        ft.DropdownOption(text = 'Ms. M. Escriba'),
        ft.DropdownOption(text = 'Prof. J. Marfil'),
        ft.DropdownOption(text = 'Dr. R.A. Torres'),
    ]


    # ID Scanner page
    page_1 = ft.Container(
        ft.Row([
            video_container,
            ft.Container(
                width = 410,
                height = 580,
                content = ft.Container(
                    ft.Column([
                        ft.Container(
                            bgcolor = ft.Colors.SURFACE_CONTAINER,
                            border_radius = 30,
                            width = 410,
                            height = 100,
                            content = ft.Column([
                                ft.Text(
                                    value = "SCANNER STATUS", 
                                    align = ft.Alignment.CENTER,
                                    style = ft.TextStyle(
                                        weight = ft.FontWeight.BOLD,
                                        size = 25,
                                        color = ft.Colors.ON_SURFACE_VARIANT
                                    )
                                ),
                                ft.Text(
                                    value = "waiting for scan...", 
                                    align = ft.Alignment.CENTER,
                                    style = ft.TextStyle(
                                        size = 20,
                                        color = ft.Colors.SURFACE_BRIGHT
                                    )
                                )
                            ], spacing = -3, alignment = ft.MainAxisAlignment.CENTER),
                        ),
                        ft.Container(
                            bgcolor = ft.Colors.SURFACE_CONTAINER,
                            border_radius = 30,
                            width = 410,
                            height = 300,
                        ),
                    ], spacing = 20)
                )
            )
        ], spacing = 30, vertical_alignment = ft.CrossAxisAlignment.START,), margin = 30
    )

    # Attendance Log page
    page_2 = ft.Container(
        content = dt_attendance,
        margin = 20,
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
                                label = ft.Text("Instructor"),
                                options = instructor_options,
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
                        on_click = lambda e: new_sheet()
                    ),
                    dt_classes
                ], spacing = 20,)
            ], 
            vertical_alignment = ft.CrossAxisAlignment.START,
            margin = 20, 
            spacing = 30,
        ),
    )

    # Dashboard page
    page_4 = ft.Container(ft.Text(value="DASHBOARD HERE!!!"))
    
    # New sheet page
    page_5 = ft.Column([
        ft.Row([
            ft.Text(value = "NEW ATTENDANCE SHEET",
            style = ft.TextStyle(
                weight = ft.FontWeight.BOLD,
                size = 25,
                color = ft.Colors.ON_SURFACE_VARIANT
            )),
            ft.IconButton(
                icon = ft.Icons.CANCEL_OUTLINED,
                icon_size = 28,
                on_click = lambda e: cancel_new_sheet()
            )
        ], spacing = 120, alignment = ft.CrossAxisAlignment.CENTER),
        ft.Container(
            bgcolor = ft.Colors.SURFACE_CONTAINER,
            border_radius = 20,
            width = 480,
            height = 320,
            content = ft.Column([
                ft.Row([
                    ft.TextField(
                        border_color = ft.Colors.SURFACE_BRIGHT,
                        width = 200,
                        height = 50,
                        border_radius = 10,
                        label = ft.Text("Start Time"),
                        hint_text = "07:30",
                    ),
                    ft.TextField(
                        border_color = ft.Colors.SURFACE_BRIGHT,
                        width = 200,
                        height = 50,
                        border_radius = 10,
                        label = ft.Text("End Time"),
                        hint_text = "09:30",
                    ),
                ], spacing = 20),
                ft.Container(
                    width = 420,
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
                    width = 420,
                    height = 50,
                    content = ft.Dropdown(
                        expand = True,
                        bgcolor = ft.Colors.SURFACE_CONTAINER_HIGH,
                        border_color = ft.Colors.SURFACE_BRIGHT,
                        label = ft.Text("Instructor"),
                        options = instructor_options,
                    )
                ),
                ft.Button(
                    bgcolor = ft.Colors.SURFACE_CONTAINER_HIGH,
                    width = 240,
                    height = 50,
                    content = ft.Text("CREATE"),
                    margin = ft.Margin(240, 0, 0, 0)
                )
            ], alignment = ft.Alignment.TOP_CENTER, margin = 30, spacing = 20)
        ),], 
        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
        margin = ft.Margin(0, 60, 0, 0), spacing = 20)
    
    # Page Container
    current_page = ft.Container(content = page_1)


    # New Sheet button
    def new_sheet():
        current_page.content = page_5
        
    def cancel_new_sheet():
        current_page.content = page_3

    # Navigation buttons
    def set_page(e):
        i = e.control.selected_index
        if i == 0:
            current_page.content = page_1
        elif i == 1:
            current_page.content = page_2
            update_attendance_log()
        elif i == 2:
            current_page.content = page_3
            update_class_list()                 # TODO: Add this function to be triggered after each new class
        elif i == 3:
            current_page.content = page_4
        page.update()
        
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
        on_change = set_page,
        selected_index = 0,
        bgcolor = ft.Colors.SURFACE_CONTAINER_HIGH
    )
    # page.navigation_bar = navbar

    page.add(
        navbar,

        ft.SafeArea(
            align = ft.Alignment.CENTER,
            
            # Changeable content
            content = current_page
        )
    )
    page.update()



# Run Flet app (Flutter my beloved!!)
if __name__ == "__main__":
    ft.run(main)