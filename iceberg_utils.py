"""Utility helpers for working with Apache Iceberg tables via PySpark DataFrames.

These helpers assume that the runtime environment has a SparkSession that is
properly configured with an Iceberg catalog.  They provide thin wrappers around
`spark.read.format("iceberg")` / `DataFrame.write.format("iceberg")` with a
few convenience options.

Example usage
-------------
>>> from pyspark.sql import SparkSession
>>> from iceberg_utils import get_spark_session, read_iceberg_table, write_df_to_iceberg
>>> spark = get_spark_session("sample-app")  # or create/obtain your own SparkSession
>>> df = read_iceberg_table(spark, "prod.db.sample")
>>> processed = df.filter(df.value > 0)
>>> write_df_to_iceberg(processed, "prod.db.processed", mode="overwrite")
"""
from __future__ import annotations

from typing import Dict, Iterable, Optional

from pyspark.sql import DataFrame, SparkSession

__all__ = [
    "get_spark_session",
    "read_iceberg_table",
    "write_df_to_iceberg",
]


# ---------------------------------------------------------------------------
# Spark helpers
# ---------------------------------------------------------------------------

def get_spark_session(
    app_name: str = "IcebergApp",
    *,
    spark_config: Optional[Dict[str, str]] = None,
) -> SparkSession:
    """Return a :class:`~pyspark.sql.SparkSession` with Iceberg support enabled.

    This convenience wrapper creates a local SparkSession if one does not
    already exist.  The session is configured with a few baseline options that
    are commonly required when using Iceberg in Spark, but these can be
    overridden or extended via *spark_config*.

    Parameters
    ----------
    app_name:
        The Spark application name.
    spark_config:
        Extra Spark configuration entries to apply via ``builder.config``.

    Returns
    -------
    pyspark.sql.SparkSession
        The active or newly created session.
    """
    builder = (
        SparkSession.getActiveSession() or SparkSession.builder.appName(app_name)
    )

    # Default configs that are generally recommended for Iceberg.
    default_conf = {
        # Enable the Iceberg SQL extensions.
        "spark.sql.extensions": "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
        # The catalog implementation to use; ``spark_catalog`` is the default
        # session catalog in Spark 3.x.  Adjust to your own catalog name if
        # different (e.g. "prod_catalog").
        "spark.sql.catalog.spark_catalog": "org.apache.iceberg.spark.SparkSessionCatalog",
        # Use HadoopTables by default (file-based).  You may wish to point this
        # at a Hive, Glue, or REST catalog instead.
        "spark.sql.catalog.spark_catalog.type": "hadoop",
    }

    # Apply default + user-provided configs.
    for k, v in {**default_conf, **(spark_config or {})}.items():
        builder = builder.config(k, v)

    return builder.getOrCreate()


# ---------------------------------------------------------------------------
# Iceberg DataFrame helpers
# ---------------------------------------------------------------------------

def read_iceberg_table(
    spark: SparkSession,
    table_identifier: str,
    *,
    options: Optional[Dict[str, str]] = None,
) -> DataFrame:
    """Read an Iceberg table into a :class:`~pyspark.sql.DataFrame`.

    Parameters
    ----------
    spark:
        The active SparkSession.
    table_identifier:
        The fully-qualified Iceberg table identifier, e.g. ``"db.table"`` or
        ``"catalog.db.table"`` depending on your setup.
    options:
        Additional read options to pass to the Iceberg source (e.g.
        ``{"snapshot-id": "..."}``).

    Returns
    -------
    pyspark.sql.DataFrame
        The resulting DataFrame.
    """
    reader = spark.read.format("iceberg")
    for k, v in (options or {}).items():
        reader = reader.option(k, v)
    return reader.load(table_identifier)


def write_df_to_iceberg(
    df: DataFrame,
    table_identifier: str,
    *,
    mode: str = "append",
    partition_by: Optional[Iterable[str]] = None,
    options: Optional[Dict[str, str]] = None,
) -> None:
    """Write a DataFrame to an Iceberg table.

    Parameters
    ----------
    df:
        The DataFrame to write.
    table_identifier:
        The target Iceberg table identifier.
    mode:
        Save mode; one of ``"append"``, ``"overwrite"``, ``"error"`` (default
        Spark meaning).  ``"overwrite"`` will *replace* the table contents.
    partition_by:
        Optional list of column names to partition by when creating a new
        table.  Ignored if the table already exists unless
        ``mode="overwrite"`` *and* Iceberg create-or-replace semantics are in
        use.
    options:
        Additional write options (e.g. ``{"merge-schema": "true"}``).
    """
    writer = df.write.mode(mode).format("iceberg")

    for k, v in (options or {}).items():
        writer = writer.option(k, v)

    if partition_by:
        writer = writer.partitionBy(*partition_by)

    writer.save(table_identifier)