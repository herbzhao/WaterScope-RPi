from __future__ import division


# import the necessary packages
from picamera.array import PiRGBArray
import picamera
import io
import time
import cv2
import numpy as np



def variance_of_laplacian(image):
    ''' focus detection ''' 
    # compute the Laplacian of the image and then return the focus
    # measure, which is simply the variance of the Laplacian
    focus_value = cv2.Laplacian(image, cv2.CV_64F).var()
    focus_text = 'f: {}'.format(focus_value)
    # CV font
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(
        image,focus_text,
        (int(image.shape[0]*0.2), int(image.shape[1]*0.1)), 
        font, 1,(255,255,255))


    return image

def annotate_image(image):
    # do some modification
    image = cv2.Canny(image,100,100)
    
    # annotation doesnt return an image but draw directly on top
    #cv2.line(image,(0,0),(511,511),(255,0,0),5)
    # CV font
    #font = cv2.FONT_HERSHEY_SIMPLEX
    #cv2.putText(image,'OpenCV',(image.shape[0]/2,image.shape[1]/2), font, 4,(255,255,255))

    return image



def circle_detection(image):
    # https://www.pyimagesearch.com/2014/07/21/detecting-circles-images-using-opencv-hough-circles/
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.bilateralFilter(gray, 9, 75, 75)
    gray = cv2.addWeighted(gray, 1.5, blurred, -0.5, 0)
    gray = cv2.bilateralFilter(gray, 9, 75, 75)

    # detect circles in the image
    dp = 1
    c1 = 100
    c2 = 20
    circles = cv2.HoughCircles(gray, cv2.cv.CV_HOUGH_GRADIENT, dp, image.shape[0] / 4, param1=c1, param2=c2)

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0,:]:
            # draw the outer circle
            cv2.circle(image,(i[0],i[1]),i[2],(0,255,0),2)
            # draw the center of the circle
            cv2.circle(image,(i[0],i[1]),2,(0,0,255),3)


    # for i in circles[0, :]:
    #     if i[1] < 400:
    #         cv2.draw_circles(circles, image) 
    # # loop over the (x, y) coordinates and radius of the circles
    # for (x, y, r) in circles:
    #     # draw the circle in the output image, then draw a rectangle
    #     # corresponding to the center of the circle
    #     cv2.circle(image, (x, y), r, (0, 255, 0), 4)
    #     cv2.rectangle(image, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
 
    return image


face_cascade = cv2.CascadeClassifier('data/haarcascades/haarcascade_frontalface_default.xml')
def face_detection(image):
    # eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
    # gray scale image for faster calculation?
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    #time.sleep(0.2)

    for (x,y,w,h) in faces:
        cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = image[y:y+h, x:x+w]
    #     eyes = eye_cascade.detectMultiScale(roi_gray)
    # for (ex,ey,ew,eh) in eyes:
    #     cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
    return image




''' streaming '''
# initialize the camera and grab a reference to the raw camera capture
with picamera.PiCamera() as camera:
    camera.resolution = (int(640), int(480))
    fps = 15
    camera.framerate = fps
    # allow the camera to warmup
    time.sleep(0.1)

    # use the memory stream, may be faster?
    stream = io.BytesIO()

    camera.start_recording(stream, format='bgr')
    print('starting now')

    # image size
    image_size = camera.resolution[0]*camera.resolution[1]*3

    while True:
        while True:
            # reset stream for next frame
            stream.seek(0)
            stream.truncate()
            # this delay has to be faster than generating
            time.sleep(1/fps*0.2)

            # return current frame, which is just a string
            frame = stream.getvalue()
            ''' ensure the size of package is right''' 
            if len(frame) != 0:
                break
            else:
                pass
        
        # convert the stream string into np.arrry
        ncols, nrows = camera.resolution
        data = np.fromstring(frame, dtype=np.uint8).reshape(nrows, ncols, 3)
        # no need to decode (it is already bgr)
        image = data

        # opencv Fun time
        image = variance_of_laplacian(image)
        #image = annotate_image(image)
        # image = face_detection(image)
        #image = circle_detection(image)


        # move the imshow window to centre
        cv2.namedWindow('stream')        # Create a named window
        cv2.moveWindow('stream', 0,0)  # Move it to (40,30)
        # show the frame
        cv2.imshow('stream', image)
        key = cv2.waitKey(1) & 0xFF

        