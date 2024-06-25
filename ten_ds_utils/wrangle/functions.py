import awswrangler as wr

import logging
from typing import Optional
import boto3
import pandas as pd

from ten_ds_utils.config.base import BaseConfig
from ten_ds_utils.wrangle.constants import rapid_layers


class AWSError(Exception):
    """Raising errors in code to user."""

    pass


def get_table_start_name(layer: str, domain: str, dataset: str) -> str:
    """
    get starting table name string to identify relevant tables in AWS.
    """
    if any([layer, domain, dataset]) is None:
        raise ValueError("ensure a layer, domain and dataset is selected")

    if layer not in rapid_layers:
        raise ValueError("layer must be one of 'raw', 'processed', 'curated'")

    return f"{layer}_{domain}_{dataset}_"


def get_full_table_list(database: str) -> list:
    """
    extract all available table names in relevant database
    """
    client = boto3.client("glue")
    response = client.get_tables(CatalogName="AwsDataCatalog", DatabaseName=database)
    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        raise AWSError("Get Tables request failed")

    return [table["Name"] for table in response["TableList"]]


def extract_relevant_tables(table_name_start: str, all_table_names: list) -> list:
    """Find all table versions listed for specified table."""

    tables = [
        table
        for table in all_table_names
        if table.startswith(table_name_start)
        and table[len(table_name_start) :].isdigit()
    ]

    if tables:
        return tables
    else:
        msg = f"Table does not exist: {table_name_start}"
        logging.error(msg)
        raise ValueError(msg)


def find_table_latest_version(table_list: list) -> int:
    """
    Find latest version based on list of the same datasets
    """
    table_versions = [int(table.split("_")[-1]) for table in table_list]
    version = int(max(table_versions))

    return version


def create_rapid_table_name(table_name_start: str, version: str) -> str:
    """create full correct table name"""
    return f"{table_name_start}_{str(version)}"


def read_data_from_athena(
    full_table_name: str, database: str, athena_workgroup: str
) -> pd.DataFrame:
    athena_query = f"SELECT * FROM {database}.{full_table_name}"
    return wr.athena.read_sql_query(
        athena_query, database=database, workgroup=athena_workgroup
    )


def get_rapid_dataset(
    config: BaseConfig,
    layer: str,
    domain: str,
    dataset: str,
    version: Optional[str] = None,
) -> pd.DataFrame:
    """
    read in data from rapid
    """

    table_name_start = get_table_start_name(layer, domain, dataset)

    database_parameter_name = config.get_rapid_database_name(config)
    database = config.get_parameter_value(database_parameter_name)

    athena_workgroup_parameter_name = config.get_rapid_athena_workgroup(config)
    athena_workgroup = config.get_parameter_value(athena_workgroup_parameter_name)

    if not version:
        all_table_names = get_full_table_list(database)
        relevant_tables = extract_relevant_tables(table_name_start, all_table_names)
        version = find_table_latest_version(relevant_tables)

    full_table_name = create_rapid_table_name()

    return read_data_from_athena(full_table_name, database, athena_workgroup)
