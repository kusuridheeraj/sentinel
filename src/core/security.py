import hashlib
import json
from datetime import datetime

def calculate_log_hash(prev_hash: str, timestamp: datetime, actor_id: str, action: str, resource: str, context: dict) -> str:
    """
    Computes SHA-256 hash for the log entry.
    Structure: SHA256(prev_hash + timestamp_iso + actor + action + resource + context_json)
    """
    # Ensure consistent serialization for context
    context_str = json.dumps(context, sort_keys=True) if context else "{}"
    
    # Create the payload string
    # We use ISO format for timestamp to ensure consistency across DB/App
    payload = f"{prev_hash}{timestamp.isoformat()}{actor_id}{action}{resource}{context_str}"
    
    return hashlib.sha256(payload.encode()).hexdigest()
