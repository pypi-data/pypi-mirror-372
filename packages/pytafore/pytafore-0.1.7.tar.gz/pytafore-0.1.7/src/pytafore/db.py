import logging
from typing import Any, Dict, Optional

import boto3
import pandas as pd
import psycopg2
import psycopg2.extras

from .const import EC2_REGION
from .util import (
    build_rel_path,
    load_env_var,
    render_template,
    timeit,
    validate_env_vars,
)

log = logging.getLogger("db")


def get_rs_config() -> dict:
    """
    Load and validate Redshift configuration from environment variables

    Outputs
    -------
    dict
        Dictionary containing the redshift config from environment variables
    """
    validate_env_vars(["RS_CLUSTER", "RS_USERNAME", "RS_DATABASE", "RS_HOST"])
    return {
        "cluster": load_env_var("RS_CLUSTER"),
        "username": load_env_var("RS_USERNAME"),
        "database": load_env_var("RS_DATABASE"),
        "host": load_env_var("RS_HOST"),
        "port": load_env_var("RS_PORT", "5439"),
    }


def get_rs_engine() -> psycopg2.extensions.connection:
    """
    Internal method to connect to redshift with explicit params
    pass params as **conn()

    Outputs
    -------
    conn : psycopg2.extensions.connection
        psycopg2 connection to redshift
    """
    params = get_rs_config()

    creds = boto3.client("redshift", region_name=EC2_REGION).get_cluster_credentials(
        ClusterIdentifier=params["cluster"],
        DbUser=params["username"],
        DbName=params["database"],
        AutoCreate=True,
    )

    conn = psycopg2.connect(
        host=params["host"],
        port=params["port"],
        database=params["database"],
        user=creds["DbUser"],
        password=creds["DbPassword"],
    )
    conn.autocommit = True
    return conn


@timeit
def rs_fetch_to_df(sql: str, **kwargs) -> pd.DataFrame:
    """
    Fetch data from redshift into a DataFrame with optional chunking

    Parameters
    ----------
    sql : str
        String containing the sql qeury
    **kwargs
        Any key words args for pandas read_sql_query function

    Outputs
    -------
    df : pd.DataFrame
        Pandas dataframe containg the output from the redshift sql query
    """
    chunk = 10_000
    with get_rs_engine() as engine:
        itr = pd.read_sql_query(sql, engine, chunksize=chunk, **kwargs)
        dfs = [
            df
            for i, df in enumerate(itr, 1)
            if not log.info(f"Loaded {chunk * i:,} rows") or True
        ]
        log.info(f"Merging {len(dfs)} chunks")
        df = pd.concat(dfs)
        log.info(f"Total rows: {len(df.index):,}")
    return df


def rs_fetch(engine, sql: str, fetch_one: bool = False) -> Optional[Dict[str, Any]]:
    """
    Execute SQL and return results.
    If fetch_one is True, return the first row as a dict, else return a generator

    Parameters
    ----------
    engine : psycopg2.extensions.connection
        Redshift connection
    sql : str
        SQL query to execute
    fetch_one : bool
        Boolean indicating if we only want the first result (useful for finding latest schema)

    Outputs
    -------
    dict
        Dictionary or generator containing dictionaries of the output rows
    """
    with engine.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
        cursor.execute(sql)
        column_names = [column.name for column in cursor.description]
        if fetch_one:
            row = next(cursor, None)
            if row is None:
                raise StopIteration
            fetched_one = dict(zip(column_names, row))
            return fetched_one
        else:
            fetched_all = [dict(zip(column_names, row)) for row in cursor]
            return fetched_all


def rs_latest_schema_by_prefix(
    engine: psycopg2.extensions.connection, pattern: str
) -> str:
    """
    List all redshift schemas using pattern and return the latest one

    Parameters
    ----------
    engine : psycopg2.extensions.connection
        Redshift connection
    pattern : str
        String containing the schema pattern

    Outputs
    -------
    str
        String containing the latest schema name for schemas of input pattern
    """
    script_path = build_rel_path(__file__, "latest_schema.sql")
    sql = render_template(script_path, {"pattern": pattern, "limit": 1}, silent=True)
    result = rs_fetch(engine, sql, fetch_one=True)
    if result:
        return result["nspname"]
    else:
        log.error("No schema found matching the pattern.")
        return ""
