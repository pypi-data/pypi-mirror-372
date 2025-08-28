"""PII redaction and compliance for AgentCorrect."""

import re
from typing import Dict, Any, Set, Tuple


class Redactor:
    """Redact PII from events."""
    
    def __init__(self):
        # Common PII patterns
        self.patterns = {
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'phone': re.compile(r'\b(?:\+?1[-.]?)?\(?[0-9]{3}\)?[-.]?[0-9]{3}[-.]?[0-9]{4}\b'),
            'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            'credit_card': re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
            'api_key': re.compile(r'\b(sk_|pk_|api_|key_)[a-zA-Z0-9]{20,}\b'),
        }
    
    def redact_value(self, value: Any) -> Any:
        """Redact PII from a single value."""
        if isinstance(value, str):
            for name, pattern in self.patterns.items():
                value = pattern.sub(f"[REDACTED_{name.upper()}]", value)
        elif isinstance(value, dict):
            return {k: self.redact_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self.redact_value(item) for item in value]
        return value
    
    def redact_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Redact PII from an entire event."""
        return self.redact_value(event)


def allowlist_and_redact(event: Dict[str, Any], domain_allowlist: Set[str], redactor: Redactor) -> Tuple[Dict[str, Any], bool]:
    """Check domain allowlist and redact PII.
    
    Returns:
        Tuple of (redacted_event, is_allowed)
    """
    is_allowed = True
    
    # Check domain allowlist for HTTP events
    if event.get("role") == "http":
        url = event.get("meta", {}).get("http", {}).get("url", "")
        if url and domain_allowlist:
            # Extract domain from URL
            domain_match = re.match(r'https?://([^/]+)', url)
            if domain_match:
                domain = domain_match.group(1).lower()
                # Remove port if present
                domain = domain.split(':')[0]
                if domain not in domain_allowlist:
                    is_allowed = False
    
    # Redact PII
    redacted = redactor.redact_event(event)
    
    return redacted, is_allowed