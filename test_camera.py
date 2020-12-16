import cv2
# from nanocamera.NanoCam import Camera
import nanocamera as nano
import utils.constants as const
import datetime
import os
import sys
import termios
import tty
import threading

IMAGE_QUALITY = 99  # from 0 to 100


def create_dir():
    start_rec1 = str(datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    created_dir1 = start_rec1
    if not os.path.exists(const.camera_save_files_path + created_dir1):
        os.makedirs(const.camera_save_files_path + created_dir1)
    return created_dir1, start_rec1


def readChar():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    if ch == '0x03':
        raise KeyboardInterrupt
    return ch


def readKey(getchar_fn=None):
    getchar = getchar_fn or readChar
    c1 = getchar()
    if ord(c1) != 0x1b:
        return c1
    c2 = getchar()
    if ord(c2) != 0x5b:
        return c1
    c3 = getchar()
    return ord(c3) - 65  # 0=Up, 1=Down, 2=Right, 3=Left arrows


# if __name__ == '__main__':
def record():
    # Create the Camera instance
    camera = nano.Camera(flip=2, width=1280, height=800, fps=30)
    print('CSI Camera ready? - ', camera.isReady())
    counter = 0
    created_dir, start_rec = create_dir()
    while camera.isReady():
        try:
            # read the camera image
            frame = camera.read()
            # display the frame
            # cv2.imshow("Video Frame", frame)

            # print(counter)

            cv2.imwrite(const.camera_save_files_path + created_dir + '/img' + str(counter) + '.jpg', frame,
                        [int(cv2.IMWRITE_JPEG_QUALITY), IMAGE_QUALITY])
            counter += 1
            # print(frame)

            # if cv2.waitKey(25) & 0xFF == ord('q'):
            #     break
        except KeyboardInterrupt:
            break

    # close the camera instance
    camera.release()

    # remove camera object
    del camera


try:
    camera_thread = None
    while True:
        keyp = readKey()
        print(keyp)

        if keyp == 'r':
            camera_thread = threading.Thread(target=record, args=())
            camera_thread.start()
        elif keyp == 's' and camera_thread is not None:
            camera_thread.join()
        elif ord(keyp) == 3:
            break
except KeyboardInterrupt:
    print('turn off')
    try:

        sys.exit(0)
    except SystemExit:
        os._exit(0)
finally:
    print('finally')
