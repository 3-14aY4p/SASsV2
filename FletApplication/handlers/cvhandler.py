import cv2
import base64
import time
import pytesseract
import re


# tesseract config
conf = r"--psm 7 --oem 1 tessedit_char_whitelist=0123456789-AI"

def extract_id(roi):
    rz = 3  # resize multiplier

    # preprocessing stuffs; cleaning up the image
    p_img = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    p_img = cv2.resize(p_img, None, fx=rz, fy=rz, interpolation=cv2.INTER_CUBIC)
    p_img = cv2.GaussianBlur(p_img, (5, 5), 0)
    _, p_img = cv2.threshold(p_img, 0, 255,
         cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # text extraction
    text = pytesseract.image_to_string(p_img, config=conf)
    text = text.strip()

    # FIXME: correct the program in mistaking -I as 4
    if re.match(r"\d{4}-\d{4}4", text):
        text = text[:-1] + "-I"

    # return match result if it exists
    match = re.search(r"\d{4}-\d{4}-[A-Z]", text)
    if match:
        return match.group()
    else:
        return None


def update_frames(page, image_control, on_detect):
    camera = cv2.VideoCapture(0)
    
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    camera.set(cv2.CAP_PROP_FPS, 15)

    last_detected = None

    while True:
        ret, frame = camera.read()
        if not ret:
            time.sleep(0.033)
            continue

        h, w = frame.shape[:2]

        # Scan box — wide and short
        box_w, box_h = 320, 80
        x1 = (w - box_w) // 2
        y1 = (h - box_h) // 2
        x2 = x1 + box_w
        y2 = y1 + box_h

        # Crop region inside box and run OCR
        roi = frame[y1:y2, x1:x2]
        detected = extract_id(roi)

        if detected and detected != last_detected:
            last_detected = detected
            on_detect(detected)

        # Draw red scan box on frame
        color = (0, 0, 255)
        cv2.line(frame, (x1,y1), (x1+15,y1), color, 2)
        cv2.line(frame, (x1,y1), (x1,y1+15), color, 2)
        cv2.line(frame, (x1,y2), (x1+15,y2), color, 2)
        cv2.line(frame, (x1,y2), (x1,y2-15), color, 2)
        cv2.line(frame, (x2,y1), (x2-15,y1), color, 2)
        cv2.line(frame, (x2,y1), (x2,y1+15), color, 2)
        cv2.line(frame, (x2,y2), (x2-15,y2), color, 2)
        cv2.line(frame, (x2,y2), (x2,y2-15), color, 2)

        ok, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
        if ok:
            frame_b64 = base64.b64encode(buffer).decode()

            async def do_update(b64 = frame_b64):
                image_control.src = f"data:image/jpeg;base64,{b64}"
                image_control.update()

            page.run_task(do_update)

        time.sleep(0.066)