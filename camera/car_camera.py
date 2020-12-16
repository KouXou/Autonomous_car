import cv2
import nanocamera
import utils.constants as const
import datetime
import os
from threading import Thread
from data.car_data import CarData, CsvFile
import pandas as pd


class CarCamera(Thread):
    def __init__(self):
        self.camera_flip = const.camera_flip
        self.image_width = const.image_width
        self.image_height = const.image_height
        self.camera_fps = const.camera_fps
        self.camera_save_files_path = const.camera_save_files_path
        self.image_quality = const.image_quality
        self.car_direction = ''
        self.car_move = ''
        self.car_speed = ''
        self.created_dir = ''
        self.start_rec = ''
        self.df = pd.DataFrame()
        self.camera = nanocamera.Camera(flip=self.camera_flip, width=self.image_width, height=self.image_height,
                                        fps=self.camera_fps)
        # self.record = True
        Thread.__init__(self)
        self.daemon = True
        # self.start()

    def start_recording(self, counter=0):
        self.created_dir, self.start_rec = self.create_dir()
        # counter = 0
        carData = CarData()
        self.df = carData.create_df()
        # print(created_dir)
        while self.camera.isReady():
            # read the camera image
            image = self.camera.read()
            self.df = carData.addToDataFrame(self.df, self.car_direction, self.car_move, self.car_speed)
            cv2.imwrite(self.camera_save_files_path + self.created_dir + '/img' + str(counter) + '.jpg', image,
                        [int(cv2.IMWRITE_JPEG_QUALITY), self.image_quality])
            counter += 1

    def create_dir(self):
        start_rec = str(datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
        created_dir = start_rec
        if not os.path.exists(const.camera_save_files_path + created_dir):
            os.makedirs(const.camera_save_files_path + created_dir)
        return created_dir, start_rec

    def stop(self):
        self.camera.release()
        csv = CsvFile(csv_name=self.start_rec + '.csv')
        csv.export_file(self.df, self.camera_save_files_path + self.created_dir + '/')
        self.df = pd.DataFrame()

    def run(self):
        self.start_recording()

    def pass_csv_param(self, car_direction, car_move, car_speed):
        self.car_direction = car_direction
        self.car_move = car_move
        self.car_speed = car_speed

