PROD_EKS_AUTH_KMS_KEY_ID = "ten-ds-eks-auth-prod-kms-key-id"


def create_auth_headers(secret: str) -> dict:
    return {
        "authorization": f"Basic {secret}",
        "content-type": "application/x-www-form-urlencoded",
    }


def create_request_data(page_subdir: str) -> dict:
    return {"grant_type": "client_credentials", "scope": f"{page_subdir}/get"}
