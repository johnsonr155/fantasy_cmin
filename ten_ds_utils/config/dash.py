import os
from dotenv import load_dotenv

from ten_ds_utils.aws.encryption import get_encrypted_token
from ten_ds_utils.aws.cognito import PROD_EKS_AUTH_KMS_KEY_ID
from ten_ds_utils.dash.constants import DASHBOARD_PROD_URL_PARAMETER_NAME
from ten_ds_utils.config.base import BaseConfig
from ten_ds_utils.filesystem.base import Path


load_dotenv()

DATA_BUCKET = "DATA_BUCKET"
REPO = "REPO"
STATIC_PATH = "STATIC_PATH"


class DashConfig(BaseConfig):
    def __init__(self):
        self.required_env_vars = [
            *super().required_env_vars,
            DATA_BUCKET,
            REPO,
            STATIC_PATH,
        ]
        super().__init__()

    def data_bucket(self) -> str:
        return os.getenv(DATA_BUCKET)

    def repo(self) -> str:
        return os.getenv(REPO)

    def static_path(self) -> str:
        return os.getenv(STATIC_PATH)

    def generate_path(self, key: str) -> Path:
        # Include the data path as part of the key if present
        if self.data_path():
            key = os.path.join(self.data_path(), key)

        return self.filesystem().path(self.data_bucket(), key)

    def generate_prod_url(self, page: str) -> str:
        if not self.is_local():
            ssm = self.system_manager()
            key_id = ssm.get_parameter(PROD_EKS_AUTH_KMS_KEY_ID, WithDecryption=True)
            url = ssm.get_parameter(
                DASHBOARD_PROD_URL_PARAMETER_NAME, WithDecryption=True
            )

            base_page = page.strip("/").split("/")[0]
            token = get_encrypted_token(key_id, base_page)
            return f"https://{url}/{page}/?token={token}"
        else:
            return None

    def is_paas(self) -> bool:
        """Check to see if the app is in an environment that will be mirrored to paas"""
        if self.is_prod() or self.env() == "preprod":
            return True
        else:
            return False

    def all(self) -> dict:
        return {
            **super().all(),
            "data_path": self.data_path(),
            "data_bucket": self.data_bucket(),
            "filesystem": type(self.filesystem()),
        }
