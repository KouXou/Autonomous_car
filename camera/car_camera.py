import cv2
import nanocamera
import utils.constants as const
from threading import Thread
from data.car_data import CarData, CsvFile
import pandas as pd


def generate_image_name(counter, car_move, car_speed):
    name = '/img_' + str(counter) + '_' + car_move + '_' + str(car_speed) + '.jpg'
    return name


class CarCamera(Thread):
    def __init__(self, autopilot=False, record_stops=False):
        self.camera_save_files_path = const.camera_save_files_path
        self.autopilot = autopilot
        self.record_stops = record_stops
        self.car_direction = ''
        self.car_move = ''
        self.car_speed = ''
        self.created_dir = ''
        self.start_rec = ''
        self.distance = ''
        self.df = pd.DataFrame()
        self.rec = False
        self.take_photo = False
        self.counter = 0
        self.camera = nanocamera.Camera(flip=const.camera_flip, width=const.image_width, height=const.image_height,
                                        fps=const.camera_fps)
        Thread.__init__(self)
        self.daemon = True

    def setup_camera_recording(self):
        carData = CarData()
        self.df = carData.create_df()

        while self.camera.isReady():
            # read the camera image
            image = self.camera.read()
            if self.rec:
                self.save_photo(image=image, carData=carData)
                self.counter += 1

    def start_recording(self, created_dir, start_rec):
        self.created_dir = created_dir
        self.start_rec = start_rec
        self.rec = True
        self.counter = 0

    def stop_recording(self):
        self.rec = False
        #  Create and export csv from dataframe
        csv = CsvFile(csv_name=self.start_rec + '.csv')
        csv.export_file(self.df, self.camera_save_files_path + self.created_dir + '/')
        self.df = pd.DataFrame()
        self.counter = 0
        self.created_dir = ''
        self.start_rec = ''

    def setup_photo_camera(self):
        carData = CarData()
        self.df = carData.create_df()

        while self.camera.isReady():
            # read the camera image
            image = self.camera.read()
            if self.take_photo:
                self.save_photo(image=image, carData=carData)
                self.take_photo = False
                self.counter += 1

    def take_pic(self, created_dir, start_rec):
        self.created_dir = created_dir
        self.start_rec = start_rec
        self.take_photo = True

    def stop_photo_camera(self):
        self.take_photo = False
        #  Create and export csv from dataframe
        csv = CsvFile(csv_name=self.start_rec + '.csv')
        csv.export_file(self.df, self.camera_save_files_path + self.created_dir + '/')
        self.df = pd.DataFrame()

    def stop(self):
        # Release Camera
        self.camera.release()

    def run(self):
        if self.autopilot:
            print('Autopilot Camera Mode')
        elif self.record_stops:
            print('Record Stops Camera Mode')
            self.setup_photo_camera()
        else:
            print('Record Video Camera Mode')
            self.setup_camera_recording()

    def pass_csv_param(self, car_direction, car_move, car_speed, distance):
        self.car_direction = car_direction
        self.car_move = car_move
        self.car_speed = car_speed
        self.distance = distance

    def save_photo(self, image, carData):
        self.df = carData.addToDataFrame(self.df, self.car_direction, self.car_move, self.car_speed, self.distance)
        cv2.imwrite(
            self.camera_save_files_path + self.created_dir + generate_image_name(self.counter, self.car_move,
                                                                                 self.car_speed),
            image, [int(cv2.IMWRITE_JPEG_QUALITY), const.image_quality])
