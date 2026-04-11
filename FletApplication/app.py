import base64
import asyncio
from datetime import datetime
import handlers.dbhandler as db
import flet as ft
import handlers.cvhandler

BG0 = "#171717"
BG1 = "#e8e4df"
BG2 = "#f3f3f3"
DK = "#2f2b28"
MD = "#6d655f"
LT = "#c3b9af"
AC = "#f4d400"
TX = "#232323"
BOX = "#f4f4f4"
ROWBG = "#f6f6f6"
BORDER = "#c8c8c8"

# 1x1 transparent PNG as a valid initial image source
EMPTY_IMG = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="


def main(page: ft.Page):
    # Functionality:
    # Main desktop application entry. Builds all screens and handles navigation.
    page.title = "Smart Attendance System"
    page.window_width = 1280
    page.window_height = 720
    page.bgcolor = BG0
    page.padding = 0
    page.spacing = 0
    page.theme_mode = "light"

    scanner_running = {"value": False}
    current_screen = {"value": "dashboard"}

    camera_image = ft.Image(
        src=EMPTY_IMG,
        width=760,
        height=430,
    )

    student_name_text = ft.Text("Waiting for scan...", size=14, color="#f2f2f2")
    student_id_text = ft.Text("Waiting for scan...", size=14, color="#f2f2f2")
    scan_status_text = ft.Text("No valid ID detected.", size=14, color=TX)
    scanner_clock_text = ft.Text(
        "APRIL 14, 2026 : TUESDAY  ||  9:49 AM",
        size=16,
        weight="bold",
        color="#171717",
    )

    def cap_bar(title):
        # Functionality:
        # Top caption bar matching the Flask layout.
        return ft.Container(
            height=28,
            bgcolor=BG0,
            padding=ft.padding.only(left=12, right=12, top=4, bottom=4),
            content=ft.Text(title, size=12, color="#8f8f8f"),
        )

    def stat_box(label, value, sub):
        # Functionality:
        # Dashboard statistic cards.
        return ft.Container(
            expand=1,
            bgcolor=BOX,
            padding=14,
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Text(label.upper(), size=11, weight="bold", color="#4b4b4b"),
                    ft.Text(value, size=21, weight="bold", color=TX),
                    ft.Text(sub, size=12, color="#4e4e4e"),
                ],
            ),
        )

    def panel_title(text):
        # Functionality:
        # Dark section title used on right-side info panels.
        return ft.Container(
            bgcolor=DK,
            padding=12,
            content=ft.Row(
                alignment="center",
                controls=[
                    ft.Text(text.upper(), size=14, weight="bold", color="white"),
                ],
            ),
        )

    def info_light(title, text_control):
        # Functionality:
        # Light info panel used by dashboard and scanner.
        return ft.Container(
            bgcolor=LT,
            padding=16,
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Text(title.upper(), size=12, weight="bold", color=TX),
                    text_control,
                ],
            ),
        )

    def progress_row(label):
        # Functionality:
        # Dashboard attendance distribution row.
        return ft.Row(
            controls=[
                ft.Container(
                    width=90,
                    content=ft.Text(label, size=12, color=TX),
                ),
                ft.Container(
                    expand=1,
                    height=12,
                    bgcolor="#efefef",
                    border=ft.border.all(1, BORDER),
                ),
            ]
        )

    def activity_table():
        # Functionality:
        # Dashboard recent activity placeholder table.
        rows = []
        for _ in range(4):
            rows.append(
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.Container(
                            width=90,
                            height=30,
                            border=ft.border.all(1, BORDER),
                            padding=ft.padding.symmetric(horizontal=8, vertical=6),
                            content=ft.Text("0:00", size=11),
                        ),
                        ft.Container(
                            expand=1,
                            height=30,
                            border=ft.border.all(1, BORDER),
                            padding=ft.padding.symmetric(horizontal=8, vertical=6),
                            content=ft.Text("No activity available", size=11),
                        ),
                    ],
                )
            )
        return ft.Column(spacing=0, controls=rows)

    def table_header(labels, widths):
        # Functionality:
        # Generic table header for log and class pages.
        cells = []
        for i, label in enumerate(labels):
            cells.append(
                ft.Container(
                    expand=widths[i],
                    bgcolor="#cfcfcf",
                    border=ft.border.all(1, "#cfcfcf"),
                    padding=10,
                    content=ft.Text(label.upper(), size=11, weight="bold"),
                )
            )
        return ft.Row(spacing=0, controls=cells)

    def table_row(values, widths):
        # Functionality:
        # Generic placeholder row matching the Flask tables.
        cells = []
        for i, value in enumerate(values):
            cells.append(
                ft.Container(
                    expand=widths[i],
                    bgcolor=ROWBG,
                    border=ft.border.all(1, "#d7d7d7"),
                    padding=10,
                    height=42,
                    content=ft.Text(value, size=11),
                )
            )
        return ft.Row(spacing=0, controls=cells)

    def pill_button(text, on_click=None):
        # Functionality:
        # Dark rounded button similar to Flask buttons.
        return ft.ElevatedButton(
            content=ft.Text(text.upper(), color="white", size=12, weight="bold"),
            on_click=on_click,
            style=ft.ButtonStyle(
                bgcolor=DK,
                padding=ft.padding.symmetric(horizontal=18, vertical=10),
                shape=ft.RoundedRectangleBorder(radius=999),
            ),
        )

    def nav_button(label, key):
        # Functionality:
        # Top navigation button matching the Flask tab bar.
        active = current_screen["value"] == key
        bg = AC if active else BG2
        color = "#171717" if active else "#3b3b3b"

        return ft.Container(
            expand=1,
            height=54,
            bgcolor=bg,
            border=ft.border.only(bottom=ft.BorderSide(2, "#c0b8b1")),
            content=ft.TextButton(
                content=ft.Text(label.upper(), size=12, weight="bold", color=color),
                on_click=lambda e, dest=key: navigate(dest),
                style=ft.ButtonStyle(
                    padding=12,
                    shape=ft.RoundedRectangleBorder(radius=0),
                ),
            ),
        )

    def nav_bar():
        # Functionality:
        # Main tab navigation bar shared by the main Flask-like pages.
        return ft.Row(
            spacing=0,
            controls=[
                nav_button("Dashboard", "dashboard"),
                nav_button("Scanner", "scanner"),
                nav_button("Attendance Log", "attendance_log"),
                nav_button("Class List", "class_list"),
            ],
        )

    def dashboard_page():
        # Functionality:
        # Dashboard page imitating the Flask dashboard layout.
        left = ft.Column(
            expand=2,
            spacing=12,
            controls=[
                ft.Row(
                    spacing=12,
                    controls=[
                        stat_box("Present", "0% Present", "0 out of 0"),
                        stat_box("Late", "0% Late", "0 out of 0"),
                        stat_box("Absent", "0% Absent", "0 out of 0"),
                    ],
                ),
                ft.Row(
                    spacing=12,
                    controls=[
                        ft.Container(
                            expand=2,
                            bgcolor=BOX,
                            padding=14,
                            content=ft.Column(
                                spacing=12,
                                controls=[
                                    ft.Text("Attendance Distribution", size=13),
                                    progress_row("Present"),
                                    progress_row("Late"),
                                    progress_row("Absent"),
                                ],
                            ),
                        ),
                        ft.Container(
                            expand=1,
                            bgcolor=BOX,
                            content=ft.Row(
                                alignment="center",
                                vertical_alignment="center",
                                controls=[
                                    ft.Container(
                                        width=95,
                                        height=95,
                                        bgcolor="#df5b51",
                                        border_radius=100,
                                        content=ft.Row(
                                            alignment="center",
                                            vertical_alignment="center",
                                            controls=[
                                                ft.Container(
                                                    width=40,
                                                    height=40,
                                                    bgcolor=BOX,
                                                    border_radius=100,
                                                )
                                            ],
                                        ),
                                    )
                                ],
                            ),
                        ),
                        ft.Container(
                            expand=2,
                            bgcolor=BOX,
                            padding=14,
                            content=ft.Column(
                                controls=[
                                    ft.Text("Top Performing Students", size=13),
                                    ft.Container(
                                        expand=1,
                                        content=ft.Row(
                                            alignment="center",
                                            vertical_alignment="center",
                                            controls=[
                                                ft.Text("No records available", size=12, color="#767676"),
                                            ],
                                        ),
                                    ),
                                ],
                            ),
                        ),
                    ],
                ),
                ft.Container(
                    expand=1,
                    bgcolor=BOX,
                    padding=14,
                    content=ft.Column(
                        controls=[
                            ft.Text("Recent Activity", size=13),
                            activity_table(),
                        ],
                    ),
                ),
                ft.Container(
                    height=55,
                    bgcolor=AC,
                    content=ft.Row(
                        alignment="center",
                        vertical_alignment="center",
                        controls=[
                            ft.Text(
                                "MON, FEB 16, 2026  ||  11:00 AM",
                                size=16,
                                weight="bold",
                                color="#171717",
                            )
                        ],
                    ),
                ),
            ],
        )

        right = ft.Column(
            expand=1,
            spacing=12,
            controls=[
                panel_title("Class Overview"),
                ft.Container(
                    bgcolor=MD,
                    padding=16,
                    content=ft.Column(
                        spacing=18,
                        controls=[
                            ft.Column(
                                spacing=4,
                                controls=[
                                    ft.Text("CLASS", size=12, weight="bold", color="#f2f2f2"),
                                    ft.Text("ICT 110", size=14, color="#f2f2f2"),
                                ],
                            ),
                            ft.Column(
                                spacing=4,
                                controls=[
                                    ft.Text("SUMMARY", size=12, weight="bold", color="#f2f2f2"),
                                    ft.Text(
                                        "Attendance monitoring dashboard with live scanner integration and student attendance tracking.",
                                        size=14,
                                        color="#f2f2f2",
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
                info_light("Current Status", ft.Text("No active attendance record yet.", size=14, color=TX)),
            ],
        )

        return ft.Row(expand=1, spacing=14, controls=[left, right])

    async def camera_loop():
        # Functionality:
        # Continuously refreshes the scanner frame and the scan details.
        while scanner_running["value"]:
            frame = handlers.cvhandler.get_processed_frame()
            frame_bytes = handlers.cvhandler.frame_to_jpeg_bytes(frame)

            if frame_bytes:
                # CHANGED: old Flet version supports src, not src_base64
                camera_image.src = "data:image/jpeg;base64," + base64.b64encode(frame_bytes).decode("utf-8")
            else:
                camera_image.src = EMPTY_IMG

            scan = handlers.cvhandler.get_scan_data()
            student_name_text.value = scan.get("student_name", "") or "Waiting for scan..."
            student_id_text.value = scan.get("student_id", "") or "Waiting for scan..."

            status_value = scan.get("status", "") or "No valid ID detected."
            if frame is None:
                status_value = "Camera frame not available."

            scan_status_text.value = status_value

            val = scan_status_text.value.lower()
            if "success" in val or "recorded" in val:
                scan_status_text.color = "#1f8d3b"
            elif "failed" in val or "not found" in val or "not enrolled" in val or "record" in val or "camera" in val:
                scan_status_text.color = "#b93a3a"
            else:
                scan_status_text.color = TX

            now = datetime.now()
            weekday = now.strftime("%A").upper()
            month = now.strftime("%B").upper()
            hour_12 = now.strftime("%I").lstrip("0") or "12"
            scanner_clock_text.value = f"{month} {now.day}, {now.year} : {weekday}  ||  {hour_12}:{now.strftime('%M')} {now.strftime('%p')}"

            page.update()
            await asyncio.sleep(0.1)

    def scanner_page():
        # Functionality:
        # Scanner page imitating the Flask scanner layout.
        left = ft.Column(
            expand=2,
            spacing=12,
            controls=[
                ft.Container(
                    expand=1,
                    bgcolor="#1c1c1f",
                    padding=10,
                    content=ft.Row(
                        alignment="center",
                        vertical_alignment="center",
                        controls=[camera_image],
                    ),
                ),
                ft.Container(
                    height=55,
                    bgcolor=AC,
                    content=ft.Row(
                        alignment="center",
                        vertical_alignment="center",
                        controls=[scanner_clock_text],
                    ),
                ),
            ],
        )

        right = ft.Column(
            expand=1,
            spacing=12,
            controls=[
                panel_title("Student Information"),
                ft.Container(
                    bgcolor=MD,
                    padding=16,
                    content=ft.Column(
                        spacing=18,
                        controls=[
                            ft.Column(
                                spacing=4,
                                controls=[
                                    ft.Text("STUDENT NAME", size=12, weight="bold", color="#f2f2f2"),
                                    student_name_text,
                                ],
                            ),
                            ft.Column(
                                spacing=4,
                                controls=[
                                    ft.Text("STUDENT ID", size=12, weight="bold", color="#f2f2f2"),
                                    student_id_text,
                                ],
                            ),
                        ],
                    ),
                ),
                info_light("Scan Status", scan_status_text),
            ],
        )

        return ft.Row(expand=1, spacing=14, controls=[left, right])

    def attendance_log_page():
        # Functionality:
        # Attendance log page imitating the Flask attendance log layout.
        widths = [1, 1, 2, 1]
        rows = [table_row(["", "", "", ""], widths) for _ in range(7)]

        return ft.Container(
            expand=1,
            margin=ft.margin.symmetric(horizontal=18, vertical=18),
            content=ft.Column(
                spacing=0,
                controls=[
                    table_header(["Date & Time", "Student ID", "Student Name", "Status"], widths),
                    ft.Container(
                        expand=1,
                        bgcolor=ROWBG,
                        content=ft.Column(spacing=0, controls=rows),
                    ),
                ],
            ),
        )

    def class_list_page():
        # Functionality:
        # Class list page imitating the Flask class list layout.
        widths = [1, 1, 3]
        rows = [table_row(["", "", ""], widths) for _ in range(6)]

        search_bar = ft.Container(
            width=220,
            height=34,
            bgcolor="#f8f8f8",
            border=ft.border.all(1, BORDER),
            border_radius=999,
            padding=ft.padding.symmetric(horizontal=14, vertical=8),
            content=ft.Row(
                alignment="spaceBetween",
                controls=[
                    ft.Text("", size=11, color="#666"),
                    ft.Text("⌕", size=12, color="#666"),
                ],
            ),
        )

        return ft.Column(
            expand=1,
            spacing=10,
            controls=[
                ft.Row(
                    alignment="spaceBetween",
                    controls=[
                        search_bar,
                        pill_button("New Sheet", lambda e: navigate("class_item")),
                    ],
                ),
                ft.Container(
                    expand=1,
                    content=ft.Column(
                        spacing=0,
                        controls=[
                            table_header(["Date", "Subject Code", "Descriptive Title"], widths),
                            ft.Container(
                                expand=1,
                                bgcolor=ROWBG,
                                content=ft.Column(spacing=0, controls=rows),
                            ),
                        ],
                    ),
                ),
            ],
        )

    def class_item_page():
        # Functionality:
        # Class item page imitating the Flask class item layout.
        widths = [1, 1, 2, 1]
        rows = [table_row(["", "", "", ""], widths) for _ in range(5)]

        return ft.Column(
            expand=1,
            spacing=12,
            controls=[
                ft.Row(
                    controls=[
                        ft.TextButton(
                            content=ft.Text("‹", size=22, weight="bold", color="#2f2f2f"),
                            on_click=lambda e: navigate("class_list"),
                        ),
                        ft.Container(
                            expand=1,
                            content=ft.Text(
                                "APRIL 14, 2026 : TUESDAY  ||  9:49 AM  ||  ICT-110",
                                size=13,
                                weight="bold",
                                color="#5c437e",
                            ),
                        ),
                    ],
                ),
                ft.Container(
                    expand=1,
                    content=ft.Column(
                        spacing=0,
                        controls=[
                            table_header(["Time", "Student ID", "Student Name", "Status"], widths),
                            ft.Container(
                                expand=1,
                                bgcolor=ROWBG,
                                content=ft.Column(spacing=0, controls=rows),
                            ),
                        ],
                    ),
                ),
                ft.Row(
                    alignment="end",
                    controls=[
                        pill_button("Export Sheet"),
                    ],
                ),
            ],
        )

    def page_body():
        # Functionality:
        # Returns the content area according to the current selected screen.
        key = current_screen["value"]

        if key == "dashboard":
            return dashboard_page()
        if key == "scanner":
            return scanner_page()
        if key == "attendance_log":
            return attendance_log_page()
        if key == "class_list":
            return class_list_page()
        if key == "class_item":
            return class_item_page()

        return dashboard_page()

    def frame_title():
        # Functionality:
        # Maps route keys to visible top caption text.
        titles = {
            "dashboard": "Dashboard",
            "scanner": "Scanner",
            "attendance_log": "Attendance Log",
            "class_list": "Class List",
            "class_item": "Class Item",
        }
        return titles.get(current_screen["value"], "Dashboard")

    def build_shell():
        # Functionality:
        # Rebuilds the full shell, frame, nav, and page content.
        frame_controls = []

        if current_screen["value"] != "class_item":
            frame_controls.append(nav_bar())

        frame_controls.append(
            ft.Container(
                expand=1,
                padding=18,
                content=page_body(),
            )
        )

        return ft.Column(
            expand=1,
            spacing=0,
            controls=[
                cap_bar(frame_title()),
                ft.Container(
                    expand=1,
                    padding=6,
                    bgcolor=BG0,
                    content=ft.Container(
                        expand=1,
                        bgcolor=BG1,
                        border=ft.border.all(1, "#2f2f2f"),
                        content=ft.Column(
                            expand=1,
                            spacing=0,
                            controls=frame_controls,
                        ),
                    ),
                ),
            ],
        )

    def navigate(dest):
        # Functionality:
        # Handles page switching and scanner start-stop behavior.
        current_screen["value"] = dest

        if dest == "scanner":
            scanner_running["value"] = True
        else:
            scanner_running["value"] = False
            handlers.cvhandler.release_camera()

        page.clean()
        page.add(build_shell())
        page.update()

        if dest == "scanner":
            page.run_task(camera_loop)

    def on_window_event(e):
        # Functionality:
        # Releases camera resources when the app window closes.
        if getattr(e, "data", "") == "close":
            scanner_running["value"] = False
            handlers.cvhandler.release_camera()

    page.window.on_event = on_window_event
    navigate("dashboard")


ft.app(target=main)