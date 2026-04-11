# This is a script to display video in Flet
# It's a pretty simple script
# TL;DR - It's a Flet application with an image control
# and a basic opencv video capture from a webcame
# Only difference, is that the frame data is converted into a base64 image
# And that is then passed to a function 'update frame' that
# Decodes the base64 using utf-8 and tells the page to update
# Has to be put into it's own function as the image controle refused to update 
# while in the 'while' loop

import cv2 # import opencv to read from the webcame
import flet as ft # import flet as this handles our UI
import base64 # import base64 so flet can read the image without having to save it



# Main class -> Basic flet setup
def main(page: ft.Page):
    page.title = "Video"
    page.update()
   
    # Update Frame Function --> this takes a base64 encoded string and decodes it with utf-8
    # It then sets the image source to this decoded base64 string
    # Then it updates the page
    def update_frame(image_file):
        print('Updating Video Frame')
        img.src_base64 = image_file.decode('utf-8')
        page.update(img)

    # Start Video runs when the start video button is pressed.
    def start_video(e):
        print("Starting Video Feed......")

        # Open a new connction to the webcam
        # The 0 may need to be changed to a different number depending on where your computer
        # Is reading the input from. When dev started it was 4......
        vc = cv2.VideoCapture(0)

        # if it's open then get the frame data
        if vc.isOpened():
            rval, frame = vc.read()
        else:
            rval = False
        
        # while loop will run while there is still input from the camera
        while rval:
            
            # read in the new frame data (next frame/image)
            rval, frame = vc.read()
            
            # convert the frame to .jpg without saving it
            _, im_arr = cv2.imencode('.jpg', frame)
            
            # covert the image into bytes
            im_bytes = im_arr.tobytes()

            # convert the bytes into base64
            im_b64 = base64.b64encode(im_bytes)
            
            # pass that base64 string to the image control
            update_frame(im_b64)
           
            # cancel the stream if the escape key is pressed
            # in theory it would, but it actually doesn't. 
            # Probably because the cv2 window isn't being used but have not confirmed at this time
            # leaving in nonetheless.
            key = cv2.waitKey(20)
            if key == 27:
                break

        # release control of the camera
        vc.release()

    # creates the image control for flet
    img = ft.Image(
        # this requires a default image. Leaving frames folder and frame0 from when testing was happening
        src='./frames/frame0.png',
        width=500,
        height=500,
        fit =  ft.BoxFit.CONTAIN,

        # supposed to help with playback, but unsure if needed. 
        gapless_playback=True,
            )

    # the button to press to start the video
    button_video = ft.ElevatedButton("Start Video", on_click=start_video) 
    
    # add the button to the page to be displayed
    page.add(img, button_video,)

# run the app
ft.app(target=main)