import base64
from ten_ds_utils.aws.session import Session


class SecretManager(Session):
    def __init__(self) -> None:
        super().__init__()
        self.client = self.session.client(
            service_name="secretsmanager", region_name=self.region
        )

    def get_secret(self, secret_name: str):
        get_secret_value_response = self.client.get_secret_value(SecretId=secret_name)

        # Decrypts secret using the associated KMS key.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if "SecretString" in get_secret_value_response:
            return get_secret_value_response["SecretString"]
        else:
            return base64.b64decode(get_secret_value_response["SecretBinary"])
