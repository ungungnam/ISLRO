from piper_sdk.kinematics import C_PiperForwardKinematics
import numpy as np

FPS = 30
SERVER_IP = "147.47.239.153"
FK_CALC = C_PiperForwardKinematics()
MOVEMENT_THRESHOLD = 50
DATASET_DIR = 'dataset'

class Config:
    def __init__(self):
        # Initialize the default values of your configuration
        self.config_dict = {
            'FPS': FPS,                  # Default frames per second
            'DATASET_DIR': DATASET_DIR,  # Default path for dataset directory
            'EPISODE_LEN': 10,         # Default episode length (can be overridden)
        }

    def set(self, key, value):
        # Method to set a key-value pair in the configuration
        self.config_dict[key] = value

    def get(self, key):
        # Method to retrieve a value for a given key
        return self.config_dict.get(key, None)

    def to_dict(self):
        # Returns the entire configuration dictionary
        return self.config_dict


def config():
    return Config().to_dict()


def deg2rad(deg):
    return deg * np.pi / 180


def rad2deg(rad):
    return rad * 180 / np.pi