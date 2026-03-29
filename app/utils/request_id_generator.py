"""
Simple request ID generator for tracking API requests.
Generates format: REQ-YYYYMMDD-XXXXXX (e.g., REQ-20260329-A7F2K)
"""
import random
import string
from datetime import datetime
from app.utils.logger import get_logger

logger = get_logger(__name__, component="request_id_generator")


def generate_request_id() -> str:
    """
    Generate a simple, unique request ID for tracking.
    
    Format: REQ-YYYYMMDD-XXXXXX
    Example: REQ-20260329-A7F2K
    
    Returns:
        str: Unique request identifier
    """
    try:
        # Get current date in YYYYMMDD format
        date_str = datetime.now().strftime("%Y%m%d")
        
        # Generate 6 random alphanumeric characters (uppercase)
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        request_id = f"REQ-{date_str}-{random_suffix}"
        logger.debug(f"Generated request ID: {request_id}")
        
        return request_id
    except Exception as e:
        logger.error(f"Failed to generate request ID: {e}")
        # Fallback: return timestamp-based ID
        fallback_id = f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        logger.info(f"Using fallback request ID: {fallback_id}")
        return fallback_id
