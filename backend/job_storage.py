"""
Job Storage - Store completed job results for later retrieval
This allows the frontend to retrieve results even after connection drops
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class JobStorage:
    """
    Store job results in memory with expiration
    """

    def __init__(self, ttl_hours: int = 24):
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.ttl = timedelta(hours=ttl_hours)

    def store_result(self, session_id: str, result: Dict[str, Any]):
        """Store a completed job result"""
        self.jobs[session_id] = {
            'result': result,
            'timestamp': datetime.now(),
            'status': 'completed'
        }
        logger.info(f"📦 Stored job result for session {session_id[:8]}")

    def get_result(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a job result"""
        if session_id not in self.jobs:
            return None

        job = self.jobs[session_id]

        # Check if expired
        if datetime.now() - job['timestamp'] > self.ttl:
            del self.jobs[session_id]
            logger.info(f"🗑️  Expired job result for session {session_id[:8]}")
            return None

        return job['result']

    def cleanup_expired(self):
        """Remove expired job results"""
        now = datetime.now()
        expired = [
            sid for sid, job in self.jobs.items()
            if now - job['timestamp'] > self.ttl
        ]
        for sid in expired:
            del self.jobs[sid]
        if expired:
            logger.info(f"🗑️  Cleaned up {len(expired)} expired job results")


# Global job storage instance
job_storage = JobStorage()
