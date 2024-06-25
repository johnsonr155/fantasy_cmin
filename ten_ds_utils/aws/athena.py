import os
import pandas as pd
from enum import Enum
from time import sleep
from io import BytesIO

from ten_ds_utils.aws.session import Session


class AthenaException(Exception):
    pass


class QueryStatus(Enum):
    """List of possible states for an athena query"""

    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class Athena(Session):
    def __init__(
        self,
        results_bucket: str,
        results_folder: str = "",
        database: str = "",
        client=None,
        s3_client=None,
    ):
        super().__init__()
        self.results_bucket = results_bucket
        self.results_folder = results_folder
        self.database = database
        self.client = (
            client if client else self.session.client("athena", region_name=self.region)
        )
        self.s3 = (
            s3_client
            if s3_client
            else self.session.client("s3", region_name=self.region)
        )

    def read_csv(self, query: str):
        """Execute a query and return the resulting data as a pandas dataframe"""
        rows = self.select(query)
        return pd.read_csv(BytesIO(rows), encoding="ISO-8859-1")

    def select(self, query: str):
        res = self.exec(query, synchronous=True)
        output_location = res["QueryExecution"]["ResultConfiguration"]["OutputLocation"]
        parts = output_location.split(self.results_bucket)
        if len(parts) != 2:
            raise AthenaException(f"Output location is not valid: {output_location}")

        folder = parts[1].lstrip("/")

        obj = self.s3.get_object(Bucket=str(self.results_bucket), Key=str(folder))

        return obj["Body"].read()

    def exec(self, query: str, synchronous=True):
        """Execute the given query"""

        res = self.client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={"Database": self.database},
            ResultConfiguration={"OutputLocation": self.results_location()},
        )

        if not synchronous:
            return res

        execution_id = res["QueryExecutionId"]

        return self.wait(execution_id)

    def wait(self, execution_id, sleep_seconds: int = 2.0):
        """Wait for a query to complete"""

        while True:
            res = self.client.get_query_execution(QueryExecutionId=execution_id)

            status = res["QueryExecution"]["Status"]["State"]

            if status == QueryStatus.SUCCEEDED.value:
                return res
            elif status in [
                QueryStatus.CANCELLED.value,
                QueryStatus.FAILED.value,
            ]:
                print(res)
                raise AthenaException(status)
            elif status in [
                QueryStatus.QUEUED.value,
                QueryStatus.RUNNING.value,
            ]:
                sleep(sleep_seconds)
            else:
                raise AthenaException(status)

    def drop_table(self, table_name: str):
        q = f"DROP TABLE IF EXISTS {table_name};"
        return self.exec(q)

    def results_location(self):
        return os.path.join("s3://", self.results_bucket, self.results_folder)
