import cv2
import nanocamera
import utils.constants as const
import datetime
import os
from threading import Thread
from data.car_data import CarData, CsvFile
import pandas as pd
import time


class CarCamera(Thread):
    def __init__(self, led, autopilot=False, record_stops=False):
        self.camera_flip = const.camera_flip
        self.image_width = const.image_width
        self.image_height = const.image_height
        self.camera_fps = const.camera_fps
        self.camera_save_files_path = const.camera_save_files_path
        self.image_quality = const.image_quality
        self.autopilot = autopilot
        self.record_stops = record_stops
        self.car_direction = ''
        self.car_move = ''
        self.car_speed = ''
        self.created_dir = ''
        self.start_rec = ''
        self.distance = ''
        self.image = ''
        self.carData = ''
        self.led = led
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
            # Turn On Red LED
            self.led.turnOn(const.red_LED_pin)
            # read the camera image
            image = self.camera.read()
            self.df = carData.addToDataFrame(self.df, self.car_direction, self.car_move, self.car_speed, self.distance)
            cv2.imwrite(
                self.camera_save_files_path + self.created_dir + self.generate_image_name(counter, self.car_move,
                                                                                          self.car_speed),
                image, [int(cv2.IMWRITE_JPEG_QUALITY), self.image_quality])
            counter += 1

    def create_dir(self):
        start_rec = str(datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
        created_dir = start_rec
        if not os.path.exists(const.camera_save_files_path + const.track_name + '/' + created_dir):
            os.makedirs(const.camera_save_files_path + created_dir)
        return created_dir, start_rec

    def generate_image_name(self, counter, car_move, car_speed):
        name = '/img_' + str(counter) + '_' + car_move + '_' + str(car_speed) + '.jpg'
        return name

    def stop(self):
        # Turn Off Red LED
        self.led.turnOff(const.red_LED_pin)
        # Release Camera
        self.camera.release()
        csv = CsvFile(csv_name=self.start_rec + '.csv')
        csv.export_file(self.df, self.camera_save_files_path + self.created_dir + '/')
        self.df = pd.DataFrame()

    def start_camera(self):
        self.created_dir, self.start_rec = self.create_dir()
        # counter = 0
        self.carData = CarData()
        self.df = self.carData.create_df()
        # print(created_dir)
        while self.camera.isReady():
            # read the camera image
            self.image = self.camera.read()

    def take_pic(self):
        # Turn On green LED
        self.led.turnOn(const.green_LED_pin)
        time.sleep(0.5)
        self.led.turnOff(const.green_LED_pin)

        self.df = self.carData.addToDataFrame(self.df, 'stop', 'stop', 0, self.distance)

        cv2.imwrite(
            self.camera_save_files_path + self.created_dir + self.generate_image_name(len(self.df) - 1, self.car_move,
                                                                                      self.car_speed),
            self.image, [int(cv2.IMWRITE_JPEG_QUALITY), self.image_quality])

    def run(self):
        print(self.record_stops)
        if self.autopilot:
            print('Autopilot Camera On')
        elif self.record_stops:
            print('Record Stops On')
            self.start_camera()
        else:
            self.start_recording()

    def pass_csv_param(self, car_direction, car_move, car_speed, distance):
        self.car_direction = car_direction
        self.car_move = car_move
        self.car_speed = car_speed
        self.distance = distance
