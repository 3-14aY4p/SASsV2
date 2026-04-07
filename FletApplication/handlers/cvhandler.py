import cv2, time, threading


camera = cv2.VideoCapture(0)

def update_frames(page, camera_preview):
    while camera.isOpened():
        ret, frame = camera.read()
        if not ret:
            continue
            
        frame_bytes = cv2.imencode('.png', frame)[1].tobytes()
        camera_preview.src = frame_bytes
        
        page.update()

    time.sleep(1/30)

threading.Thread(target=update_frames, daemon=True).start()