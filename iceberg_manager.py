import json
import time
import hashlib
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class Snapshot:
    """Represents a snapshot with metadata and data state"""
    snapshot_id: str
    timestamp: float
    description: str
    data_state: Dict[str, Any]
    parent_snapshot_id: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary for serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Snapshot':
        """Create snapshot from dictionary"""
        return cls(**data)


class IcebergManager:
    """
    Iceberg snapshot manager with history and rollback capabilities
    """
    
    def __init__(self, storage_path: str = "iceberg_snapshots"):
        self.storage_path = storage_path
        self.snapshots: Dict[str, Snapshot] = {}
        self.current_snapshot_id: Optional[str] = None
        self.current_data_state: Dict[str, Any] = {}
        
        # Ensure storage directory exists
        os.makedirs(storage_path, exist_ok=True)
        
        # Load existing snapshots
        self._load_snapshots()

    def _generate_snapshot_id(self, data_state: Dict[str, Any]) -> str:
        """Generate unique snapshot ID based on data state and timestamp"""
        content = json.dumps(data_state, sort_keys=True) + str(time.time())
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _load_snapshots(self):
        """Load snapshots from storage"""
        manifest_path = os.path.join(self.storage_path, "manifest.json")
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                    self.current_snapshot_id = manifest.get('current_snapshot_id')
                    
                    # Load individual snapshots
                    for snapshot_id in manifest.get('snapshots', []):
                        snapshot_path = os.path.join(self.storage_path, f"{snapshot_id}.json")
                        if os.path.exists(snapshot_path):
                            with open(snapshot_path, 'r') as sf:
                                snapshot_data = json.load(sf)
                                self.snapshots[snapshot_id] = Snapshot.from_dict(snapshot_data)
                    
                    # Load current data state
                    if self.current_snapshot_id and self.current_snapshot_id in self.snapshots:
                        self.current_data_state = self.snapshots[self.current_snapshot_id].data_state.copy()
            except Exception as e:
                print(f"Warning: Could not load snapshots: {e}")

    def _save_snapshots(self):
        """Save snapshots to storage"""
        manifest = {
            'current_snapshot_id': self.current_snapshot_id,
            'snapshots': list(self.snapshots.keys()),
            'last_updated': time.time()
        }
        
        manifest_path = os.path.join(self.storage_path, "manifest.json")
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)

    def create_snapshot(self, description: str = "", metadata: Dict[str, Any] = None) -> str:
        """
        Create a new snapshot of the current data state
        
        Args:
            description: Optional description for the snapshot
            metadata: Additional metadata to store with the snapshot
            
        Returns:
            The ID of the created snapshot
        """
        if metadata is None:
            metadata = {}
            
        snapshot_id = self._generate_snapshot_id(self.current_data_state)
        
        # Avoid duplicate snapshots
        if snapshot_id in self.snapshots:
            return snapshot_id
            
        snapshot = Snapshot(
            snapshot_id=snapshot_id,
            timestamp=time.time(),
            description=description or f"Snapshot created at {datetime.now().isoformat()}",
            data_state=self.current_data_state.copy(),
            parent_snapshot_id=self.current_snapshot_id,
            metadata=metadata
        )
        
        self.snapshots[snapshot_id] = snapshot
        self.current_snapshot_id = snapshot_id
        
        # Save snapshot to file
        snapshot_path = os.path.join(self.storage_path, f"{snapshot_id}.json")
        with open(snapshot_path, 'w') as f:
            json.dump(snapshot.to_dict(), f, indent=2)
        
        self._save_snapshots()
        
        return snapshot_id

    def get_snapshot_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get snapshot history ordered by timestamp (newest first)
        
        Args:
            limit: Maximum number of snapshots to return
            
        Returns:
            List of snapshot information dictionaries
        """
        sorted_snapshots = sorted(
            self.snapshots.values(), 
            key=lambda s: s.timestamp, 
            reverse=True
        )
        
        if limit:
            sorted_snapshots = sorted_snapshots[:limit]
            
        return [
            {
                'snapshot_id': s.snapshot_id,
                'timestamp': s.timestamp,
                'datetime': datetime.fromtimestamp(s.timestamp).isoformat(),
                'description': s.description,
                'parent_snapshot_id': s.parent_snapshot_id,
                'metadata': s.metadata
            }
            for s in sorted_snapshots
        ]

    def rollback_to_snapshot(self, snapshot_id: str) -> bool:
        """
        Rollback to a specific snapshot
        
        Args:
            snapshot_id: The ID of the snapshot to rollback to
            
        Returns:
            True if rollback was successful, False otherwise
        """
        if snapshot_id not in self.snapshots:
            raise ValueError(f"Snapshot {snapshot_id} not found")
            
        snapshot = self.snapshots[snapshot_id]
        self.current_data_state = snapshot.data_state.copy()
        self.current_snapshot_id = snapshot_id
        
        self._save_snapshots()
        
        return True

    def rollback_to_previous(self) -> bool:
        """
        Rollback to the previous snapshot
        
        Returns:
            True if rollback was successful, False otherwise
        """
        if not self.current_snapshot_id:
            raise ValueError("No current snapshot to rollback from")
            
        current_snapshot = self.snapshots[self.current_snapshot_id]
        if not current_snapshot.parent_snapshot_id:
            raise ValueError("No previous snapshot available")
            
        return self.rollback_to_snapshot(current_snapshot.parent_snapshot_id)

    def get_snapshot_details(self, snapshot_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific snapshot
        
        Args:
            snapshot_id: The ID of the snapshot
            
        Returns:
            Dictionary containing snapshot details
        """
        if snapshot_id not in self.snapshots:
            raise ValueError(f"Snapshot {snapshot_id} not found")
            
        snapshot = self.snapshots[snapshot_id]
        return {
            'snapshot_id': snapshot.snapshot_id,
            'timestamp': snapshot.timestamp,
            'datetime': datetime.fromtimestamp(snapshot.timestamp).isoformat(),
            'description': snapshot.description,
            'parent_snapshot_id': snapshot.parent_snapshot_id,
            'metadata': snapshot.metadata,
            'data_state': snapshot.data_state
        }

    def delete_snapshot(self, snapshot_id: str) -> bool:
        """
        Delete a specific snapshot
        
        Args:
            snapshot_id: The ID of the snapshot to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        if snapshot_id not in self.snapshots:
            raise ValueError(f"Snapshot {snapshot_id} not found")
            
        # Don't allow deleting the current snapshot
        if snapshot_id == self.current_snapshot_id:
            raise ValueError("Cannot delete the current snapshot")
            
        # Remove from memory
        del self.snapshots[snapshot_id]
        
        # Remove file
        snapshot_path = os.path.join(self.storage_path, f"{snapshot_id}.json")
        if os.path.exists(snapshot_path):
            os.remove(snapshot_path)
            
        self._save_snapshots()
        
        return True

    def cleanup_old_snapshots(self, keep_count: int = 10) -> int:
        """
        Clean up old snapshots, keeping only the most recent ones
        
        Args:
            keep_count: Number of recent snapshots to keep
            
        Returns:
            Number of snapshots deleted
        """
        if len(self.snapshots) <= keep_count:
            return 0
            
        # Sort by timestamp and keep the most recent
        sorted_snapshots = sorted(
            self.snapshots.values(), 
            key=lambda s: s.timestamp, 
            reverse=True
        )
        
        to_delete = sorted_snapshots[keep_count:]
        deleted_count = 0
        
        for snapshot in to_delete:
            # Don't delete current snapshot
            if snapshot.snapshot_id != self.current_snapshot_id:
                try:
                    self.delete_snapshot(snapshot.snapshot_id)
                    deleted_count += 1
                except ValueError:
                    pass  # Skip if already deleted or is current
                    
        return deleted_count

    def update_data_state(self, key: str, value: Any):
        """
        Update the current data state
        
        Args:
            key: The key to update
            value: The new value
        """
        self.current_data_state[key] = value

    def get_current_data_state(self) -> Dict[str, Any]:
        """
        Get the current data state
        
        Returns:
            Dictionary containing the current data state
        """
        return self.current_data_state.copy()

    def get_current_snapshot_id(self) -> Optional[str]:
        """
        Get the current snapshot ID
        
        Returns:
            Current snapshot ID or None if no snapshots exist
        """
        return self.current_snapshot_id

    def compare_snapshots(self, snapshot_id1: str, snapshot_id2: str) -> Dict[str, Any]:
        """
        Compare two snapshots and return the differences
        
        Args:
            snapshot_id1: First snapshot ID
            snapshot_id2: Second snapshot ID
            
        Returns:
            Dictionary containing the differences
        """
        if snapshot_id1 not in self.snapshots:
            raise ValueError(f"Snapshot {snapshot_id1} not found")
        if snapshot_id2 not in self.snapshots:
            raise ValueError(f"Snapshot {snapshot_id2} not found")
            
        snap1 = self.snapshots[snapshot_id1]
        snap2 = self.snapshots[snapshot_id2]
        
        state1 = snap1.data_state
        state2 = snap2.data_state
        
        # Find differences
        added = {}
        removed = {}
        modified = {}
        
        all_keys = set(state1.keys()) | set(state2.keys())
        
        for key in all_keys:
            if key in state1 and key in state2:
                if state1[key] != state2[key]:
                    modified[key] = {'from': state1[key], 'to': state2[key]}
            elif key in state1:
                removed[key] = state1[key]
            else:
                added[key] = state2[key]
        
        return {
            'snapshot1': snapshot_id1,
            'snapshot2': snapshot_id2,
            'added': added,
            'removed': removed,
            'modified': modified
        }