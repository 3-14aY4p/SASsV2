

import base64
import json
import os
import tempfile
import cv2
import flet as ft
import threading
import pandas as pd
from io import BytesIO
from process.measurement import measure
from process.calibration import calibration
# from process.coin_detect import detect_onnx
from process.onnx_rt import build_model, process_frame
import sys
stop_flags = {
    0: threading.Event(),
    1: threading.Event()
}
from datetime import datetime
now = datetime.now()
formatted_date = now.strftime("%d %B %Y, %H:%M")
def write_json(new_data, filename="results.json"):
    with open(filename, 'r+') as file:
        file_data = json.load(file)
        file_data["results"].append({
            "data": new_data,
            "date": formatted_date
        })
        
        file.seek(0)
        json.dump(file_data, file, indent=4)
        file.truncate()
selected_index = 0
measurement_result = [0, 0, 0, 0,0]
def load_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data
def main(page: ft.Page):
    page.window_width = 1024
    page.window_height = 600
    
    def change_content(index):
        content_container.controls.clear()  
        if index == 0:
            content_container.controls.append(home())
        elif index == 1:
            content_container.controls.append(kalibrasi())
        elif index == 2:
            content_container.controls.append(pengukuran())
        elif index == 3:
            content_container.controls.append(riwayat())
        elif index == 11:
            content_container.controls.append(pengukuran2())
        elif index == 12:
            content_container.controls.append(result())
        page.update()
        
    def stop_all_cameras(e):
        stop_flags[0].set()
        stop_flags[1].set()
        print("Cameras stopped.")
    
    def capture_image(vc_index, filename):
    # Open a connection to the camera
        vc = cv2.VideoCapture(vc_index)

        if not vc.isOpened():
            print(f"Failed to open Camera {vc_index}")
            return

        # Capture a single frame
        rval, frame = vc.read()

        if rval:
            # Save the captured frame to a file
            cv2.imwrite(filename, frame)
            print(f"Image saved to {filename}")

        # Release the camera
        vc.release()
    
    def update_frame(image_file, img_control):
        img_control.src_base64 = image_file.decode('utf-8')
        page.update(img_control)
    
    def capture_pengukuran1(e):
        
        capture_image(0, 'pengukuran1.jpg')
        stop_flags[0].set()
        change_content(11)
    
    def capture_pengukuran2(e):
        capture_image(1, 'pengukuran2.jpg')
        # stop_all_cameras(None)
        stop_flags[1].set()
        global measurement_result
        # result = measure("images/tes2/baby_up.jpeg", "images/tes2/baby_side.jpeg")
        result = measure("pengukuran1.jpg", "pengukuran2.jpg")
        print(result)
        measurement_result = result
        if(result):
            change_content(12)
        else:
            print("Ada masalah dalam pengukuran")
    def capture_all_images(e):
        
        # Capture images from both cameras
        capture_image(0, 'calibration1.jpg')
        capture_image(1, 'calibration2.jpg')
        stop_all_cameras(None)
        calibration("calibration1.jpg", "calibration2.jpg")
        # Optionally, you can update the images on the Flet UI after capturing
        # update_frame_from_file('camera0_image.jpg', img)
        # update_frame_from_file('camera1_image.jpg', img1)
    
    def update_frame_from_file(filename, img_control):
        with open(filename, 'rb') as file:
            image_file = base64.b64encode(file.read())
            update_frame(image_file, img_control)

    def start_video(vc_index, img_control):
        is_cuda = len(sys.argv) > 1 and sys.argv[1] == "cuda"
        net = build_model(is_cuda, "model/best.onnx")
        vc = cv2.VideoCapture(vc_index)

        if not vc.isOpened():
            print(f"Failed to open Camera {vc_index}")
            return

        while not stop_flags[vc_index].is_set():
            rval, frame = vc.read()
            if not rval:
                break
            # print(selected_index)
            if(selected_index == 1):
                frame = process_frame(frame, net)
            _, im_arr = cv2.imencode('.jpg', frame)
            im_bytes = im_arr.tobytes()
            im_b64 = base64.b64encode(im_bytes)
            update_frame(im_b64, img_control)
            
            # Introduce a small delay to prevent overloading the CPU
            cv2.waitKey(1)

        vc.release()

    def start_all_cameras(e):
        for key in stop_flags.keys():
            stop_flags[key].clear()
        threading.Thread(target=start_video, args=(0, img)).start()
        threading.Thread(target=start_video, args=(1, img1)).start()
    
    def start_camera_pengukuran(e):
        for key in stop_flags.keys():
            stop_flags[key].clear()
        threading.Thread(target=start_video, args=(0, img2)).start()
        threading.Thread(target=start_video, args=(1, img3)).start()
    result_data = load_json('results.json')
    assets_dir = os.path.join(os.getcwd(), "assets")

    # Membuat direktori untuk menyimpan file sementara jika belum ada
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)

    def download_action(e,i):
        file_data = download(i)
        with tempfile.NamedTemporaryFile(delete=False, dir=assets_dir, suffix=".xlsx") as tmp:
            with open(tmp.name, 'wb') as f:
                f.write(file_data.getvalue())
            # Menggunakan launch_url untuk membuka file
            e.page.launch_url(f"file://{tmp.name}", web_window_name='_self')
    def download(i):
        if i == "all":
            # Mengambil semua data
            data_list = [entry["data"] for entry in result_data["results"]]
            dates = [entry["date"] for entry in result_data["results"]]
            df = pd.DataFrame(data_list)
            df["date"] = dates
        else:
            i = int(i)
            data_entry = result_data["results"][i]["data"]
            date = result_data["results"][i]["date"]
            df = pd.DataFrame([data_entry])
            df["date"] = [date]
        file_data = BytesIO()
        df.to_excel(file_data, index=False, engine='openpyxl')
        file_data.seek(0) 
        return file_data
    
    def riwayat():
        
        # print(data)
        lv = ft.ListView(expand=True, spacing=20, padding=20)
        for i in range(len(result_data["results"])-1,0,-1):
            lv.controls.append(
                ft.Card(
                    ft.Container(
                        padding=ft.padding.all(20),
                        content=ft.Row(
                        [
                            
                            ft.Row([
                                ft.Text(f"ID{i}"),
                                ft.Text(result_data["results"][i]["date"]),
                                ]),
                            ft.Row(
                                [
                                    
                                    ft.Text(result_data["results"][i]["data"]["head"]),
                                    ft.Text(result_data["results"][i]["data"]["abdomen"]),
                                    ft.Text(result_data["results"][i]["data"]["chest"]),
                                    ft.Text(result_data["results"][i]["data"]["leg"]),
                                    ft.Text(result_data["results"][i]["data"]["height"])
                                    
                                    
                                ]
                            ),
                            ft.IconButton("Download", on_click=lambda e, i=i: download_action(e,i)),
                            
                            
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    )
                    )
                )
            )
        return ft.Column([
            ft.Container(
                ft.ElevatedButton(
                "Download Excel",icon=ft.icons.DOWNLOAD, on_click=lambda e: download_action(e,"all")), padding=ft.padding.all(20)),
            lv
        ],
        horizontal_alignment=ft.CrossAxisAlignment.END)
        
    def result():
        return ft.Container(
            padding=ft.padding.all(20),
            content=ft.Column(
                [
                    # ft.Text("Hasil Pengukuran", weight=ft.FontWeight.BOLD),
                    ft.DataTable(
            vertical_lines=ft.BorderSide(1, ft.colors.PRIMARY),
            columns=[
                ft.DataColumn(ft.Text("Hasil Pengukuran", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Nilai", weight=ft.FontWeight.BOLD), numeric=True),
                # ft.DataColumn(ft.Text("Age"), numeric=True),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("Tinggi")),
                        # ft.DataCell(ft.Text("Smith")),
                        ft.DataCell(ft.Text(measurement_result[5])),
                    ],
                ),
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("Lingkar Kepala")),
                        # ft.DataCell(ft.Text("Brown")),
                        ft.DataCell(ft.Text(measurement_result[0])),
                    ],
                ),
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("Lingkar Dada")),
                        ft.DataCell(ft.Text(measurement_result[1])),
                    ],
                ),
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("Lingkar Perut")),
                        ft.DataCell(ft.Text(measurement_result[2])),
                    ],
                ),
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("Lingkar Kaki")),
                        ft.DataCell(ft.Text(measurement_result[4])),
                    ],
                ),
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("Lingkar Lengan")),
                        ft.DataCell(ft.Text(measurement_result[3])),
                    ],
                ),
            ],
        )

                ]
        ))
    def home():
        return ft.Column(
            [
                ft.Container(
                    padding=ft.padding.all(20),
                    content =
                ft.Card(
                    content=ft.Container(
                    content=ft.Row(
                        [
                           ft.Column([
                            ft.Text("Antropometri Bayi Digital", weight=ft.FontWeight.BOLD),
                           ft.Text("Antropometri Bayi Digital", weight=ft.FontWeight.W_100, size=12),
                           ]),
                           ft.Card(
                               content=ft.Container(
                                   ft.Image(
                                        src=f"images/baby.png",
                                        width=100,
                                        height=100,
                                    ),
                                   bgcolor=ft.colors.PRIMARY_CONTAINER,
                                   border_radius=10,
                                   padding=ft.padding.all(10),
                               )
                           )
                        ],
                        spacing=10,
                        tight=True
                    ),
                    padding=ft.padding.all(20),
                    ),
                    elevation=2,
                )
                )
            ],
            alignment=ft.CrossAxisAlignment.CENTER,
        )
    def kalibrasi():
        return ft.Column(
            
            [
                ft.Container(expand=True),
                ft.Container(
                    ft.Row([img, img1], alignment=ft.MainAxisAlignment.CENTER),
                    # padding=ft.padding.only(left=10, right=10),
                    padding=ft.padding.all(20),
                    
                ),
                ft.Container(
                    ft.Row(
                    [
                        ft.ElevatedButton("Mulai Kalibrasi (Kamera)", on_click=start_all_cameras),
                        ft.OutlinedButton("Hentikan Pengukuran", on_click=capture_all_images ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    
                    spacing=20
                ),
                    padding=ft.padding.only(bottom=40),
                    expand=True
                )
            ],
            alignment=ft.MainAxisAlignment.START,
            expand=True
        )
    def pengukuran():
        return ft.Column(
            [
                ft.Container(
                    ft.Row([img2], alignment=ft.MainAxisAlignment.CENTER),
                    # padding=ft.padding.only(left=10, right=10),
                    padding=ft.padding.all(20),
                    
                ),
                ft.Container(
                    ft.Row(
                        
                    [
                        ft.ElevatedButton("Mulai Kamera", on_click=start_camera_pengukuran),
                        ft.OutlinedButton("Lanjutkan", on_click=capture_pengukuran1 ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                ),
                    padding=ft.padding.only(bottom=20),
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    def pengukuran2():
        return ft.Column(
            [
                ft.Container(
                    ft.Row([img3], alignment=ft.MainAxisAlignment.CENTER),
                    # padding=ft.padding.only(left=10, right=10),
                    padding=ft.padding.all(20),
                    
                ),
                ft.Container(
                    ft.Row(
                    [
                        ft.OutlinedButton("Kembali", on_click=lambda e: change_content(2)),
                        ft.ElevatedButton("Mulai Pengukuran", on_click=capture_pengukuran2 ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                ),
                    padding=ft.padding.only(bottom=20),
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        

    
    def on_change(e):
        global selected_index  # Use global to modify the global variable
        selected_index = e.control.selected_index
        change_content(selected_index)
        # if(selected_index == 1 | selected_index == 2):
        if(selected_index == 1):
            stop_all_cameras(None)
        if(selected_index == 2):
            stop_all_cameras(None)
        
    img = ft.Image(
        src='./frames/frame0.png',
        # width=400,
        height=250,
        fit=ft.ImageFit.CONTAIN,
        gapless_playback=True
    )

    img1 = ft.Image(
        src='./frames/frame0.png',
        # width=00,
        height=250,
        fit=ft.ImageFit.CONTAIN,
        gapless_playback=True
    )
    img2 = ft.Image(
        src='./frames/frame0.png',
        # width=00,
        height=400,
        fit=ft.ImageFit.CONTAIN,
        gapless_playback=True
    )
    img3 = ft.Image(
        src='./frames/frame0.png',
        # width=00,
        height=400,
        fit=ft.ImageFit.CONTAIN,
        gapless_playback=True
    )
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(
                label="Home",
                icon=ft.icons.HOME_OUTLINED,
                selected_icon_content=ft.Icon(ft.icons.HOME),
            ),
            ft.NavigationRailDestination(
                icon_content=ft.Icon(ft.icons.LINEAR_SCALE_OUTLINED),
                label="Kalibrasi",
                selected_icon=ft.icons.LINEAR_SCALE_ROUNDED,
            ),
            ft.NavigationRailDestination(
                icon_content=ft.Icon(ft.icons.CAMERA_OUTLINED),
                label="Pengukuran",
                selected_icon=ft.icons.CAMERA,
            ),
            ft.NavigationRailDestination(
                icon_content=ft.Icon(ft.icons.HISTORY_OUTLINED),
                label="Riwayat",
                selected_icon=ft.icons.MANAGE_HISTORY,
            ),
            ft.NavigationRailDestination(
                icon_content=ft.Icon(ft.icons.BOOK_OUTLINED),
                label="Petunjuk",
                selected_icon=ft.icons.BOOK,
            ),
        ],
        on_change=on_change, 
    )

    content_container = ft.Column(expand=True)
    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1),
                content_container
            ],
            expand=True
        )
    )

    page.dark_theme = ft.Theme(color_scheme_seed="indigo")
    page.theme = ft.Theme(color_scheme_seed="indigo")
    page.theme_mode = ft.ThemeMode.LIGHT
    page.update()

    change_content(0)

ft.app(main)