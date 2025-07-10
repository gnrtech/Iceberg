#!/usr/bin/env python3
"""
Demonstration script for Iceberg snapshot manager
Shows how to use snapshot history and rollback functionality
"""

from iceberg_manager import IcebergManager
import json
import time


def demo_snapshot_operations():
    """Demonstrate snapshot operations"""
    print("=== Iceberg Snapshot Manager Demo ===\n")
    
    # Initialize the manager
    manager = IcebergManager("demo_snapshots")
    
    # 1. Create initial data state
    print("1. Setting up initial data state...")
    manager.update_data_state("users", {"alice": {"age": 30, "role": "admin"}})
    manager.update_data_state("config", {"version": "1.0.0", "debug": True})
    manager.update_data_state("settings", {"theme": "dark", "notifications": True})
    
    # Create first snapshot
    snapshot1_id = manager.create_snapshot("Initial setup with users and config")
    print(f"   Created snapshot: {snapshot1_id}")
    print(f"   Current state: {manager.get_current_data_state()}")
    
    time.sleep(1)  # Small delay to ensure different timestamps
    
    # 2. Modify data and create another snapshot
    print("\n2. Modifying data state...")
    manager.update_data_state("users", {
        "alice": {"age": 30, "role": "admin"},
        "bob": {"age": 25, "role": "user"}
    })
    manager.update_data_state("config", {"version": "1.1.0", "debug": False})
    
    snapshot2_id = manager.create_snapshot("Added Bob user and updated config")
    print(f"   Created snapshot: {snapshot2_id}")
    print(f"   Current state: {manager.get_current_data_state()}")
    
    time.sleep(1)
    
    # 3. More modifications
    print("\n3. Further modifications...")
    manager.update_data_state("users", {
        "alice": {"age": 31, "role": "admin"},
        "bob": {"age": 25, "role": "user"},
        "charlie": {"age": 28, "role": "moderator"}
    })
    manager.update_data_state("settings", {"theme": "light", "notifications": False})
    
    snapshot3_id = manager.create_snapshot("Added Charlie and updated settings", 
                                         metadata={"author": "demo_script", "version": "1.2.0"})
    print(f"   Created snapshot: {snapshot3_id}")
    print(f"   Current state: {manager.get_current_data_state()}")
    
    # 4. Display snapshot history
    print("\n4. Snapshot History:")
    history = manager.get_snapshot_history()
    for i, snap in enumerate(history, 1):
        print(f"   {i}. ID: {snap['snapshot_id']}")
        print(f"      Time: {snap['datetime']}")
        print(f"      Description: {snap['description']}")
        print(f"      Parent: {snap['parent_snapshot_id']}")
        if snap['metadata']:
            print(f"      Metadata: {snap['metadata']}")
        print()
    
    # 5. Rollback to previous snapshot
    print("5. Rolling back to previous snapshot...")
    print(f"   Current snapshot: {manager.get_current_snapshot_id()}")
    
    success = manager.rollback_to_previous()
    print(f"   Rollback successful: {success}")
    print(f"   New current snapshot: {manager.get_current_snapshot_id()}")
    print(f"   Current state: {manager.get_current_data_state()}")
    
    # 6. Rollback to specific snapshot
    print("\n6. Rolling back to first snapshot...")
    success = manager.rollback_to_snapshot(snapshot1_id)
    print(f"   Rollback successful: {success}")
    print(f"   Current state: {manager.get_current_data_state()}")
    
    # 7. Compare snapshots
    print("\n7. Comparing snapshots...")
    comparison = manager.compare_snapshots(snapshot1_id, snapshot3_id)
    print(f"   Comparison between {snapshot1_id} and {snapshot3_id}:")
    print(f"   Added: {comparison['added']}")
    print(f"   Removed: {comparison['removed']}")
    print(f"   Modified: {comparison['modified']}")
    
    # 8. Get detailed snapshot info
    print("\n8. Detailed snapshot information:")
    details = manager.get_snapshot_details(snapshot2_id)
    print(f"   Snapshot {snapshot2_id} details:")
    print(f"   Description: {details['description']}")
    print(f"   Timestamp: {details['datetime']}")
    print(f"   Data state: {details['data_state']}")
    
    # 9. Cleanup demonstration
    print("\n9. Cleanup operations:")
    print(f"   Total snapshots before cleanup: {len(manager.snapshots)}")
    
    # This won't delete much since we only have 3 snapshots
    deleted = manager.cleanup_old_snapshots(keep_count=2)
    print(f"   Deleted {deleted} old snapshots")
    print(f"   Remaining snapshots: {len(manager.snapshots)}")
    
    # 10. Create a few more snapshots to demonstrate cleanup
    print("\n10. Creating more snapshots for cleanup demo...")
    for i in range(5):
        manager.update_data_state("counter", i)
        manager.create_snapshot(f"Counter update {i}")
        time.sleep(0.1)
    
    print(f"    Total snapshots: {len(manager.snapshots)}")
    deleted = manager.cleanup_old_snapshots(keep_count=3)
    print(f"    Deleted {deleted} old snapshots during cleanup")
    print(f"    Remaining snapshots: {len(manager.snapshots)}")
    
    print("\n=== Demo Complete ===")


def interactive_demo():
    """Interactive demonstration"""
    print("\n=== Interactive Snapshot Manager ===")
    manager = IcebergManager("interactive_snapshots")
    
    while True:
        print("\nAvailable commands:")
        print("1. set <key> <value>    - Set a data value")
        print("2. get                  - Show current data state")
        print("3. snapshot <desc>      - Create a snapshot")
        print("4. history [limit]      - Show snapshot history")
        print("5. rollback <id>        - Rollback to specific snapshot")
        print("6. rollback_prev        - Rollback to previous snapshot")
        print("7. compare <id1> <id2>  - Compare two snapshots")
        print("8. details <id>         - Show snapshot details")
        print("9. cleanup <keep>       - Cleanup old snapshots")
        print("10. quit                - Exit")
        
        try:
            cmd = input("\nEnter command: ").strip().split()
            if not cmd:
                continue
                
            if cmd[0] == "set" and len(cmd) >= 3:
                key = cmd[1]
                value = " ".join(cmd[2:])
                # Try to parse as JSON first
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    pass  # Keep as string
                manager.update_data_state(key, value)
                print(f"Set {key} = {value}")
                
            elif cmd[0] == "get":
                print(f"Current data state: {manager.get_current_data_state()}")
                
            elif cmd[0] == "snapshot":
                desc = " ".join(cmd[1:]) if len(cmd) > 1 else ""
                snap_id = manager.create_snapshot(desc)
                print(f"Created snapshot: {snap_id}")
                
            elif cmd[0] == "history":
                limit = int(cmd[1]) if len(cmd) > 1 else None
                history = manager.get_snapshot_history(limit)
                for i, snap in enumerate(history, 1):
                    print(f"{i}. {snap['snapshot_id']} - {snap['description']} ({snap['datetime']})")
                    
            elif cmd[0] == "rollback" and len(cmd) == 2:
                success = manager.rollback_to_snapshot(cmd[1])
                print(f"Rollback successful: {success}")
                
            elif cmd[0] == "rollback_prev":
                success = manager.rollback_to_previous()
                print(f"Rollback to previous successful: {success}")
                
            elif cmd[0] == "compare" and len(cmd) == 3:
                comparison = manager.compare_snapshots(cmd[1], cmd[2])
                print(f"Comparison:")
                print(f"Added: {comparison['added']}")
                print(f"Removed: {comparison['removed']}")
                print(f"Modified: {comparison['modified']}")
                
            elif cmd[0] == "details" and len(cmd) == 2:
                details = manager.get_snapshot_details(cmd[1])
                print(f"Snapshot details:")
                print(f"ID: {details['snapshot_id']}")
                print(f"Description: {details['description']}")
                print(f"Timestamp: {details['datetime']}")
                print(f"Data state: {details['data_state']}")
                
            elif cmd[0] == "cleanup" and len(cmd) == 2:
                keep = int(cmd[1])
                deleted = manager.cleanup_old_snapshots(keep)
                print(f"Deleted {deleted} old snapshots")
                
            elif cmd[0] == "quit":
                print("Goodbye!")
                break
                
            else:
                print("Invalid command or missing parameters")
                
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    # Run automated demo
    demo_snapshot_operations()
    
    # Ask if user wants to try interactive mode
    response = input("\nWould you like to try the interactive mode? (y/n): ").lower()
    if response in ['y', 'yes']:
        interactive_demo()