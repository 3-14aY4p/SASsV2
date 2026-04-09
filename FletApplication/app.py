# Module/Library imports
import flet as ft
import threading
from datetime import datetime

# Custom files for handling
import handlers.dbhandler as db
import handlers.cvhandler as cv


#* Main structure; We gotta put it all here!!
def main(page: ft.Page):
    # Page settings
    page.title = "SASs: Smart Attendance System"
    page.theme_mode = ft.ThemeMode.DARK
    
    WIDTH, HEIGHT = 1280, 720

    page.window_resizable = False
    page.window.width  = WIDTH
    page.window.height = HEIGHT


    # FIXME: Camera Vision stuff; still broken
    frame_bytes = None
    camera_preview = ft.Image(
        src = frame_bytes,
        fit = ft.BoxFit.FILL
    )
    video_container = ft.Container(
        # content = camera_preview,
        margin = ft.Margin(20, 20, 20, 60),
        bgcolor = ft.Colors.SURFACE_CONTAINER,
        border_radius = 30,
        width = 760,
        height = 540
    )
    # threading.Thread(target = cv.update_frames, args = (page, camera_preview), daemon = True).start()
    
    
    # Database Tables
    dt_attendance = ft.DataTable(
        align = ft.Alignment.CENTER,
        width = WIDTH,
        expand = True,
        border = ft.Border.all(2, ft.Colors.SURFACE_BRIGHT),
        horizontal_lines = ft.border.BorderSide(1, ft.Colors.SURFACE_BRIGHT),
        # vertical_lines = ft.border.BorderSide(1, Colors.SURFACE_BRIGHT),
        heading_row_color = ft.Colors.SURFACE_CONTAINER_LOW,
        columns = [
            ft.DataColumn(ft.Text("DATE")),
            ft.DataColumn(ft.Text("TIME")),
            ft.DataColumn(ft.Text("NAME")),
            ft.DataColumn(ft.Text("STATUS")),
        ],
        rows = [], 
    )
    dt_classes = ft.DataTable(
        align = ft.Alignment.CENTER,
        width = WIDTH,
        expand = True,
        border = ft.Border.all(2, ft.Colors.SURFACE_BRIGHT),
        horizontal_lines = ft.border.BorderSide(1, ft.Colors.SURFACE_BRIGHT),
        # vertical_lines = ft.border.BorderSide(1, Colors.SURFACE_BRIGHT),
        heading_row_color = ft.Colors.SURFACE_CONTAINER_LOW,
        columns = [
            ft.DataColumn(ft.Text("DATE")),
            ft.DataColumn(ft.Text("TIME")),
            ft.DataColumn(ft.Text("SUBJECT CODE")),
            ft.DataColumn(ft.Text("INSTRUCTOR")),
        ],
        rows = [], 
    )

    # Database Retrievals and Updates
    def update_attendance_log():
        dt_attendance.rows.clear()
        
        cols, rows = db.get_attendance_log()
        for row in rows:
            if row['date']:
                date = str(row['date'])
            if row['time']:
                time = str(row['time'])
            
            dt_attendance.rows.append(
                ft.DataRow(
                    cells = [
                        ft.DataCell(ft.Text(date)),
                        ft.DataCell(ft.Text(time)),
                        ft.DataCell(ft.Text(row['student_name'])),
                        ft.DataCell(ft.Text(row['attendance_status'])),
                    ]
                )
            )
        
        page.update()
    
    def update_class_list():
        pass
    

    # ID Scanner page
    page_1 = ft.Container(
        ft.Row([
            video_container,
            ft.Container(
                margin = 20,
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
        ],)
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
                    height = 350,
                    content = ft.Column(
                        
                    )
                ),
                dt_classes
            ], 
            vertical_alignment = ft.CrossAxisAlignment.START,
            margin = 20, 
            spacing = 30,
        ),
    )

    # Dashboard page
    page_4 = ft.Container(ft.Text(value="4"))

    # Page Container
    current_page = ft.Container(content = page_1)

    # Navigation buttons
    def set_page(e):
        i = e.control.selected_index

        if i == 0:
            current_page.content = page_1
        elif i == 1:
            current_page.content = page_2
            update_attendance_log() # TODO: Transfer this function to be ran after each scan
        elif i == 2:
            current_page.content = page_3
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
    )
    # page.navigation_bar = navbar

    page.add(
        navbar,

        # Changeable content
        current_page
    )
    
    page.update()


# Run Flet app (Flutter my beloved!!)
if __name__ == "__main__":
    ft.run(main)