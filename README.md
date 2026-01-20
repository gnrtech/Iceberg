# DataFrame → Iceberg write examples (PySpark)

This repo shows **multiple ways** to create a **sample DataFrame** and write it into an **Apache Iceberg** table, then read it back.

## Prerequisites

- Java 11+ (required by Spark)
- Spark 3.5.x (these examples use the Iceberg Spark runtime for Spark 3.5)
- Python 3.9+

## Install Python deps (optional)

Only needed for the **Pandas → Spark → Iceberg** example:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run examples

All examples use a **local Hadoop catalog** with warehouse at `./warehouse/`.

### 1) Spark DataFrameWriterV2 (recommended)

```bash
spark-submit \
  --packages org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.6.1 \
  examples/pyspark_write_iceberg_dfwriter_v2.py
```

### 2) Spark SQL (DDL + INSERT)

```bash
spark-submit \
  --packages org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.6.1 \
  examples/pyspark_write_iceberg_sql.py
```

### 3) Pandas → Spark → Iceberg

```bash
spark-submit \
  --packages org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.6.1 \
  examples/pyspark_write_iceberg_from_pandas.py
```

## Output / where data is stored

- Iceberg warehouse directory: `./warehouse/`
- Spark catalog: `local`
- Namespace: `local.default`
- Tables created by examples:
  - `local.default.sample_dfwriter_v2`
  - `local.default.sample_sql`
  - `local.default.sample_from_pandas`

## Create a new dev branch named `dev1`

If you want to do your own development on a new branch called `dev1`:

```bash
git checkout -b dev1
git push -u origin dev1
```