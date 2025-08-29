"""Example of how to use the DatasetLoader class."""

from environs import Env

from lightly_purple import DatasetLoader

# Read environment variables
env = Env()
env.read_env()

# Create a DatasetLoader instance
loader = DatasetLoader()

# Define the path to the dataset (folder containing data.yaml)
dataset_path = env.path("DATASET_PATH", "/path/to/your/yolo/dataset/data.yaml")

# Load YOLO dataset using data.yaml path
loader.from_yolo(
    str(dataset_path),
    input_split=env.str("PURPLE_DATASET_SPLIT", "test"),
)

loader.start_gui()
