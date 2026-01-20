"""
Write a sample Spark DataFrame to an Apache Iceberg table (DataFrameWriterV2).

This example uses a local Hadoop catalog (warehouse on local disk).
It creates a small DataFrame, writes it to Iceberg, then reads it back.

Run (example):
  spark-submit \
    --packages org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.6.1 \
    examples/pyspark_write_iceberg_dfwriter_v2.py
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, lit


def main() -> None:
    warehouse_dir = "./warehouse"

    spark = (
        SparkSession.builder.appName("iceberg-dfwriter-v2")
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
        .config("spark.sql.catalog.local", "org.apache.iceberg.spark.SparkCatalog")
        .config("spark.sql.catalog.local.type", "hadoop")
        .config("spark.sql.catalog.local.warehouse", warehouse_dir)
        .getOrCreate()
    )

    # Sample DataFrame
    df = (
        spark.createDataFrame(
            [
                (1, "alice", 10.5),
                (2, "bob", 20.0),
                (3, "carol", 30.25),
            ],
            "id INT, name STRING, amount DOUBLE",
        )
        .withColumn("ingested_at", current_timestamp())
        .withColumn("source", lit("dfwriter_v2"))
    )

    table = "local.default.sample_dfwriter_v2"

    # Write to Iceberg (create or replace table)
    df.writeTo(table).using("iceberg").createOrReplace()

    # Read back
    out = spark.table(table).orderBy("id")
    out.show(truncate=False)

    spark.stop()


if __name__ == "__main__":
    main()
