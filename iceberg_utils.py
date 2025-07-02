"""
Iceberg Utilities Module

This module provides utility functions for working with Apache Iceberg tables.
Includes functions for reading, writing, and managing Iceberg tables using
both PyIceberg and PySpark.

Dependencies:
    - pyiceberg
    - pandas
    - pyarrow
    - pyspark (optional, for Spark integration)
"""

import logging
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
import pandas as pd

try:
    from pyiceberg.catalog import load_catalog
    from pyiceberg.table import Table
    from pyiceberg.expressions import EqualTo, In, IsNull, NotNull, GreaterThan, LessThan
    from pyiceberg.schema import Schema
    from pyiceberg.types import *
    PYICEBERG_AVAILABLE = True
except ImportError:
    PYICEBERG_AVAILABLE = False
    logging.warning("PyIceberg not available. Install with: pip install pyiceberg")

try:
    from pyspark.sql import SparkSession, DataFrame as SparkDataFrame
    from pyspark.sql.types import StructType
    PYSPARK_AVAILABLE = True
except ImportError:
    PYSPARK_AVAILABLE = False
    logging.warning("PySpark not available. Install with: pip install pyspark")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IcebergUtils:
    """Utility class for Apache Iceberg operations."""
    
    def __init__(self, catalog_config: Optional[Dict[str, Any]] = None, spark_session: Optional['SparkSession'] = None):
        """
        Initialize IcebergUtils.
        
        Args:
            catalog_config: Configuration for Iceberg catalog
            spark_session: Optional Spark session for Spark-based operations
        """
        self.catalog_config = catalog_config or {}
        self.spark = spark_session
        self._catalog = None
        
    def _get_catalog(self):
        """Get or create Iceberg catalog."""
        if not PYICEBERG_AVAILABLE:
            raise ImportError("PyIceberg is required. Install with: pip install pyiceberg")
            
        if self._catalog is None:
            self._catalog = load_catalog("default", **self.catalog_config)
        return self._catalog
    
    def _get_spark(self):
        """Get or create Spark session."""
        if not PYSPARK_AVAILABLE:
            raise ImportError("PySpark is required for Spark operations. Install with: pip install pyspark")
            
        if self.spark is None:
            self.spark = SparkSession.builder \
                .appName("IcebergUtils") \
                .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
                .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkSessionCatalog") \
                .config("spark.sql.catalog.spark_catalog.type", "hive") \
                .config("spark.sql.catalog.local", "org.apache.iceberg.spark.SparkCatalog") \
                .config("spark.sql.catalog.local.type", "hadoop") \
                .config("spark.sql.catalog.local.warehouse", "warehouse") \
                .getOrCreate()
        return self.spark

    # ========== READ OPERATIONS ==========
    
    def read_iceberg_table(self, table_name: str, namespace: str = "default") -> pd.DataFrame:
        """
        Read an Iceberg table into a Pandas DataFrame.
        
        Args:
            table_name: Name of the Iceberg table
            namespace: Namespace/database name
            
        Returns:
            pd.DataFrame: Table data as Pandas DataFrame
        """
        try:
            catalog = self._get_catalog()
            table = catalog.load_table(f"{namespace}.{table_name}")
            
            # Scan and convert to Pandas DataFrame
            scan = table.scan()
            arrow_table = scan.to_arrow()
            df = arrow_table.to_pandas()
            
            logger.info(f"Successfully read table {namespace}.{table_name} with {len(df)} rows")
            return df
            
        except Exception as e:
            logger.error(f"Error reading table {namespace}.{table_name}: {str(e)}")
            raise
    
    def read_iceberg_table_spark(self, table_name: str, namespace: str = "default") -> 'SparkDataFrame':
        """
        Read an Iceberg table using Spark.
        
        Args:
            table_name: Name of the Iceberg table
            namespace: Namespace/database name
            
        Returns:
            SparkDataFrame: Table data as Spark DataFrame
        """
        spark = self._get_spark()
        
        try:
            df = spark.read.format("iceberg").load(f"{namespace}.{table_name}")
            logger.info(f"Successfully read table {namespace}.{table_name} using Spark")
            return df
            
        except Exception as e:
            logger.error(f"Error reading table {namespace}.{table_name} with Spark: {str(e)}")
            raise
    
    def read_iceberg_table_with_filter(self, 
                                     table_name: str, 
                                     filters: Dict[str, Any],
                                     namespace: str = "default") -> pd.DataFrame:
        """
        Read an Iceberg table with filters applied.
        
        Args:
            table_name: Name of the Iceberg table
            filters: Dictionary of column filters
            namespace: Namespace/database name
            
        Returns:
            pd.DataFrame: Filtered table data
        """
        try:
            catalog = self._get_catalog()
            table = catalog.load_table(f"{namespace}.{table_name}")
            
            # Build filter expressions
            scan = table.scan()
            for column, value in filters.items():
                if isinstance(value, list):
                    scan = scan.filter(In(column, value))
                elif value is None:
                    scan = scan.filter(IsNull(column))
                else:
                    scan = scan.filter(EqualTo(column, value))
            
            arrow_table = scan.to_arrow()
            df = arrow_table.to_pandas()
            
            logger.info(f"Successfully read filtered table {namespace}.{table_name} with {len(df)} rows")
            return df
            
        except Exception as e:
            logger.error(f"Error reading filtered table {namespace}.{table_name}: {str(e)}")
            raise

    # ========== WRITE OPERATIONS ==========
    
    def write_dataframe_to_iceberg(self, 
                                 df: pd.DataFrame, 
                                 table_name: str,
                                 namespace: str = "default",
                                 mode: str = "append",
                                 schema: Optional[Schema] = None) -> None:
        """
        Write a Pandas DataFrame to an Iceberg table.
        
        Args:
            df: Pandas DataFrame to write
            table_name: Name of the target Iceberg table
            namespace: Namespace/database name
            mode: Write mode ('append', 'overwrite')
            schema: Optional schema for the table
        """
        try:
            catalog = self._get_catalog()
            full_table_name = f"{namespace}.{table_name}"
            
            # Convert DataFrame to Arrow Table
            import pyarrow as pa
            arrow_table = pa.Table.from_pandas(df)
            
            try:
                # Try to load existing table
                table = catalog.load_table(full_table_name)
                
                if mode == "overwrite":
                    table.overwrite(arrow_table)
                    logger.info(f"Overwritten table {full_table_name} with {len(df)} rows")
                else:  # append
                    table.append(arrow_table)
                    logger.info(f"Appended {len(df)} rows to table {full_table_name}")
                    
            except Exception:
                # Table doesn't exist, create it
                if schema is None:
                    # Infer schema from Arrow table
                    from pyiceberg.schema import Schema
                    from pyiceberg.types import *
                    
                    schema_fields = []
                    for field in arrow_table.schema:
                        iceberg_type = self._arrow_to_iceberg_type(field.type)
                        schema_fields.append(NestedField(
                            field_id=len(schema_fields) + 1,
                            name=field.name,
                            field_type=iceberg_type,
                            required=not field.nullable
                        ))
                    schema = Schema(*schema_fields)
                
                table = catalog.create_table(full_table_name, schema=schema)
                table.append(arrow_table)
                logger.info(f"Created new table {full_table_name} and added {len(df)} rows")
                
        except Exception as e:
            logger.error(f"Error writing DataFrame to table {full_table_name}: {str(e)}")
            raise
    
    def write_spark_dataframe_to_iceberg(self,
                                       df: 'SparkDataFrame',
                                       table_name: str,
                                       namespace: str = "default",
                                       mode: str = "append") -> None:
        """
        Write a Spark DataFrame to an Iceberg table.
        
        Args:
            df: Spark DataFrame to write
            table_name: Name of the target Iceberg table
            namespace: Namespace/database name
            mode: Write mode ('append', 'overwrite')
        """
        try:
            full_table_name = f"{namespace}.{table_name}"
            
            df.write \
                .format("iceberg") \
                .mode(mode) \
                .save(full_table_name)
            
            logger.info(f"Successfully wrote Spark DataFrame to {full_table_name} in {mode} mode")
            
        except Exception as e:
            logger.error(f"Error writing Spark DataFrame to table {full_table_name}: {str(e)}")
            raise

    # ========== TABLE MANAGEMENT ==========
    
    def create_iceberg_table(self,
                           table_name: str,
                           schema: Schema,
                           namespace: str = "default",
                           properties: Optional[Dict[str, str]] = None) -> Table:
        """
        Create a new Iceberg table.
        
        Args:
            table_name: Name of the table to create
            schema: Table schema
            namespace: Namespace/database name
            properties: Optional table properties
            
        Returns:
            Table: Created Iceberg table
        """
        try:
            catalog = self._get_catalog()
            full_table_name = f"{namespace}.{table_name}"
            
            table = catalog.create_table(
                full_table_name,
                schema=schema,
                properties=properties or {}
            )
            
            logger.info(f"Successfully created table {full_table_name}")
            return table
            
        except Exception as e:
            logger.error(f"Error creating table {full_table_name}: {str(e)}")
            raise
    
    def drop_iceberg_table(self, table_name: str, namespace: str = "default") -> None:
        """
        Drop an Iceberg table.
        
        Args:
            table_name: Name of the table to drop
            namespace: Namespace/database name
        """
        try:
            catalog = self._get_catalog()
            full_table_name = f"{namespace}.{table_name}"
            
            catalog.drop_table(full_table_name)
            logger.info(f"Successfully dropped table {full_table_name}")
            
        except Exception as e:
            logger.error(f"Error dropping table {full_table_name}: {str(e)}")
            raise
    
    def list_tables(self, namespace: str = "default") -> List[str]:
        """
        List all tables in a namespace.
        
        Args:
            namespace: Namespace to list tables from
            
        Returns:
            List[str]: List of table names
        """
        try:
            catalog = self._get_catalog()
            tables = catalog.list_tables(namespace)
            
            table_names = [str(table) for table in tables]
            logger.info(f"Found {len(table_names)} tables in namespace {namespace}")
            return table_names
            
        except Exception as e:
            logger.error(f"Error listing tables in namespace {namespace}: {str(e)}")
            raise
    
    def get_table_metadata(self, table_name: str, namespace: str = "default") -> Dict[str, Any]:
        """
        Get metadata for an Iceberg table.
        
        Args:
            table_name: Name of the table
            namespace: Namespace/database name
            
        Returns:
            Dict[str, Any]: Table metadata
        """
        try:
            catalog = self._get_catalog()
            table = catalog.load_table(f"{namespace}.{table_name}")
            
            metadata = {
                "location": table.location(),
                "schema": str(table.schema()),
                "spec": str(table.spec()),
                "sort_order": str(table.sort_order()),
                "properties": table.properties,
                "current_snapshot": table.current_snapshot(),
                "snapshots": [snap.snapshot_id for snap in table.snapshots()]
            }
            
            logger.info(f"Retrieved metadata for table {namespace}.{table_name}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error getting metadata for table {namespace}.{table_name}: {str(e)}")
            raise

    # ========== MAINTENANCE OPERATIONS ==========
    
    def compact_table(self, table_name: str, namespace: str = "default") -> None:
        """
        Compact an Iceberg table (removes old data files).
        
        Args:
            table_name: Name of the table to compact
            namespace: Namespace/database name
        """
        spark = self._get_spark()
        
        try:
            full_table_name = f"{namespace}.{table_name}"
            
            # Use Spark to perform compaction
            spark.sql(f"CALL system.rewrite_data_files(table => '{full_table_name}')")
            
            logger.info(f"Successfully compacted table {full_table_name}")
            
        except Exception as e:
            logger.error(f"Error compacting table {full_table_name}: {str(e)}")
            raise
    
    def expire_snapshots(self, 
                        table_name: str, 
                        older_than_days: int = 7,
                        namespace: str = "default") -> None:
        """
        Expire old snapshots from an Iceberg table.
        
        Args:
            table_name: Name of the table
            older_than_days: Remove snapshots older than this many days
            namespace: Namespace/database name
        """
        spark = self._get_spark()
        
        try:
            full_table_name = f"{namespace}.{table_name}"
            
            # Calculate timestamp for expiration
            from datetime import datetime, timedelta
            expire_timestamp = datetime.now() - timedelta(days=older_than_days)
            timestamp_ms = int(expire_timestamp.timestamp() * 1000)
            
            spark.sql(f"""
                CALL system.expire_snapshots(
                    table => '{full_table_name}',
                    older_than => {timestamp_ms}L
                )
            """)
            
            logger.info(f"Successfully expired snapshots older than {older_than_days} days for table {full_table_name}")
            
        except Exception as e:
            logger.error(f"Error expiring snapshots for table {full_table_name}: {str(e)}")
            raise

    # ========== HELPER METHODS ==========
    
    def _arrow_to_iceberg_type(self, arrow_type):
        """Convert Arrow type to Iceberg type."""
        import pyarrow as pa
        from pyiceberg.types import *
        
        if pa.types.is_int64(arrow_type):
            return LongType()
        elif pa.types.is_int32(arrow_type):
            return IntegerType()
        elif pa.types.is_float64(arrow_type):
            return DoubleType()
        elif pa.types.is_float32(arrow_type):
            return FloatType()
        elif pa.types.is_string(arrow_type):
            return StringType()
        elif pa.types.is_boolean(arrow_type):
            return BooleanType()
        elif pa.types.is_date32(arrow_type):
            return DateType()
        elif pa.types.is_timestamp(arrow_type):
            return TimestampType()
        else:
            return StringType()  # Default fallback


# ========== CONVENIENCE FUNCTIONS ==========

def read_iceberg_table(table_name: str, 
                      namespace: str = "default",
                      catalog_config: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """
    Convenience function to read an Iceberg table.
    
    Args:
        table_name: Name of the Iceberg table
        namespace: Namespace/database name
        catalog_config: Optional catalog configuration
        
    Returns:
        pd.DataFrame: Table data as Pandas DataFrame
    """
    utils = IcebergUtils(catalog_config=catalog_config)
    return utils.read_iceberg_table(table_name, namespace)


def write_dataframe_to_iceberg(df: pd.DataFrame,
                              table_name: str,
                              namespace: str = "default",
                              mode: str = "append",
                              catalog_config: Optional[Dict[str, Any]] = None) -> None:
    """
    Convenience function to write a DataFrame to an Iceberg table.
    
    Args:
        df: Pandas DataFrame to write
        table_name: Name of the target Iceberg table
        namespace: Namespace/database name
        mode: Write mode ('append', 'overwrite')
        catalog_config: Optional catalog configuration
    """
    utils = IcebergUtils(catalog_config=catalog_config)
    utils.write_dataframe_to_iceberg(df, table_name, namespace, mode)


def get_table_info(table_name: str,
                  namespace: str = "default",
                  catalog_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Convenience function to get table information.
    
    Args:
        table_name: Name of the table
        namespace: Namespace/database name
        catalog_config: Optional catalog configuration
        
    Returns:
        Dict[str, Any]: Table metadata
    """
    utils = IcebergUtils(catalog_config=catalog_config)
    return utils.get_table_metadata(table_name, namespace)


# ========== EXAMPLE USAGE ==========

if __name__ == "__main__":
    # Example usage
    
    # Initialize utils
    catalog_config = {
        "uri": "http://localhost:8181",  # REST catalog URI
        "warehouse": "s3://your-bucket/warehouse/"  # Warehouse location
    }
    
    utils = IcebergUtils(catalog_config=catalog_config)
    
    # Example: Create sample DataFrame
    sample_data = pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
        'age': [25, 30, 35, 28, 32],
        'city': ['New York', 'London', 'Tokyo', 'Paris', 'Sydney']
    })
    
    # Write DataFrame to Iceberg table
    utils.write_dataframe_to_iceberg(
        df=sample_data,
        table_name="users",
        namespace="demo",
        mode="overwrite"
    )
    
    # Read table back
    df = utils.read_iceberg_table("users", "demo")
    print("Read data:")
    print(df.head())
    
    # Read with filters
    filtered_df = utils.read_iceberg_table_with_filter(
        table_name="users",
        filters={"city": ["New York", "London"]},
        namespace="demo"
    )
    print("Filtered data:")
    print(filtered_df.head())
    
    # Get table metadata
    metadata = utils.get_table_metadata("users", "demo")
    print("Table metadata:")
    print(metadata)