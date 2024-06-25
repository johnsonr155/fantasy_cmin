# std
import os
import json
import pickle
from datetime import datetime
from typing import Union, Any
from dataclasses import dataclass

# third party
import pandas as pd
from pandas import DataFrame

# ten_ds_utils
from ten_ds_utils.filesystem.base import Filesystem, Path, FileTypeException


@dataclass
class LocalPath(Path):
    """Path class to work locally"""


class LocalFilesystem(Filesystem):
    """
    Class to work with objects locally
    """

    @property
    def path(self) -> LocalPath:
        return LocalPath

    @staticmethod
    def get_file_stats(path) -> str:
        stats = os.stat(path)
        return {
            "LastModified": str(datetime.fromtimestamp(stats.st_mtime)),
            "Size": stats.st_size,
        }

    def list_objects(self, path: LocalPath, as_list: bool = False) -> DataFrame:
        files = os.listdir(path.str)
        if path.key:
            files = [os.path.join(path.key, file) for file in files]
        if as_list:
            return files
        else:
            return pd.json_normalize(
                [
                    {
                        "Key": file,
                        **self.get_file_stats(os.path.join(path.bucket, file)),
                    }
                    for file in files
                ]
            )

    def path_exists(self, path: LocalPath) -> bool:
        return os.path.exists(path.str)

    def read_file(self, path: LocalPath, **kwargs) -> Union[DataFrame, dict]:
        extension = path.str.split(".")[-1].lower()
        if extension == "csv":
            return pd.read_csv(path.str, **kwargs)
        elif extension in ("xls", "xlsx", "xlsb"):
            return pd.read_excel(path.str, **kwargs)
        elif extension in ("json", "geojson"):
            with open(path.str) as file:
                return json.loads(file.read(), **kwargs)
        elif extension == "pkl":
            with open(path.str, "rb") as f:
                return pickle.load(f, **kwargs)
        elif extension == "parquet":
            return pd.read_parquet(path.str, **kwargs)
        elif extension == "dta":
            return pd.read_stata(path.str, **kwargs)
        else:
            raise FileTypeException(
                f"Unexpected file type, function not build to \
                handle files of type: {extension}"
            )

    def upload_df(self, path: LocalPath, df: DataFrame):
        extension = path.str.split(".")[-1]
        if extension == "csv":
            df.to_csv(path.str, index=False)
        elif extension == "parquet":
            df.to_parquet(path.str)
        else:
            raise FileTypeException(
                f"Unexpected file type, function not build to \
                handle files of type: {extension}"
            )

    def upload_pickle(self, path: LocalPath, pickle_obj: Any):
        with open(path.str, "wb") as f:
            pickle.dump(pickle_obj, f)
