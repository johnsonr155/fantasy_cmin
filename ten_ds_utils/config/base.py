import os
from dotenv import load_dotenv
import logging
from typing import List, Optional


from ten_ds_utils.aws.secret_manager import SecretManager
from ten_ds_utils.aws.system_manager import SystemManager
from ten_ds_utils.filesystem.base import Filesystem
from ten_ds_utils.filesystem.s3 import S3Filesystem
from ten_ds_utils.filesystem.local import LocalFilesystem
from ten_ds_utils.config.services.rapid import (
    RapidAthenaConfig,
    RapidAthenaConfigSelector,
)

# Required environment variables
ENVIRONMENT = "ENVIRONMENT"
APP_NAME = "APP_NAME"
DATA_PATH = "DATA_PATH"
BASE_REQUIRED_ENV_VARS = [ENVIRONMENT, APP_NAME]

# Non essential environment variables
LOG_LEVEL = "LOG_LEVEL"
FILESYSTEM = "FILESYSTEM"


class BaseConfig:
    """Base config class that all config objects should inherit from"""

    required_env_vars = BASE_REQUIRED_ENV_VARS

    def __init__(self):
        self.set_logging()
        # Require data path when not working locally
        if not self.is_local():
            self.required_env_vars.append(DATA_PATH)
        self.check_env_vars(self.required_env_vars)
        logging.info(self.all())

    def set_logging(self):
        logging.basicConfig(level=self.log_level())

    def check_env_vars(self, required_env_vars: List[str]):
        """Checks that the necessary environment variables exist"""
        load_dotenv()

        for item in required_env_vars:
            if item not in os.environ:
                msg = f"Environment variable does not exist: {item}"
                logging.error(msg)
                raise EnvironmentError(msg)

    def env(self):
        return os.getenv(ENVIRONMENT, "local").lower()

    def app_name(self) -> str:
        """Application name"""
        return os.environ[APP_NAME]

    def use_s3_filesystem(self) -> bool:
        """
        Returns true if we should be using the s3 filesytem, false if local
        """
        filesystem = os.getenv(FILESYSTEM)
        # Use s3 if the filesystem env var is set to this
        # Optionally gives the option of running locally against s3 data
        if filesystem and filesystem.lower().strip() == "s3":
            return True
        # Otherwise select the filesystem based on the environment
        else:
            if self.is_local():
                return False
            else:
                return True

    def data_path(self) -> Optional[str]:
        if self.use_s3_filesystem():
            return os.getenv(DATA_PATH)
        # Ignore the data_path when working locally
        else:
            return None

    def filesystem(self, client=None, resource=None) -> Filesystem:
        if self.use_s3_filesystem():
            return S3Filesystem(client, resource)
        else:
            return LocalFilesystem()

    def secret_manager(self) -> SecretManager:
        return SecretManager()

    def system_manager(self) -> SystemManager:
        return SystemManager()

    def is_local(self) -> bool:
        """Check if the script is running locally"""
        return self.env() in ["local"]

    def is_prod(self) -> bool:
        """Check if the script is running in production"""
        return self.env() in ["prod", "production"]

    def log_level(self) -> int:
        """Application log level"""

        log_level = os.getenv(LOG_LEVEL)

        if isinstance(log_level, str):
            log_level = log_level.lower()

            if log_level in ["error", "err"]:
                return logging.ERROR

            if log_level in ["warn", "warning"]:
                return logging.WARN

            if log_level in ["debug"]:
                return logging.DEBUG

        # default to info
        return logging.INFO

    def all(self) -> dict:
        return {
            "env": self.env(),
            "app_name": self.app_name(),
            "log_level": self.log_level(),
        }

    def get_rapid_athena_config(self, env: Optional[str] = None) -> RapidAthenaConfig:
        if env:
            return RapidAthenaConfigSelector[env].value
        else:
            return RapidAthenaConfigSelector["prod"].value

    def get_parameter_value(self, parameter) -> str:
        ssm = self.system_manager()
        return ssm.get_parameter(parameter)
