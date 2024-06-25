import os
import logging
from typing import Callable
from datetime import datetime
from dotenv import load_dotenv

from ten_ds_utils.config.base import BaseConfig
from ten_ds_utils.filesystem.base import Path
from ten_ds_utils.govuk_notify import govuk_notify_service

load_dotenv()


DATA_VERSION = "DATA_VERSION"
SOURCE_BUCKET = "SOURCE_BUCKET"
TARGET_BUCKET = "TARGET_BUCKET"


class PipelineConfig(BaseConfig):
    def __init__(self):
        self.required_env_vars = [
            *super().required_env_vars,
            DATA_VERSION,
            SOURCE_BUCKET,
            TARGET_BUCKET,
        ]
        super().__init__()

    def set_logging(self):
        # Ensures that we can log in Lambdas
        if len(logging.getLogger().handlers) > 0:
            logging.getLogger().setLevel(self.log_level())
        else:
            logging.basicConfig(level=self.log_level())

    def data_version(self) -> str:
        return os.getenv(DATA_VERSION)

    def source_bucket(self) -> str:
        return os.getenv(SOURCE_BUCKET)

    def target_bucket(self) -> str:
        return os.getenv(TARGET_BUCKET)

    def generate_path(self, bucket: str, key: str = "") -> Path:
        """
        Generates a path for a given bucket and key
        """
        if self.data_path():
            key = os.path.join(self.data_path(), self.data_version(), key)
        else:
            key = os.path.join(self.data_version(), key)

        return self.filesystem().path(bucket, key)

    def generate_source_path(self, key: str = "") -> Path:
        """
        Generates a source path with the given key
        """
        return self.generate_path(self.source_bucket(), key)

    def generate_target_path(self, key: str = "") -> Path:
        """
        Generates a target path with the given key
        """
        return self.generate_path(self.target_bucket(), key)

    def all(self) -> dict:
        return {
            **super().all(),
            "data_path": self.data_path(),
            "data_version": self.data_version(),
            "source_bucket": self.source_bucket(),
            "target_bucket": self.target_bucket(),
        }
