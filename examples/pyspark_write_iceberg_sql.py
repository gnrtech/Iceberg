"""
Write a sample dataset to an Apache Iceberg table using Spark SQL.

This example uses a local Hadoop catalog (warehouse on local disk).
It creates a table (if needed), inserts rows, then reads them back.

Run (example):
  spark-submit \
    --packages org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.6.1 \
    examples/pyspark_write_iceberg_sql.py
"""

from pyspark.sql import SparkSession


def main() -> None:
    warehouse_dir = "./warehouse"

    spark = (
        SparkSession.builder.appName("iceberg-sql-write")
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
        .config("spark.sql.catalog.local", "org.apache.iceberg.spark.SparkCatalog")
        .config("spark.sql.catalog.local.type", "hadoop")
        .config("spark.sql.catalog.local.warehouse", warehouse_dir)
        .getOrCreate()
    )

    spark.sql("CREATE NAMESPACE IF NOT EXISTS local.default")

    spark.sql(
        """
        CREATE TABLE IF NOT EXISTS local.default.sample_sql (
          id INT,
          name STRING,
          amount DOUBLE
        )
        USING iceberg
        """
    )

    spark.sql(
        """
        INSERT INTO local.default.sample_sql (id, name, amount) VALUES
          (101, 'dave',  99.9),
          (102, 'erin', 199.0),
          (103, 'frank',  0.5)
        """
    )

    spark.sql("SELECT * FROM local.default.sample_sql ORDER BY id").show(truncate=False)

    spark.stop()


if __name__ == "__main__":
    main()
