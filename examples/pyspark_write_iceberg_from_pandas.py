"""
Create a Pandas DataFrame, convert to Spark DataFrame, write to Apache Iceberg.

This is useful when your upstream data is in Pandas and you want to land it in Iceberg.

Run (example):
  pip install pandas pyspark
  spark-submit \
    --packages org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.6.1 \
    examples/pyspark_write_iceberg_from_pandas.py
"""

import pandas as pd
from pyspark.sql import SparkSession


def main() -> None:
    warehouse_dir = "./warehouse"

    spark = (
        SparkSession.builder.appName("iceberg-from-pandas")
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
        .config("spark.sql.catalog.local", "org.apache.iceberg.spark.SparkCatalog")
        .config("spark.sql.catalog.local.type", "hadoop")
        .config("spark.sql.catalog.local.warehouse", warehouse_dir)
        .getOrCreate()
    )

    pdf = pd.DataFrame(
        {
            "id": [1001, 1002, 1003],
            "name": ["gita", "hari", "ines"],
            "amount": [1.1, 2.2, 3.3],
        }
    )

    df = spark.createDataFrame(pdf)

    table = "local.default.sample_from_pandas"
    df.writeTo(table).using("iceberg").createOrReplace()

    spark.table(table).orderBy("id").show(truncate=False)

    spark.stop()


if __name__ == "__main__":
    main()
