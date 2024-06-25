from dataclasses import dataclass
from enum import Enum

from ten_ds_utils.dash.constants import (
    RAPID_PROD_ATHENA_DATABASE_PARAMETER_NAME,
    RAPID_PREPROD_ATHENA_DATABASE_PARAMETER_NAME,
    RAPID_DEV_ATHENA_DATABASE_PARAMETER_NAME,
    RAPID_PROD_ATHENA_WORKGROUP_PARAMETER_NAME,
    RAPID_PREPROD_ATHENA_WORKGROUP_PARAMETER_NAME,
    RAPID_DEV_ATHENA_WORKGROUP_PARAMETER_NAME,
)


@dataclass
class RapidAthenaConfig:
    athena_database: str
    athena_workgroup: str


class RapidAthenaConfigSelector(Enum):
    prod = RapidAthenaConfig(
        RAPID_PROD_ATHENA_DATABASE_PARAMETER_NAME,
        RAPID_PROD_ATHENA_WORKGROUP_PARAMETER_NAME,
    )
    preprod = RapidAthenaConfig(
        RAPID_PREPROD_ATHENA_DATABASE_PARAMETER_NAME,
        RAPID_PREPROD_ATHENA_WORKGROUP_PARAMETER_NAME,
    )
    dev = RapidAthenaConfig(
        RAPID_DEV_ATHENA_DATABASE_PARAMETER_NAME,
        RAPID_DEV_ATHENA_WORKGROUP_PARAMETER_NAME,
    )
