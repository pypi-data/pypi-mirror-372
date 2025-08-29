"""Example of how to add tags to samples to set up a split review workflow."""

import math

from environs import Env

from lightly_purple import DatasetLoader
from lightly_purple.models.tag import TagCreate
from lightly_purple.resolvers import (
    tag_resolver,
)

# Read environment variables
env = Env()
env.read_env()

# Create a DatasetLoader instance
loader = DatasetLoader()

# Define the path to the dataset (folder containing data.yaml)
dataset_path = env.path("DATASET_PATH", "/path/to/your/yolo/dataset/data.yaml")

# Load YOLO dataset using data.yaml path
dataset = loader.from_yolo(
    str(dataset_path),
    input_split=env.str("PURPLE_DATASET_SPLIT", "test"),
)

# Define the reviewers
# This should be a comma-separated list of reviewers
# we will then create a tag for each reviewer and assign them samples
# to work on.
reviewers = env.str("DATASET_REVIEWERS", "Alice, Bob, Charlie, David")

# Get all samples from the db
samples = dataset.get_samples()

# Create a tag for each reviewer to work on
tags = []
for reviewer in reviewers.split(","):
    tags.append(
        tag_resolver.create(
            session=loader.session,
            tag=TagCreate(
                dataset_id=dataset.dataset_id,
                name=f"""{reviewer.strip()} tasks""",
                kind="sample",
            ),
        )
    )

# Chunk the samples into portions equally divided among the reviewers.
chunk_size = math.ceil(len(samples) / len(tags))
for i, tag in enumerate(tags):
    # allocate all samples for this tag
    sample_ids = [sample.sample_id for sample in samples[i * chunk_size : (i + 1) * chunk_size]]

    # Add sample_ids to the tag
    tag_resolver.add_sample_ids_to_tag_id(
        session=loader.session,
        tag_id=tag.tag_id,
        sample_ids=sample_ids,
    )


# Launch the server to load data
loader.start_gui()
