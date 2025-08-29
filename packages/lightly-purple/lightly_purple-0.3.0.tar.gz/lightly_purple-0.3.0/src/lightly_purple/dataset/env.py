"""Initialize environment variables for the dataset module."""

from environs import Env

env = Env()
env.read_env()
PURPLE_EMBEDDINGS_MODEL_TYPE: str = env.str("PURPLE_EMBEDDINGS_MODEL_TYPE", "MOBILE_CLIP")
PURPLE_EDGE_MODEL_FILE_PATH: str = env.str("EDGE_MODEL_PATH", "./lightly_model.tar")
PURPLE_PROTOCOL: str = env.str("PURPLE_PROTOCOL", "http")
PURPLE_PORT: int = env.int("PURPLE_PORT", 8001)
PURPLE_HOST: str = env.str("PURPLE_HOST", "localhost")
PURPLE_DEBUG: str = env.bool("PURPLE_DEBUG", "false")

APP_URL = f"{PURPLE_PROTOCOL}://{PURPLE_HOST}:{PURPLE_PORT}"
