import arducam_mipicamera as arducam
import v4l2 #sudo pip install v4l2
import time
import cv2 #sudo apt-get install python-opencv

def align_down(size, align):
    return (size & ~((align)-1))

def align_up(size, align):
    return align_down(size + align - 1, align)

def set_controls(camera):
    try:
        print("Reset the focus...")
        camera.reset_control(v4l2.V4L2_CID_FOCUS_ABSOLUTE)
    except Exception as e:
        print(e)
        print("The camera may not support this control.")

    try:
        print("Enable Auto Exposure...")
        camera.software_auto_exposure(enable = True)
        # print("set exposure manually")
        # camera.write_sensor_reg(0x020E, 3)
        # camera.write_sensor_reg(0x0214, 3)
        # camera.set_control(v4l2.V4L2_CID_EXPOSURE, 10e6)

        print("Enable Auto White Balance...")
        camera.software_auto_white_balance(enable = True)

    except Exception as e:
        print(e)


def measure_focus(image):
    focus_value = cv2.Laplacian(image, cv2.CV_64F).var()
    focus_text = 'f: {:.2f}'.format(focus_value)
    # CV font
    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(
        image, focus_text,
        (int(image.shape[0]*0.1), int(image.shape[1]*0.1)), 
        font, 2, (0, 0, 255))


if __name__ == "__main__":
    try:
        camera = arducam.mipi_camera()
        print("Open camera...")
        camera.init_camera()
        print("Setting the resolution...")
        fmt = camera.set_resolution(1920, 1080)
        print("Current resolution is {}".format(fmt))
        set_controls(camera)
        while cv2.waitKey(10) != 27:
            frame = camera.capture(encoding = 'i420')
            height = int(align_up(fmt[1], 16))
            width = int(align_up(fmt[0], 32))
            image = frame.as_array.reshape(int(height * 1.5), width)
            image = cv2.cvtColor(image, cv2.COLOR_YUV2BGR_I420)
            height = image.shape[0]/2
            width = image.shape[1]/2
            # downsize a bit
            image = cv2.resize(image, (width, height ))
            measure_focus(image)
            print(image.shape)

            cv2.imshow("Arducam", image)


        # Release memory
        del frame
        print("Close camera...")
        camera.close_camera()
    except Exception as e:
        print(e)
