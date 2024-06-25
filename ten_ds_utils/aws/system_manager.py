from ten_ds_utils.aws.session import Session


class SystemManager(Session):
    def __init__(self) -> None:
        super().__init__()
        self.client = self.session.client(service_name="ssm", region_name=self.region)

    def get_parameter(self, name: str, **kwargs):
        response = self.client.get_parameter(Name=name, **kwargs)
        return response["Parameter"]["Value"]
