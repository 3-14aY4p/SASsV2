# Module/Library imports
from flet import MainAxisAlignment
from flet import *
import threading

# Custom files for handling
import handlers.dbhandler as db
import handlers.cvhandler as cv


# Main structure; We gotta put it all here!!
def main(page: Page):
    # Page settings
    page.title = "SASs: Smart Attendance System"
    page.theme_mode = ThemeMode.DARK
    
    WIDTH, HEIGHT = 1280, 720

    page.window_resizable = False
    page.window.width  = WIDTH
    page.window.height = HEIGHT


    # Camera Vision stuff; still broken
    frame_bytes = None
    camera_preview = Image(
        src = frame_bytes,
        fit = BoxFit.FILL
    )
    video_container = Container(
        content = camera_preview,
        margin = 20,
        bgcolor = Colors.SURFACE_CONTAINER,
        border_radius = 30,
        width = 760,
        height = 580
    )
    threading.Thread(target = cv.update_frames, args = (page, camera_preview), daemon = True).start()
    
    # Database Display
    dt_attendance = DataTable(
        align = Alignment.CENTER,
        column_spacing = WIDTH/5,
        columns = [
            DataColumn(Text("Date")),
            DataColumn(Text("Time")),
            DataColumn(Text("Student Name")),
            DataColumn(Text("Student ID")),
        ],
        rows = [],
    )



    # ID Scanner page
    page_1 = Container(
        Row([
            video_container,
            Container(
                margin = 20,
                width = 410,
                height = 580,
                content = Container(
                    Column([
                        Container(
                            bgcolor = Colors.SURFACE_CONTAINER,
                            border_radius = 30,
                            width = 410,
                            height = 100,
                            content = Column([
                                Text(
                                    value = "SCANNER STATUS", 
                                    align = Alignment.CENTER,
                                    style = TextStyle(
                                        weight = FontWeight.BOLD,
                                        size = 25,
                                        color = Colors.SURFACE_BRIGHT
                                    )
                                ),
                                Text(
                                    value = "waiting for scan...", 
                                    align = Alignment.CENTER,
                                    style = TextStyle(
                                        size = 20,
                                        color = Colors.SURFACE_BRIGHT
                                    )
                                )
                            ], margin = 10,
                            )
                        ),
                        Container(
                            bgcolor = Colors.SURFACE_CONTAINER,
                            border_radius = 30,
                            width = 410,
                            height = 300,
                        ),
                    ])
                )
            )
        ])
    )

    # Attendance Log page
    page_2 = Container(
        dt_attendance
    )

    # Class List page
    page_3 = Container(Text(value="3"))

    # Dashboard page
    page_4 = Container(Text(value="4"))

    current_page = Container(content = page_1)

    # Navigation buttons
    def set_page(e):
        i = e.page.navigation_bar.selected_index

        if i == 0:
            current_page.content = page_1
        elif i == 1:
            current_page.content = page_2
        elif i == 2:
            current_page.content = page_3
        elif i == 3:
            current_page.content = page_4
        page.update()
    
    navbar = NavigationBar(destinations = [
        NavigationBarDestination(
            icon = Icons.IMAGE,
            label = "ID Scanner"
        ),
        NavigationBarDestination(
            icon = Icons.ASSIGNMENT,
            label = "Attendance Log"
        ),
        NavigationBarDestination(
            icon = Icons.CLASS_,
            label = "Class List"
        ),
        NavigationBarDestination(
            icon = Icons.ANALYTICS,
            label = "Dashboard"
        ),],
        on_change = set_page,
        selected_index = 0,
    )
    page.navigation_bar = navbar

    page.add(
        current_page
    )
    
    page.update()


# Run Flet app (Flutter my beloved!!)
if __name__ == "__main__":
    run(main)