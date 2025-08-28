"""Event normalization to canonical format."""

from typing import Dict, Any, Optional


def to_canonical(event: Dict[str, Any]) -> Dict[str, Any]:
    """Convert any event format to canonical format.
    
    Canonical format:
    {
        "trace_id": str,
        "span_id": str,
        "role": "http" | "sql" | "redis" | "mongo" | "s3",
        "meta": {
            "http": {...},
            "sql": {...},
            "redis": {...},
            "mongo": {...},
            "s3": {...}
        }
    }
    """
    # Already in canonical format
    if "role" in event and "meta" in event:
        return event
    
    # Try to detect format and normalize
    canonical = {
        "trace_id": event.get("trace_id", event.get("id", "unknown")),
        "span_id": event.get("span_id", event.get("id", "unknown")),
        "role": event.get("role", "unknown"),
        "meta": event.get("meta", {})
    }
    
    # Detect role from content if not specified
    if canonical["role"] == "unknown":
        if "http" in event or "url" in event:
            canonical["role"] = "http"
            if "http" not in canonical["meta"]:
                canonical["meta"]["http"] = {
                    "method": event.get("method", "POST"),
                    "url": event.get("url", ""),
                    "headers": event.get("headers", {}),
                    "body": event.get("body", {})
                }
        elif "sql" in event or "query" in event:
            canonical["role"] = "sql"
            if "sql" not in canonical["meta"]:
                canonical["meta"]["sql"] = {
                    "query": event.get("query", event.get("sql", ""))
                }
        elif "redis" in event or "command" in event:
            canonical["role"] = "redis"
            if "redis" not in canonical["meta"]:
                canonical["meta"]["redis"] = {
                    "command": event.get("command", "")
                }
        elif "mongo" in event or "op" in event:
            canonical["role"] = "mongo"
            if "mongo" not in canonical["meta"]:
                canonical["meta"]["mongo"] = {
                    "op": event.get("op", "")
                }
        elif "s3" in event:
            canonical["role"] = "s3"
            if "s3" not in canonical["meta"]:
                canonical["meta"]["s3"] = {
                    "op": event.get("op", "")
                }
    
    return canonical