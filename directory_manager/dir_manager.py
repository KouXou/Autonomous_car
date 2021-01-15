import datetime
from utils import constants as const
import os


class DirectoryManager:
    def __init__(self):
        self.name = ''

    def create_directory(self):
        start_rec = str(datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
        created_dir = start_rec
        if not os.path.exists(const.camera_save_files_path + const.track_name + '/' + created_dir):
            os.makedirs(const.camera_save_files_path + created_dir)
        return created_dir, start_rec
