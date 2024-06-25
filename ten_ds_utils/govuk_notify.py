from notifications_python_client.notifications import NotificationsAPIClient
from ten_ds_utils.aws.secret_manager import SecretManager


def govuk_notify_service(key_name: str, secret: SecretManager = SecretManager()):
    key = secret.get_secret(key_name)

    return NotificationsAPIClient(api_key=key)
