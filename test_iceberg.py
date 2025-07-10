#!/usr/bin/env python3
"""
Test script for Iceberg snapshot manager
Tests snapshot history and rollback functionality
"""

import os
import shutil
import tempfile
from iceberg_manager import IcebergManager, Snapshot


def test_basic_functionality():
    """Test basic snapshot operations"""
    print("Testing basic functionality...")
    
    # Use temporary directory for testing
    test_dir = tempfile.mkdtemp()
    try:
        manager = IcebergManager(test_dir)
        
        # Test data state updates
        manager.update_data_state("key1", "value1")
        manager.update_data_state("key2", {"nested": "data"})
        
        assert manager.get_current_data_state() == {
            "key1": "value1", 
            "key2": {"nested": "data"}
        }
        
        # Test snapshot creation
        snapshot_id = manager.create_snapshot("Test snapshot")
        assert snapshot_id is not None
        assert manager.get_current_snapshot_id() == snapshot_id
        
        print("✓ Basic functionality tests passed")
        
    finally:
        shutil.rmtree(test_dir)


def test_snapshot_history():
    """Test snapshot history functionality"""
    print("Testing snapshot history...")
    
    test_dir = tempfile.mkdtemp()
    try:
        manager = IcebergManager(test_dir)
        
        # Create multiple snapshots
        manager.update_data_state("version", 1)
        snap1 = manager.create_snapshot("Version 1")
        
        manager.update_data_state("version", 2)
        snap2 = manager.create_snapshot("Version 2")
        
        manager.update_data_state("version", 3)
        snap3 = manager.create_snapshot("Version 3")
        
        # Test history retrieval
        history = manager.get_snapshot_history()
        assert len(history) == 3
        
        # Should be ordered by timestamp (newest first)
        assert history[0]['snapshot_id'] == snap3
        assert history[1]['snapshot_id'] == snap2
        assert history[2]['snapshot_id'] == snap1
        
        # Test limited history
        limited_history = manager.get_snapshot_history(limit=2)
        assert len(limited_history) == 2
        
        print("✓ Snapshot history tests passed")
        
    finally:
        shutil.rmtree(test_dir)


def test_rollback_functionality():
    """Test rollback functionality"""
    print("Testing rollback functionality...")
    
    test_dir = tempfile.mkdtemp()
    try:
        manager = IcebergManager(test_dir)
        
        # Create snapshots with different states
        manager.update_data_state("counter", 1)
        snap1 = manager.create_snapshot("Counter = 1")
        
        manager.update_data_state("counter", 2)
        snap2 = manager.create_snapshot("Counter = 2")
        
        manager.update_data_state("counter", 3)
        snap3 = manager.create_snapshot("Counter = 3")
        
        # Test rollback to specific snapshot
        success = manager.rollback_to_snapshot(snap1)
        assert success
        assert manager.get_current_data_state()["counter"] == 1
        assert manager.get_current_snapshot_id() == snap1
        
        # Go back to latest
        manager.rollback_to_snapshot(snap3)
        assert manager.get_current_data_state()["counter"] == 3
        
        # Test rollback to previous
        success = manager.rollback_to_previous()
        assert success
        assert manager.get_current_data_state()["counter"] == 2
        assert manager.get_current_snapshot_id() == snap2
        
        print("✓ Rollback functionality tests passed")
        
    finally:
        shutil.rmtree(test_dir)


def test_snapshot_comparison():
    """Test snapshot comparison functionality"""
    print("Testing snapshot comparison...")
    
    test_dir = tempfile.mkdtemp()
    try:
        manager = IcebergManager(test_dir)
        
        # Create first snapshot
        manager.update_data_state("a", 1)
        manager.update_data_state("b", 2)
        snap1 = manager.create_snapshot("State 1")
        
        # Modify and create second snapshot
        manager.update_data_state("a", 10)  # modified
        manager.update_data_state("c", 3)   # added
        del manager.current_data_state["b"]  # removed
        snap2 = manager.create_snapshot("State 2")
        
        # Compare snapshots
        comparison = manager.compare_snapshots(snap1, snap2)
        
        assert comparison["added"] == {"c": 3}
        assert comparison["removed"] == {"b": 2}
        assert comparison["modified"] == {"a": {"from": 1, "to": 10}}
        
        print("✓ Snapshot comparison tests passed")
        
    finally:
        shutil.rmtree(test_dir)


def test_persistence():
    """Test data persistence across manager instances"""
    print("Testing persistence...")
    
    test_dir = tempfile.mkdtemp()
    try:
        # Create manager and snapshots
        manager1 = IcebergManager(test_dir)
        manager1.update_data_state("persistent", "data")
        snap_id = manager1.create_snapshot("Persistent snapshot")
        
        # Create new manager instance with same storage
        manager2 = IcebergManager(test_dir)
        
        # Verify data was loaded
        assert manager2.get_current_snapshot_id() == snap_id
        assert manager2.get_current_data_state() == {"persistent": "data"}
        
        # Verify history is available
        history = manager2.get_snapshot_history()
        assert len(history) == 1
        assert history[0]["snapshot_id"] == snap_id
        
        print("✓ Persistence tests passed")
        
    finally:
        shutil.rmtree(test_dir)


def test_cleanup_functionality():
    """Test snapshot cleanup functionality"""
    print("Testing cleanup functionality...")
    
    test_dir = tempfile.mkdtemp()
    try:
        manager = IcebergManager(test_dir)
        
        # Create many snapshots
        snapshot_ids = []
        for i in range(10):
            manager.update_data_state("counter", i)
            snap_id = manager.create_snapshot(f"Snapshot {i}")
            snapshot_ids.append(snap_id)
        
        assert len(manager.snapshots) == 10
        
        # Cleanup keeping only 3 most recent
        deleted_count = manager.cleanup_old_snapshots(keep_count=3)
        
        # Should delete 7 snapshots (but not the current one)
        assert deleted_count <= 7
        assert len(manager.snapshots) <= 3
        
        # Current snapshot should still be available
        assert manager.get_current_snapshot_id() in manager.snapshots
        
        print("✓ Cleanup functionality tests passed")
        
    finally:
        shutil.rmtree(test_dir)


def test_error_handling():
    """Test error handling"""
    print("Testing error handling...")
    
    test_dir = tempfile.mkdtemp()
    try:
        manager = IcebergManager(test_dir)
        
        # Test rollback to non-existent snapshot
        try:
            manager.rollback_to_snapshot("non-existent")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass  # Expected
        
        # Test rollback to previous when no snapshots exist
        try:
            manager.rollback_to_previous()
            assert False, "Should have raised ValueError"
        except ValueError:
            pass  # Expected
        
        # Create a snapshot and test delete current snapshot
        manager.update_data_state("test", "data")
        snap_id = manager.create_snapshot("Test snapshot")
        
        try:
            manager.delete_snapshot(snap_id)
            assert False, "Should have raised ValueError"
        except ValueError:
            pass  # Expected - can't delete current snapshot
        
        print("✓ Error handling tests passed")
        
    finally:
        shutil.rmtree(test_dir)


def run_all_tests():
    """Run all tests"""
    print("=== Running Iceberg Manager Tests ===\n")
    
    test_functions = [
        test_basic_functionality,
        test_snapshot_history,
        test_rollback_functionality,
        test_snapshot_comparison,
        test_persistence,
        test_cleanup_functionality,
        test_error_handling
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__} FAILED: {e}")
            failed += 1
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False


if __name__ == "__main__":
    run_all_tests()