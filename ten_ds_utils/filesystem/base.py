from abc import ABC, abstractmethod, abstractproperty
from pandas import DataFrame
from dataclasses import dataclass
import pandas as pd
from typing import List, Optional, Tuple
import os
import copy
from warnings import warn
from ten_ds_utils.wrangle.dataframe import get_delta


class FileTypeException(Exception):
    pass


@dataclass
class Path:
    bucket: str = ""
    key: str = ""

    @property
    def str(self) -> str:
        if self.key:
            return os.path.join(self.bucket, self.key)
        else:
            return self.bucket

    def append(self, suffix: str, alter: bool = False):
        """
        Append a suffix to the path. Optionally adding it to the existing
        object or returning a new one without altering the original.
        """
        new_key = os.path.join(self.key, suffix)

        if alter:
            self.key = new_key
        else:
            obj = copy.deepcopy(self)
            obj.key = new_key
            return obj


class Filesystem(ABC):
    @abstractproperty
    def path(self) -> Path:
        """
        The path dataclass that corresponds to the Filesystem
        """
        return Path

    @abstractmethod
    def list_objects(
        self, path: Path, as_list: bool = False
    ) -> Tuple[DataFrame, List[str]]:
        pass

    @abstractmethod
    def path_exists(self, path: Path) -> bool:
        pass

    def append_all_dataframes_in_path(
        self, path: Path, allow_type_exception: bool = False
    ) -> DataFrame:
        keys = self.list_objects(path, as_list=True)
        dfs = []
        for key in keys:
            try:
                file_path = self.path(path.bucket, key)
                df = self.read_file(file_path)
                if isinstance(df, DataFrame):
                    dfs.append(df)
                else:
                    warn(
                        f"""File {path.str} has not been appended as it is not interpreted as a
                    DataFrame, please save it as a csv or spreadsheet if you wish to use this
                    functionality"""
                    )
            except FileTypeException:
                if not allow_type_exception:
                    raise

        df = pd.concat(dfs).reset_index(drop=True)
        return df

    @abstractmethod
    def read_file(self, path: Path) -> DataFrame:
        pass

    def fetch_latest_file(self, path: Path, **kwargs) -> DataFrame:
        objs = self.list_objects(path, as_list=False)
        latest_obj = (
            objs.query("Size != 0").sort_values("LastModified", ascending=False).iloc[0]
        )
        path.key = latest_obj["Key"]
        return self.read_file(path, **kwargs)

    @abstractmethod
    def upload_df(self, path: Path, df: DataFrame, *args):
        pass

    @abstractmethod
    def upload_pickle(self, path: Path, df: DataFrame, *args):
        pass

    def upload_delta(
        self,
        path: Path,
        key: str,
        latest: DataFrame,
        column_subset: Optional[List[str]] = None,
    ):
        history = self.append_all_dataframes_in_path(path)
        delta = get_delta(history, latest, column_subset)
        output_path = self.path(path.str, key)
        self.upload_df(output_path, delta)
