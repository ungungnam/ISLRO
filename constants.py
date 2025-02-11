FPS = 30
SERVER_IP = "147.47.239.153"

class Config:
    def __init__(self):
        # Initialize the default values of your configuration
        self.config_dict = {
            'FPS': 30,                  # Default frames per second
            'DATASET_DIR': '/home/islab/islab_ws/ISLRO/dataset',  # Default path for dataset directory
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