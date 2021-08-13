import utils.constants as const
from threading import Thread
from data.car_data import CarData, CsvFile
import pandas as pd
import jetson.utils
import sys
import numpy as np
import PIL.Image
import torchvision.transforms as transforms


def generate_image_name(counter, car_move, car_speed):
    name = '/img_' + str(counter) + '_' + car_move + '_' + str(car_speed) + '.jpg'
    return name


class CarCamera(Thread):
    def __init__(self, autopilot=False, record_stops=False, video_output=False):
        self.camera_save_files_path = const.camera_save_files_path
        self.autopilot = autopilot
        self.record_stops = record_stops
        self.car_move = ''
        self.car_speed = ''
        self.created_dir = ''
        self.start_rec = ''
        self.distance = ''
        self.df = pd.DataFrame()
        self.rec = False
        self.take_photo = False
        self.video_output = video_output
        self.counter = 0
        self.font = jetson.utils.cudaFont()
        self.camera = jetson.utils.videoSource("csi://0", ['--input-width=640', '--input-height=320'])
        self.output = jetson.utils.videoOutput(const.video_output_url, argv=sys.argv)

        Thread.__init__(self)
        self.daemon = True

    def setup_camera_recording(self):
        carData = CarData()
        self.df = carData.create_df()

        while True:
            image = self.camera.Capture()
            # self.font.OverlayText(image, width, height, "YOLO", 10, 10, self.font.White,
            #                  self.font.Gray40)
            if self.video_output:
                self.output.Render(image)

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

        while True:
            # read the camera image
            image = self.camera.Capture()
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
        self.camera.Close()

    def read(self, showMoves=False, move=None, output_percent=None):
        image = self.camera.Capture()
        if showMoves:
            self.font.OverlayText(image, 50, 20, move + ' ' + "{:.2f}%".format(output_percent), 10, 10, self.font.White,
                                  self.font.Gray40)
        if self.video_output:
            self.output.Render(image)
        return image

    def video_out(self, image, showMoves=False, move=None, output_percent=None):
        if showMoves:
            self.font.OverlayText(image, 50, 20, move + ' ' + "{:.2f}%".format(output_percent), 10, 10, self.font.White,
                                  self.font.Gray40)
        if self.video_output:
            self.output.Render(image)

    def run(self):
        if self.autopilot:
            print('Autopilot Camera Mode')
        elif self.record_stops:
            print('Record Stops Camera Mode')
            self.setup_photo_camera()
        else:
            print('Record Video Camera Mode')
            self.setup_camera_recording()

    def pass_csv_param(self, car_move, car_speed, distance):
        self.car_move = car_move
        self.car_speed = car_speed
        self.distance = distance

    def save_photo(self, image, carData):
        self.df = carData.addToDataFrame(self.df,
                                         move=self.car_move,
                                         speed=self.car_speed,
                                         distance=self.distance)
        # generate image name
        name = self.camera_save_files_path + self.created_dir + generate_image_name(self.counter, self.car_move,
                                                                                    self.car_speed)
        # convert CudaImage to np array
        image = jetson.utils.cudaToNumpy(image).astype(np.uint8)
        # read PIL image from array
        image = PIL.Image.fromarray(image)
        # resize image
        image = transforms.functional.resize(image, [224, 224])
        # save image
        image.save(name)
