# std
import json
import pickle
from io import StringIO, BytesIO
from dataclasses import dataclass
from typing import List, Optional, Union, Any

# third party
import boto3
import pandas as pd
from pandas import DataFrame
from botocore.response import StreamingBody

# ten_ds_utils
from ten_ds_utils.filesystem.base import Filesystem, Path, FileTypeException


LANDING_DSI_BUCKET = "pact-dops-euw2-datarepository-muew7ezn9hug"
PROD_DSI_BUCKET = "pact-dops-euw2-publication-10ds-hkogbg5bdvgw"
SANDBOX_DSI_BUCKET = "sandbox"

SANDBOX_BUCKET = "ten-ds-sandbox"
RAW_BUCKET = "ten-ds-raw-data"
CLEAN_BUCKET = "ten-ds-clean-data"


class NoFoldersException(Exception):
    pass


class InvalidS3Response(Exception):
    pass


@dataclass
class S3Path(Path):
    # Bucket shouldn't have a default value
    bucket: str

    @property
    def remote_path(self) -> str:
        return "s3://" + self.str


class S3Filesystem(Filesystem):
    """
    Class to work with objects within S3
    """

    def __init__(self, client=None, resource=None):
        self.client = client if client else boto3.client("s3")
        self.resource = resource if resource else boto3.resource("s3")

    @property
    def path(self) -> S3Path:
        return S3Path

    def list_buckets(self) -> List[str]:
        return [bucket["Name"] for bucket in self.client.list_buckets()["Buckets"]]

    def list_folders(self, path: S3Path, limit: int = 1000) -> DataFrame:
        if path.key and not path.key.endswith("/"):
            path.key += "/"
        res = self.client.list_objects_v2(
            Bucket=path.bucket, Delimiter="/", Prefix=path.key, MaxKeys=limit
        )
        folders = res.get("CommonPrefixes")
        if not folders:
            raise NoFoldersException
        return pd.json_normalize(folders)

    def list_objects(
        self, path: S3Path, limit: int = 1000, as_list: bool = False
    ) -> DataFrame:
        objects = self.client.list_objects_v2(
            Bucket=path.bucket, Prefix=path.key, MaxKeys=limit
        )["Contents"]

        if as_list is False:
            return pd.json_normalize(objects)
        else:
            return [obj["Key"] for obj in objects]

    def path_exists(self, path: S3Path) -> bool:
        try:
            self.list_objects(path, as_list=True)
            return True
        except KeyError:
            return False

    def read_file(self, path: S3Path, **kwargs) -> Union[DataFrame, dict]:
        extension = path.str.split(".")[-1].lower()
        body = self.fetch_file_body(path)
        if extension == "csv":
            return pd.read_csv(body, **kwargs)
        elif extension in ("xls", "xlsx", "xlsb"):
            return pd.read_excel(BytesIO(body.read()), **kwargs)
        elif extension in ("json", "geojson"):
            return json.loads(body.read().decode("utf-8"), **kwargs)
        elif extension == "pkl":
            return pickle.loads(body.read(), **kwargs)
        elif extension == "parquet":
            return pd.read_parquet(BytesIO(body.read()), **kwargs)
        elif extension == "dta":
            return pd.read_stata(BytesIO(body.read()), **kwargs)
        else:
            raise FileTypeException(
                f"Unexpected file type, function not build to handle \
                files of type: {extension}"
            )

    def upload_df(self, path: S3Path, df: DataFrame, acl: Optional[str] = ""):
        extension = path.str.split(".")[-1]
        if extension == "csv":
            buffer = StringIO()
            df.to_csv(buffer, index=False)
        elif extension == "parquet":
            buffer = BytesIO()
            df.to_parquet(buffer)
        else:
            raise FileTypeException(
                f"Unexpected file type, function not build to handle \
                files of type: {extension}"
            )
        res = self.resource.Object(path.bucket, path.key).put(
            ACL=acl, Body=buffer.getvalue()
        )
        self.validate_response(res)

    def upload_pickle(self, path: S3Path, pickle_obj: Any, acl: Optional[str] = ""):
        pickle_byte_obj = pickle.dumps(pickle_obj)
        res = self.resource.Object(path.bucket, path.key).put(
            ACL=acl, Body=pickle_byte_obj
        )
        self.validate_response(res)

    def fetch_file_body(self, path: S3Path) -> StreamingBody:
        res = self.client.get_object(Bucket=path.bucket, Key=path.key)
        self.validate_response(res)
        body = res["Body"]
        return body

    def validate_response(self, response: dict):
        """
        Validates the response from S3. Raising an error if the code is not 200
        """
        try:
            status_code = response["ResponseMetadata"]["HTTPStatusCode"]
            assert status_code == 200
        except (KeyError, AssertionError):
            raise InvalidS3Response
