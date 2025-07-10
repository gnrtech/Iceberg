# Iceberg Snapshot Manager

A comprehensive snapshot management system with history tracking and rollback capabilities. Perfect for managing data states, configurations, or any application that needs versioning and rollback functionality.

## Features

### Core Snapshot Operations
- **Create Snapshots**: Capture current data state with descriptions and metadata
- **Snapshot History**: View chronological history of all snapshots
- **Rollback Functionality**: Revert to any previous snapshot or the immediate previous state
- **Snapshot Comparison**: Compare differences between any two snapshots
- **Persistent Storage**: Snapshots are saved to disk and persist across sessions

### Advanced Features
- **Automatic Cleanup**: Remove old snapshots while keeping recent ones
- **Metadata Support**: Attach custom metadata to snapshots
- **Parent Tracking**: Maintain snapshot lineage with parent-child relationships
- **Error Handling**: Robust error handling with descriptive messages
- **Data Integrity**: Prevent accidental deletion of current snapshots

## Quick Start

```python
from iceberg_manager import IcebergManager

# Initialize the manager
manager = IcebergManager("my_snapshots")

# Update data state
manager.update_data_state("users", {"alice": {"role": "admin"}})
manager.update_data_state("config", {"version": "1.0.0"})

# Create a snapshot
snapshot_id = manager.create_snapshot("Initial setup")

# Modify data
manager.update_data_state("config", {"version": "1.1.0"})
manager.create_snapshot("Version update")

# View snapshot history
history = manager.get_snapshot_history()
for snap in history:
    print(f"{snap['snapshot_id']}: {snap['description']}")

# Rollback to previous snapshot
manager.rollback_to_previous()
```

## API Reference

### IcebergManager Class

#### Constructor
```python
IcebergManager(storage_path: str = "iceberg_snapshots")
```
- `storage_path`: Directory to store snapshot data

#### Data Management
```python
update_data_state(key: str, value: Any)
get_current_data_state() -> Dict[str, Any]
get_current_snapshot_id() -> Optional[str]
```

#### Snapshot Operations
```python
create_snapshot(description: str = "", metadata: Dict[str, Any] = None) -> str
get_snapshot_history(limit: Optional[int] = None) -> List[Dict[str, Any]]
get_snapshot_details(snapshot_id: str) -> Dict[str, Any]
delete_snapshot(snapshot_id: str) -> bool
```

#### Rollback Operations
```python
rollback_to_snapshot(snapshot_id: str) -> bool
rollback_to_previous() -> bool
```

#### Analysis Operations
```python
compare_snapshots(snapshot_id1: str, snapshot_id2: str) -> Dict[str, Any]
```

#### Maintenance Operations
```python
cleanup_old_snapshots(keep_count: int = 10) -> int
```

## Usage Examples

### Basic Workflow
```python
# Initialize manager
manager = IcebergManager()

# Set initial data
manager.update_data_state("counter", 0)
manager.update_data_state("settings", {"theme": "dark"})

# Create snapshots as you make changes
snap1 = manager.create_snapshot("Initial state")

manager.update_data_state("counter", 10)
snap2 = manager.create_snapshot("Counter updated")

manager.update_data_state("settings", {"theme": "light"})
snap3 = manager.create_snapshot("Theme changed")

# View what changed
comparison = manager.compare_snapshots(snap1, snap3)
print("Changes:", comparison)

# Rollback if needed
manager.rollback_to_snapshot(snap1)
print("Rolled back to:", manager.get_current_data_state())
```

### With Metadata
```python
# Create snapshots with custom metadata
manager.create_snapshot(
    description="Database migration v2.1",
    metadata={
        "author": "admin",
        "migration_id": "m_001", 
        "database_version": "2.1.0"
    }
)
```

### Cleanup Management
```python
# Keep only the 5 most recent snapshots
deleted_count = manager.cleanup_old_snapshots(keep_count=5)
print(f"Cleaned up {deleted_count} old snapshots")
```

## Data Storage

The manager stores data in the specified directory with the following structure:
```
storage_path/
├── manifest.json          # Index of all snapshots
├── <snapshot_id1>.json    # Individual snapshot data
├── <snapshot_id2>.json
└── ...
```

## Error Handling

The manager provides comprehensive error handling:
- `ValueError`: For invalid snapshot IDs or operations
- Automatic recovery from corrupted storage
- Protection against deleting current snapshots
- Graceful handling of missing files

## Running Tests

Test the functionality with the included test suite:
```bash
python test_iceberg.py
```

## Demo

Run the demonstration to see all features in action:
```bash
python demo.py
```

The demo includes:
- Automated demonstration of all features
- Interactive mode for hands-on testing
- Example workflows and use cases

## Use Cases

- **Configuration Management**: Track configuration changes with easy rollback
- **Data Pipeline States**: Snapshot data transformations at each stage
- **Application State**: Save and restore application states during development
- **Experiment Tracking**: Version different model parameters or data sets
- **Backup and Recovery**: Create recovery points for critical data states

## Requirements

- Python 3.7+
- Standard library only (no external dependencies)

## License

This project is open source and available under the MIT License.