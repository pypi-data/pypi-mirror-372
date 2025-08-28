"""Coverage tracking for AgentCorrect."""

from typing import Dict, Any, Set


class CoverageTracker:
    """Track detection coverage statistics."""
    
    def __init__(self):
        self.total_events = 0
        self.events_by_role = {}
        self.checked_events = set()
        self.payment_events = 0
        self.sql_events = 0
        self.redis_events = 0
        self.mongo_events = 0
        self.s3_events = 0
    
    def process_event(self, event: Dict[str, Any]):
        """Track an event for coverage statistics."""
        self.total_events += 1
        
        role = event.get("role", "unknown")
        self.events_by_role[role] = self.events_by_role.get(role, 0) + 1
        
        # Track specific event types
        if role == "http":
            url = event.get("meta", {}).get("http", {}).get("url", "")
            if any(provider in url for provider in ["stripe", "paypal", "square", "adyen"]):
                self.payment_events += 1
        elif role == "sql":
            self.sql_events += 1
        elif role == "redis":
            self.redis_events += 1
        elif role == "mongo":
            self.mongo_events += 1
        elif role == "s3":
            self.s3_events += 1
    
    def record_checked(self, check_type: str, event: Dict[str, Any]):
        """Record that an event was checked."""
        event_id = f"{event.get('trace_id', '')}:{event.get('span_id', '')}"
        self.checked_events.add(f"{check_type}:{event_id}")
    
    def to_dict(self, total_events: int = None) -> Dict[str, Any]:
        """Get coverage statistics as a dictionary."""
        if total_events is None:
            total_events = self.total_events
        
        eligible_events = self.payment_events + self.sql_events
        checked_count = len(self.checked_events)
        
        return {
            "total_events": total_events,
            "events_by_role": self.events_by_role,
            "payment_events": self.payment_events,
            "sql_events": self.sql_events,
            "redis_events": self.redis_events,
            "mongo_events": self.mongo_events,
            "s3_events": self.s3_events,
            "eligible_events": eligible_events,
            "checked_events": checked_count,
            "coverage_percentage": (checked_count / eligible_events * 100) if eligible_events > 0 else 0
        }