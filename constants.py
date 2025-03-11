from piper_sdk.kinematics import C_PiperForwardKinematics
import numpy as np

REPLAY_FPS = 30
RECORD_FPS = 30

SERVER_IP = "147.47.239.153"
FK_CALC = C_PiperForwardKinematics()
MOVEMENT_THRESHOLD = 50
RECORD_DATASET_DIR = 'record'
REPLAY_DATASET_DIR = 'replay'

WRIST_CAM_SN = "f1150781"
EXO_CAM_SN = "f1371608"

class replayConfig:
    def __init__(self):
        # Initialize the default values of your configuration
        self.config_dict = {
            'FPS': RECORD_FPS,                  # Default frames per second
            'DATASET_DIR': RECORD_DATASET_DIR,  # Default path for dataset directory
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


def replay_config():
    return replayConfig().to_dict()


def deg2rad(deg):
    return deg * np.pi / 180


def rad2deg(rad):
    return rad * 180 / np.pi