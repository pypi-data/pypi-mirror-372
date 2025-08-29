"""Example of how to run selection class."""

from pathlib import Path

from environs import Env

from lightly_purple import DatasetLoader
from lightly_purple.selection.select import Selection

# Read environment variables
env = Env()
env.read_env()

# Define the path to the dataset directory
dataset_path = Path(env.path("DATASET_PATH", "/path/to/your/dataset"))
dataset_path = dataset_path.parent if dataset_path.is_file() else dataset_path

# Create a DatasetLoader from a path
loader = DatasetLoader()
dataset = loader.from_directory(
    dataset_name="clothing_small_test",
    img_dir=str(dataset_path),
)

# Create the selection interface
# TODO(Malte, 08/2025): Replace this with using a DatasetView.
# See the Select class for more details on the TODO.
select = Selection(
    dataset_id=dataset.dataset_id,
    session=loader.session,
)

# Select a diverse subset of 10 samples.
select.diverse(
    n_samples_to_select=10,
    selection_result_tag_name="diverse_selection",
)

loader.start_gui()
