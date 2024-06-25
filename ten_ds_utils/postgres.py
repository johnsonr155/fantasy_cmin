import json

import sqlalchemy

from ten_ds_utils.config.base import BaseConfig


def create_engine(db_name: str, conf: BaseConfig, local_env: str = "dev"):
    secret_manager = conf.secret_manager()
    system_manager = conf.system_manager()

    if conf.is_local():
        env = local_env
    else:
        env = conf.env()

    db_login = json.loads(
        secret_manager.get_secret(f"ten-ds-rds-{env}-{db_name}-db-login")
    )
    db_host = system_manager.get_parameter(
        f"ten-ds-rds-{env}-db-host", WithDecryption=True
    )

    url = sqlalchemy.engine.url.URL(
        drivername="postgresql+psycopg2",
        username=db_login["username"],
        password=db_login["password"],
        database=db_name,
        host=db_host,
    )
    return sqlalchemy.create_engine(
        url,
        pool_size=5,
        max_overflow=2,
        pool_timeout=30,  # 30 seconds
    )
