"""
Progress tracker for multi-agent workflows
Stores progress updates that can be polled by the frontend
"""
from typing import Dict, List
from datetime import datetime

class ProgressTracker:
    """Singleton to track multi-agent progress"""

    _instance = None
    _progress_store: Dict[str, List[Dict]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def start_workflow(self, session_id: str):
        """Start tracking a new workflow"""
        self._progress_store[session_id] = []

    def add_progress(self, session_id: str, step: str, message: str, data: Dict = None):
        """Add a progress update"""
        if session_id not in self._progress_store:
            self._progress_store[session_id] = []

        self._progress_store[session_id].append({
            'timestamp': datetime.now().isoformat(),
            'step': step,
            'message': message,
            'data': data or {}
        })

    def get_progress(self, session_id: str) -> List[Dict]:
        """Get all progress for a session"""
        return self._progress_store.get(session_id, [])

    def clear_progress(self, session_id: str):
        """Clear progress for a session"""
        if session_id in self._progress_store:
            del self._progress_store[session_id]

# Global instance
progress_tracker = ProgressTracker()
