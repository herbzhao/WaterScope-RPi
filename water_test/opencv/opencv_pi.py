from __future__ import division


# import the necessary packages 
from picamera.array import PiRGBArray
import picamera
import io
import time
import cv2
import numpy as np



def variance_of_laplacian(image, roi=[]):
    ''' focus detection ''' 
    if roi == []:
        roi = image
    # compute the Laplacian of the image and then return the focus
    # measure, which is simply the variance of the Laplacian

    focus_value = cv2.Laplacian(roi, cv2.CV_64F).var()
    focus_text = 'f: {}'.format(focus_value)
    # CV font
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(
        image,focus_text,
        (int(image.shape[0]*0.2), int(image.shape[1]*0.1)), 
        font, 1,(255,255,255))

    return image


def define_ROI(image):
    # do some modification
    print(image.shape)
    # the opencv size is (y,x)
    image_y, image_x = image.shape[:2]

    # a square from the centre of image
    box_size = int(image_x*0.3)
    roi_box = {
        'x1': int(image_x/2-box_size/2), 'y1':int(image_y/2-box_size/2), 
        'x2': int(image_x/2+box_size/2), 'y2':int(image_y/2+box_size/2)}
    # draw the rectangle
    cv2.rectangle(
        image, 
        pt1=(roi_box['x1'], roi_box['y1']),
        pt2=(roi_box['x2'], roi_box['y2']), 
        color=(255,0,0),
        thickness=2)
    
    # crop the image
    roi = image[roi_box['y1']: roi_box['y2'], roi_box['x1']:roi_box['x2']]

    return image, roi


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
        #image = variance_of_laplacian(image)
        image, roi = define_ROI(image)
        # use the roi to calculate the sharpness
        image = variance_of_laplacian(image, roi)
        #image = annotate_image(image)
        # image = face_detection(image)
        #image = circle_detection(image)


        # move the imshow window to centre
        cv2.namedWindow('stream')        # Create a named window
        cv2.moveWindow('stream', 0,0)  # Move it to (40,30)
        # show the frame
        cv2.imshow('stream', image)


        key = cv2.waitKey(1) & 0xFF
        # if the `x` key was pressed, break from the loop
        if key == ord("x"):
            break

        