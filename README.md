# Iceberg Utils

A comprehensive Python utility library for working with Apache Iceberg tables. This library provides easy-to-use functions for reading, writing, and managing Iceberg tables using both PyIceberg and PySpark.

## Features

- **Read Operations**: Read Iceberg tables into Pandas DataFrames or Spark DataFrames
- **Write Operations**: Write DataFrames to Iceberg tables with support for append/overwrite modes
- **Table Management**: Create, drop, and list Iceberg tables
- **Filtering**: Read tables with column-based filters for efficient data retrieval
- **Metadata**: Get comprehensive table metadata including schema, snapshots, and properties
- **Maintenance**: Table compaction and snapshot expiration
- **Dual Interface**: Both class-based and convenience function APIs
- **Spark Integration**: Full PySpark support for large-scale operations

## Installation

### Core Dependencies

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install "pyiceberg>=0.5.1" "pandas>=1.5.0" "pyarrow>=10.0.0"
```

### Optional Dependencies

For Spark integration:

```bash
pip install "pyspark>=3.3.0"
```

## Quick Start

### Basic Usage with Convenience Functions

```python
import pandas as pd
from iceberg_utils import read_iceberg_table, write_dataframe_to_iceberg

# Create sample data
df = pd.DataFrame({
    'id': [1, 2, 3],
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35]
})

# Configuration for your Iceberg catalog
catalog_config = {
    "type": "hadoop",
    "warehouse": "./warehouse"
}

# Write DataFrame to Iceberg table
write_dataframe_to_iceberg(
    df=df,
    table_name="users",
    namespace="demo",
    mode="overwrite",
    catalog_config=catalog_config
)

# Read table back
result_df = read_iceberg_table(
    table_name="users",
    namespace="demo",
    catalog_config=catalog_config
)
print(result_df)
```

### Advanced Usage with IcebergUtils Class

```python
from iceberg_utils import IcebergUtils

# Initialize utils
utils = IcebergUtils(catalog_config={
    "type": "hadoop",
    "warehouse": "./warehouse"
})

# Read with filters
filtered_df = utils.read_iceberg_table_with_filter(
    table_name="users",
    filters={"age": [25, 30]},  # Users aged 25 or 30
    namespace="demo"
)

# Get table metadata
metadata = utils.get_table_metadata("users", "demo")
print(f"Table location: {metadata['location']}")
print(f"Current schema: {metadata['schema']}")

# List all tables
tables = utils.list_tables("demo")
print(f"Available tables: {tables}")
```

## API Reference

### IcebergUtils Class

#### Initialization

```python
utils = IcebergUtils(
    catalog_config=None,  # Dict with catalog configuration
    spark_session=None    # Optional pre-configured Spark session
)
```

#### Read Operations

| Method | Description | Returns |
|--------|-------------|---------|
| `read_iceberg_table(table_name, namespace="default")` | Read table into Pandas DataFrame | `pd.DataFrame` |
| `read_iceberg_table_spark(table_name, namespace="default")` | Read table using Spark | `SparkDataFrame` |
| `read_iceberg_table_with_filter(table_name, filters, namespace="default")` | Read table with column filters | `pd.DataFrame` |

#### Write Operations

| Method | Description | Parameters |
|--------|-------------|------------|
| `write_dataframe_to_iceberg(df, table_name, namespace="default", mode="append", schema=None)` | Write Pandas DataFrame to table | `mode`: "append" or "overwrite" |
| `write_spark_dataframe_to_iceberg(df, table_name, namespace="default", mode="append")` | Write Spark DataFrame to table | `mode`: "append" or "overwrite" |

#### Table Management

| Method | Description | Returns |
|--------|-------------|---------|
| `create_iceberg_table(table_name, schema, namespace="default", properties=None)` | Create new table | `Table` |
| `drop_iceberg_table(table_name, namespace="default")` | Drop table | `None` |
| `list_tables(namespace="default")` | List all tables in namespace | `List[str]` |
| `get_table_metadata(table_name, namespace="default")` | Get table metadata | `Dict[str, Any]` |

#### Maintenance Operations

| Method | Description | Requirements |
|--------|-------------|-------------|
| `compact_table(table_name, namespace="default")` | Compact table files | Requires Spark |
| `expire_snapshots(table_name, older_than_days=7, namespace="default")` | Remove old snapshots | Requires Spark |

### Convenience Functions

| Function | Description |
|----------|-------------|
| `read_iceberg_table(table_name, namespace="default", catalog_config=None)` | Quick table read |
| `write_dataframe_to_iceberg(df, table_name, namespace="default", mode="append", catalog_config=None)` | Quick table write |
| `get_table_info(table_name, namespace="default", catalog_config=None)` | Quick metadata access |

## Configuration Examples

### Local Hadoop Catalog

```python
catalog_config = {
    "type": "hadoop",
    "warehouse": "./warehouse"
}
```

### REST Catalog

```python
catalog_config = {
    "uri": "http://localhost:8181",
    "warehouse": "s3://your-bucket/warehouse/"
}
```

### Hive Catalog

```python
catalog_config = {
    "type": "hive",
    "uri": "thrift://localhost:9083"
}
```

### AWS Glue Catalog

```python
catalog_config = {
    "type": "glue",
    "warehouse": "s3://your-bucket/warehouse/"
}
```

## Filtering Examples

### Simple Filters

```python
# Single value filter
filters = {"status": "active"}

# Multiple values (IN clause)
filters = {"category": ["electronics", "books", "clothing"]}

# Null check
filters = {"description": None}
```

### Complex Filters

```python
# Multiple column filters
filters = {
    "status": "active",
    "category": ["electronics", "books"],
    "price_range": "premium"
}
```

## Schema Definition

### Custom Schema Example

```python
from pyiceberg.schema import Schema
from pyiceberg.types import NestedField, StringType, IntegerType, TimestampType

schema = Schema(
    NestedField(1, "id", StringType(), required=True),
    NestedField(2, "name", StringType(), required=True),
    NestedField(3, "price", IntegerType(), required=False),
    NestedField(4, "created_at", TimestampType(), required=True)
)

utils.create_iceberg_table(
    table_name="products",
    schema=schema,
    namespace="demo"
)
```

## Error Handling

The library includes comprehensive error handling and logging:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

try:
    df = utils.read_iceberg_table("nonexistent_table")
except Exception as e:
    print(f"Error: {e}")
```

## Performance Tips

1. **Use Filters**: Apply filters at the Iceberg level for better performance
2. **Batch Writes**: Use larger DataFrames for write operations
3. **Spark for Large Data**: Use Spark operations for datasets > 1GB
4. **Regular Maintenance**: Run compaction and snapshot expiration regularly
5. **Partitioning**: Use partitioned tables for large datasets

## Spark Integration

### Spark Session Configuration

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("IcebergApp") \
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkSessionCatalog") \
    .config("spark.sql.catalog.spark_catalog.type", "hive") \
    .getOrCreate()

utils = IcebergUtils(spark_session=spark)
```

## Examples

Run the example script to see all features in action:

```bash
python example_usage.py
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Catalog Connection**: Verify catalog configuration and connectivity
3. **Permissions**: Check read/write permissions to warehouse location
4. **Spark Issues**: Ensure Java 8+ is installed for Spark operations
5. **Schema Mismatch**: Verify DataFrame schema matches table schema

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Check the troubleshooting section
- Review the example usage
- Create an issue with detailed error information