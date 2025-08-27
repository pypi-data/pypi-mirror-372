import logging
import os
from typing import Literal, Optional

from sqlalchemy import Engine, create_engine

logger = logging.getLogger(__name__)


def get_connection_string(
    db_env: Literal["DEBUG", "ACC", "PROD"] | None = None,
    schema_name: str | None = None,
    db_user: str | None = None,
    db_passwd: str | None = None,
    db_host: str | None = None,
    db_port: str | None = None,
    db_database: str | None = None,
) -> tuple[str, Optional[dict]]:
    """Get the connection string for the database.

    Two options:
    1. Use the SQLite debug database by setting use_debug_sqlite to True and specifying
       the schema name (as the local SQLite database does not have a schema).
    2. Use the configured database environment and get the connection string
       from environment variables or provided parameters.

    Parameters
    ----------
    db_env : str, optional
        The database environment to use ('DEBUG','ACC', 'PROD', or None).
        If None, uses general (not acc/prod) database environment variables.
    schema_name : str, optional
        The schema name of the database. Used for schema translation in SQLite.
    db_user : str, optional
        Username for the database. If None, uses DB_USER from environment.
    db_passwd : str, optional
        Password for the database. If None, uses DB_PASSWD from environment.
    db_host : str, optional
        Host for the database. If None, uses DB_HOST or DB_HOST_{db_env} from .env
    db_port : str, optional
        Port for the database. If None, uses DB_PORT from .env
    db_database : str, optional
        Database name. If None, uses DB_DATABASE or DB_DATABASE_{db_env} from .env

    Returns
    -------
    tuple[str, Optional[dict]]
        The connection string and optional execution options for SQLAlchemy.
    """
    if db_env == "DEBUG":
        if schema_name is None:
            raise ValueError("Schema name must be provided for debug SQLite database.")
        logger.warning("Using debug SQLite database...")
        return "sqlite:///./sql_app.db", {"schema_translate_map": {schema_name: None}}

    db_user = db_user or os.getenv("DB_USER", None)
    db_passwd = db_passwd or os.getenv("DB_PASSWD", None)
    db_port = db_port or os.getenv("DB_PORT", None)
    if db_env is None:  # this uses DB_HOST and DB_DATABASE from the .env file
        db_host = db_host or os.getenv("DB_HOST", None)
        db_database = db_database or os.getenv("DB_DATABASE", None)
    elif (
        db_env == "ACC" or db_env == "PROD"
    ):  # this uses DB_HOST_ACC/PROD and DB_DATABASE_ACC/PROD from the .env file
        db_host = db_host or os.getenv(f"DB_HOST_{db_env}", None)
        db_database = db_database or os.getenv(f"DB_DATABASE_{db_env}", None)
    else:
        raise ValueError(f"Invalid environment: {db_env}")

    logger.info(f"Connecting to {db_host} and database {db_database}")

    if (
        db_user is None
        or db_passwd is None
        or db_host is None
        or db_port is None
        or db_database is None
    ):
        raise ValueError(
            "Database connection parameters are not all set. "
            f"DB_USER={db_user}, DB_PASSWD={db_passwd}, DB_HOST={db_host}, "
            f"DB_PORT={db_port}, DB_DATABASE={db_database}. Please set "
            "the required environment variables or pass them directly as parameters."
        )

    return (
        f"mssql+pymssql://{db_user}:{db_passwd}@{db_host}:{db_port}/{db_database}",
        None,
    )


def get_engine(
    connection_str: str | None = None,
    db_env: Literal["DEBUG", "ACC", "PROD"] | None = None,
    schema_name: str | None = None,
) -> Engine:
    """Get the SQLAlchemy engine.

    Two ways of using this function:
    1. Input the connection string directly and get the engine directly
    2. Specify the database environment and get the connection string from
        get_connection_string()
        --> if db_env is set to DEBUG, then specify the schema_name

    Parameters
    ----------
    connection_str : str, optional
        The connection string to the database, by default None
    db_env : Literal["DEBUG", "ACC", "PROD"] | None = None,
        The environment to use, by default None, alternatively 'DEBUG', 'ACC' or 'PROD'
        If None then the database connection variables are derived
        from the environment variables
    schema_name : str, optional
        The schema name of the database, by default None.
        Only needs to be set to remove it when using the SQLite debug database by
        defining db_env as DEBUG.

    Returns
    -------
    Engine
        The SQLAlchemy engine used for queries
    """
    if connection_str is not None:  # option 1
        connection_str, execution_options = connection_str, None
    else:  # option 2
        connection_str, execution_options = get_connection_string(
            db_env=db_env, schema_name=schema_name
        )

    return create_engine(
        connection_str, pool_pre_ping=True, execution_options=execution_options
    )
