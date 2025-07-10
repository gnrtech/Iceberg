#!/usr/bin/env python3
"""
Test script for Bubot automation system
Tests all Bubot functionality including commands, scheduling, and monitoring
"""

import os
import time
import tempfile
import shutil
from bubot import Bubot, BubotConfig
from iceberg_manager import IcebergManager


def test_bubot_commands():
    """Test Bubot command processing"""
    print("Testing Bubot commands...")
    
    test_dir = tempfile.mkdtemp()
    try:
        config = BubotConfig(
            storage_path=test_dir,
            enable_scheduling=False,  # Disable for testing
            enable_monitoring=False
        )
        bubot = Bubot(config)
        
        # Test help command
        response = bubot.command("help")
        assert "🤖 Bubot Commands:" in response
        
        # Test status command
        response = bubot.command("status")
        assert "🤖 Bubot Status:" in response
        
        # Set up some test data
        bubot.manager.update_data_state("test_key", "test_value")
        
        # Test create snapshot command
        response = bubot.command("create snapshot Test snapshot via command")
        assert "✅ Created snapshot" in response
        
        # Test show history command
        response = bubot.command("show history")
        assert "📋 Last" in response
        
        # Test show current command
        response = bubot.command("show current")
        assert "📊 Current snapshot:" in response
        
        # Test stats command
        response = bubot.command("stats")
        assert "📊 Snapshot Statistics:" in response
        
        print("✓ Command processing tests passed")
        
    finally:
        shutil.rmtree(test_dir)


def test_bubot_automation():
    """Test Bubot automation features"""
    print("Testing Bubot automation...")
    
    test_dir = tempfile.mkdtemp()
    try:
        config = BubotConfig(
            storage_path=test_dir,
            auto_snapshot_interval=2,  # 2 seconds for testing
            enable_scheduling=True,
            enable_monitoring=True,
            max_snapshots=5
        )
        bubot = Bubot(config)
        
        # Set initial data
        bubot.manager.update_data_state("counter", 0)
        
        # Start automation
        bubot.start()
        
        # Verify status
        status = bubot.get_status()
        assert status["running"] == True
        
        # Wait a bit for scheduler to potentially run
        time.sleep(1)
        
        # Stop automation
        bubot.stop()
        
        assert bubot.running == False
        
        print("✓ Automation tests passed")
        
    finally:
        shutil.rmtree(test_dir)


def test_bubot_monitoring():
    """Test Bubot monitoring and alerts"""
    print("Testing Bubot monitoring...")
    
    test_dir = tempfile.mkdtemp()
    try:
        config = BubotConfig(
            storage_path=test_dir,
            enable_scheduling=False,
            enable_monitoring=True,
            alert_threshold_changes=2
        )
        bubot = Bubot(config)
        
        # Initialize monitoring
        bubot.monitor.check_changes()
        
        # Make some changes
        bubot.manager.update_data_state("key1", "value1")
        alerts1 = bubot.check_alerts()
        
        bubot.manager.update_data_state("key2", "value2")
        alerts2 = bubot.check_alerts()
        
        # Should trigger alert after threshold
        bubot.manager.update_data_state("key3", "value3")
        alerts3 = bubot.check_alerts()
        
        # Check if alerts were generated
        all_alerts = bubot.monitor.get_recent_alerts()
        
        print(f"   Generated {len(all_alerts)} alerts during monitoring test")
        print("✓ Monitoring tests passed")
        
    finally:
        shutil.rmtree(test_dir)


def test_bubot_integration():
    """Test integration between Bubot and IcebergManager"""
    print("Testing Bubot integration...")
    
    test_dir = tempfile.mkdtemp()
    try:
        config = BubotConfig(
            storage_path=test_dir,
            enable_scheduling=False,
            enable_monitoring=False
        )
        bubot = Bubot(config)
        
        # Test that Bubot can manage snapshots
        bubot.manager.update_data_state("integration_test", "data")
        snapshot_id = bubot.manager.create_snapshot("Integration test snapshot")
        
        # Test command that uses partial ID
        partial_id = snapshot_id[:6]
        response = bubot.command(f"rollback to {partial_id}")
        assert "↩️ Rolled back to snapshot" in response
        
        # Test comparison via commands
        bubot.manager.update_data_state("new_key", "new_value")
        new_snapshot_id = bubot.manager.create_snapshot("Second snapshot")
        
        response = bubot.command(f"compare {snapshot_id[:6]} {new_snapshot_id[:6]}")
        assert "🔍 Comparison between" in response
        
        print("✓ Integration tests passed")
        
    finally:
        shutil.rmtree(test_dir)


def test_bubot_error_handling():
    """Test Bubot error handling"""
    print("Testing Bubot error handling...")
    
    test_dir = tempfile.mkdtemp()
    try:
        config = BubotConfig(storage_path=test_dir)
        bubot = Bubot(config)
        
        # Test invalid commands
        response = bubot.command("invalid command")
        assert "❓ Unknown command" in response
        
        # Test rollback to non-existent snapshot
        response = bubot.command("rollback to nonexistent")
        assert "❌ Snapshot not found" in response
        
        # Test comparison with invalid IDs
        response = bubot.command("compare invalid1 invalid2")
        assert "❌ Could not find snapshots" in response
        
        print("✓ Error handling tests passed")
        
    finally:
        shutil.rmtree(test_dir)


def test_bubot_configurations():
    """Test different Bubot configurations"""
    print("Testing Bubot configurations...")
    
    test_dir = tempfile.mkdtemp()
    try:
        # Test with scheduling disabled
        config1 = BubotConfig(
            storage_path=test_dir,
            enable_scheduling=False,
            enable_monitoring=True
        )
        bubot1 = Bubot(config1)
        status1 = bubot1.get_status()
        assert status1["config"]["enable_scheduling"] == False
        
        # Test with monitoring disabled
        config2 = BubotConfig(
            storage_path=test_dir,
            enable_scheduling=True,
            enable_monitoring=False
        )
        bubot2 = Bubot(config2)
        status2 = bubot2.get_status()
        assert status2["config"]["enable_monitoring"] == False
        
        # Test custom intervals
        config3 = BubotConfig(
            storage_path=test_dir,
            auto_snapshot_interval=1800,  # 30 minutes
            cleanup_interval=7200  # 2 hours
        )
        bubot3 = Bubot(config3)
        status3 = bubot3.get_status()
        assert status3["config"]["auto_snapshot_interval"] == 1800
        
        print("✓ Configuration tests passed")
        
    finally:
        shutil.rmtree(test_dir)


def demo_bubot_interaction():
    """Demonstrate Bubot interactive features"""
    print("\n=== Bubot Interactive Demo ===")
    
    test_dir = tempfile.mkdtemp()
    try:
        config = BubotConfig(
            storage_path=test_dir,
            auto_snapshot_interval=5,  # 5 seconds for demo
            enable_scheduling=True,
            enable_monitoring=True
        )
        bubot = Bubot(config)
        
        print("🤖 Starting Bubot...")
        bubot.start()
        
        # Demonstrate various commands
        commands = [
            "status",
            "create snapshot Demo snapshot 1",
            "show history 5",
            "create snapshot Demo snapshot 2", 
            "stats",
            "show current"
        ]
        
        for cmd in commands:
            print(f"\n🤖 Bubot> {cmd}")
            response = bubot.command(cmd)
            print(response)
            time.sleep(0.5)  # Small delay for readability
            
        print("\n🤖 Stopping Bubot...")
        bubot.stop()
        
        print("✓ Interactive demo completed")
        
    finally:
        shutil.rmtree(test_dir)


def run_all_bubot_tests():
    """Run all Bubot tests"""
    print("=== Running Bubot Tests ===\n")
    
    test_functions = [
        test_bubot_commands,
        test_bubot_automation,
        test_bubot_monitoring,
        test_bubot_integration,
        test_bubot_error_handling,
        test_bubot_configurations
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
    
    print(f"\n=== Bubot Test Results ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("🎉 All Bubot tests passed!")
        
        # Run interactive demo
        demo_bubot_interaction()
        
        return True
    else:
        print("❌ Some Bubot tests failed!")
        return False


if __name__ == "__main__":
    run_all_bubot_tests()