"""
Simple request tracking for debugging.
"""
import uuid
import time
import logging

logger = logging.getLogger(__name__)


class RequestContext:
    """Track request execution time and details."""
    
    def __init__(self, user_id: str = "anonymous"):
        self.request_id = str(uuid.uuid4())[:8]
        self.user_id = user_id
        self.start_time = time.time()
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time in seconds."""
        return time.time() - self.start_time
    
    def log_result(self, success: bool, intent: str = None):
        """Log query result."""
        elapsed = self.get_elapsed_time()
        logger.info(
            f"[{self.request_id}] {self.user_id}: "
            f"success={success}, intent={intent}, time={elapsed:.2f}s"
        )

