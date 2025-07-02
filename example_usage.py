"""
Example Usage of Iceberg Utils

This script demonstrates how to use the Iceberg utilities for common operations
like reading, writing, and managing Iceberg tables.
"""

import pandas as pd
from iceberg_utils import IcebergUtils, read_iceberg_table, write_dataframe_to_iceberg

def example_basic_operations():
    """Example of basic read/write operations."""
    print("=== Basic Iceberg Operations ===")
    
    # Create sample data
    sample_data = pd.DataFrame({
        'user_id': [1, 2, 3, 4, 5],
        'username': ['alice', 'bob', 'charlie', 'diana', 'eve'],
        'email': ['alice@example.com', 'bob@example.com', 'charlie@example.com', 
                 'diana@example.com', 'eve@example.com'],
        'age': [25, 30, 35, 28, 32],
        'signup_date': pd.to_datetime(['2023-01-15', '2023-02-20', '2023-03-10', 
                                     '2023-04-05', '2023-05-12'])
    })
    
    print("Sample data:")
    print(sample_data)
    
    # Configuration for local testing (adjust for your setup)
    catalog_config = {
        "type": "hadoop",
        "warehouse": "./warehouse"  # Local warehouse directory
    }
    
    # Using convenience functions
    print("\n--- Using convenience functions ---")
    
    # Write data to Iceberg table
    write_dataframe_to_iceberg(
        df=sample_data,
        table_name="users",
        namespace="demo",
        mode="overwrite",
        catalog_config=catalog_config
    )
    print("✓ Data written to Iceberg table")
    
    # Read data back
    df_read = read_iceberg_table(
        table_name="users",
        namespace="demo",
        catalog_config=catalog_config
    )
    print("✓ Data read from Iceberg table:")
    print(df_read.head())


def example_class_based_operations():
    """Example using the IcebergUtils class for advanced operations."""
    print("\n=== Advanced Operations with IcebergUtils Class ===")
    
    # Initialize utils with configuration
    catalog_config = {
        "type": "hadoop",
        "warehouse": "./warehouse"
    }
    
    utils = IcebergUtils(catalog_config=catalog_config)
    
    # Create additional sample data
    new_users = pd.DataFrame({
        'user_id': [6, 7, 8],
        'username': ['frank', 'grace', 'henry'],
        'email': ['frank@example.com', 'grace@example.com', 'henry@example.com'],
        'age': [27, 31, 29],
        'signup_date': pd.to_datetime(['2023-06-15', '2023-07-20', '2023-08-10'])
    })
    
    # Append new data
    utils.write_dataframe_to_iceberg(
        df=new_users,
        table_name="users",
        namespace="demo",
        mode="append"
    )
    print("✓ Appended new users to table")
    
    # Read with filters
    filtered_users = utils.read_iceberg_table_with_filter(
        table_name="users",
        filters={"age": [25, 30, 35]},  # Users with specific ages
        namespace="demo"
    )
    print("✓ Filtered users (age 25, 30, or 35):")
    print(filtered_users)
    
    # Get table metadata
    metadata = utils.get_table_metadata("users", "demo")
    print("\n✓ Table metadata:")
    print(f"Location: {metadata['location']}")
    print(f"Schema: {metadata['schema']}")
    print(f"Properties: {metadata['properties']}")
    
    # List all tables in namespace
    tables = utils.list_tables("demo")
    print(f"\n✓ Tables in 'demo' namespace: {tables}")


def example_spark_operations():
    """Example using Spark integration (requires PySpark)."""
    print("\n=== Spark Integration Example ===")
    
    try:
        from pyspark.sql import SparkSession
        
        # Create Spark session with Iceberg configuration
        spark = SparkSession.builder \
            .appName("IcebergExample") \
            .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
            .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkSessionCatalog") \
            .config("spark.sql.catalog.spark_catalog.type", "hive") \
            .config("spark.sql.catalog.local", "org.apache.iceberg.spark.SparkCatalog") \
            .config("spark.sql.catalog.local.type", "hadoop") \
            .config("spark.sql.catalog.local.warehouse", "./warehouse") \
            .getOrCreate()
        
        utils = IcebergUtils(spark_session=spark)
        
        # Create Spark DataFrame
        spark_data = [
            (9, 'iris', 'iris@example.com', 26, '2023-09-15'),
            (10, 'jack', 'jack@example.com', 33, '2023-10-20')
        ]
        
        columns = ['user_id', 'username', 'email', 'age', 'signup_date']
        spark_df = spark.createDataFrame(spark_data, columns)
        
        # Write using Spark
        utils.write_spark_dataframe_to_iceberg(
            df=spark_df,
            table_name="users",
            namespace="demo",
            mode="append"
        )
        print("✓ Written data using Spark")
        
        # Read using Spark
        spark_read_df = utils.read_iceberg_table_spark("users", "demo")
        print("✓ Read data using Spark:")
        spark_read_df.show()
        
        spark.stop()
        
    except ImportError:
        print("⚠ Spark not available. Install PySpark to run Spark examples.")
    except Exception as e:
        print(f"⚠ Spark example failed: {e}")


def example_maintenance_operations():
    """Example of table maintenance operations."""
    print("\n=== Table Maintenance Operations ===")
    
    catalog_config = {
        "type": "hadoop",
        "warehouse": "./warehouse"
    }
    
    utils = IcebergUtils(catalog_config=catalog_config)
    
    try:
        # These operations typically require Spark
        print("Attempting table maintenance operations...")
        
        # Compact table (requires Spark)
        utils.compact_table("users", "demo")
        print("✓ Table compacted")
        
        # Expire old snapshots (requires Spark)
        utils.expire_snapshots("users", older_than_days=1, namespace="demo")
        print("✓ Old snapshots expired")
        
    except Exception as e:
        print(f"⚠ Maintenance operations require Spark setup: {e}")


def example_custom_schema():
    """Example of creating table with custom schema."""
    print("\n=== Custom Schema Example ===")
    
    try:
        from pyiceberg.schema import Schema
        from pyiceberg.types import NestedField, StringType, IntegerType, TimestampType
        
        # Define custom schema
        custom_schema = Schema(
            NestedField(1, "product_id", StringType(), required=True),
            NestedField(2, "product_name", StringType(), required=True),
            NestedField(3, "price", IntegerType(), required=False),
            NestedField(4, "created_at", TimestampType(), required=True)
        )
        
        catalog_config = {
            "type": "hadoop",
            "warehouse": "./warehouse"
        }
        
        utils = IcebergUtils(catalog_config=catalog_config)
        
        # Create table with custom schema
        table = utils.create_iceberg_table(
            table_name="products",
            schema=custom_schema,
            namespace="demo",
            properties={"format-version": "2"}
        )
        print("✓ Created table with custom schema")
        
        # Create sample data matching the schema
        products_data = pd.DataFrame({
            'product_id': ['P001', 'P002', 'P003'],
            'product_name': ['Laptop', 'Mouse', 'Keyboard'],
            'price': [999, 25, 75],
            'created_at': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03'])
        })
        
        # Write data to the new table
        utils.write_dataframe_to_iceberg(
            df=products_data,
            table_name="products",
            namespace="demo",
            mode="append"
        )
        print("✓ Added data to custom schema table")
        
        # Read back the data
        products_df = utils.read_iceberg_table("products", "demo")
        print("✓ Products table data:")
        print(products_df)
        
    except ImportError:
        print("⚠ PyIceberg schema types not available")
    except Exception as e:
        print(f"⚠ Custom schema example failed: {e}")


if __name__ == "__main__":
    """Run all examples."""
    
    print("🚀 Iceberg Utils Examples")
    print("=" * 50)
    
    try:
        # Run basic examples
        example_basic_operations()
        example_class_based_operations()
        
        # Run advanced examples
        example_spark_operations()
        example_maintenance_operations()
        example_custom_schema()
        
        print("\n" + "=" * 50)
        print("✅ Examples completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("2. For Spark operations, ensure Java 8+ is installed")
        print("3. Check that the warehouse directory is writable")
        print("4. Verify catalog configuration matches your setup")