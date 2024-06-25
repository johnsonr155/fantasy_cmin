import base64
from warnings import warn
from datetime import date

import aws_encryption_sdk
from aws_encryption_sdk import CommitmentPolicy


def get_encrypted_token(key_id: str, page: str):
    try:
        client = aws_encryption_sdk.EncryptionSDKClient(
            commitment_policy=CommitmentPolicy.REQUIRE_ENCRYPT_REQUIRE_DECRYPT
        )

        kms_key_provider = aws_encryption_sdk.StrictAwsKmsMasterKeyProvider(
            key_ids=[key_id]
        )
        token, _ = client.encrypt(
            source=bytes(page, "utf-8"),
            key_provider=kms_key_provider,
            encryption_context={
                "purpose": page,
                "time": date.today().strftime("%Y-%m-%d"),
            },
        )
        token = base64.urlsafe_b64encode(token).decode("ascii")
        return token
    except Exception as ex:
        warn(f"Error in returning access token for {page}")
        warn(str(ex))
        warn(
            "If you are running this locally, you do not need to worry about this warning."
        )
        return None
