import boto3


REGION = "eu-west-2"


class Session:
    def __init__(self) -> None:
        self.session = boto3.session.Session()
        self.region = REGION
