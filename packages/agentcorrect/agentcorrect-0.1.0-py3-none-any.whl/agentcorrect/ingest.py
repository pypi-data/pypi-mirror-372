"""Input handling and validation for AgentCorrect."""

import json
import sys
from pathlib import Path
from typing import Iterator, Dict, Any, Tuple


def validate_input(filepath: str) -> Tuple[bool, str]:
    """Validate input file exists and is readable."""
    if filepath == '-':
        return True, ""
    
    path = Path(filepath)
    if not path.exists():
        return False, f"File not found: {filepath}"
    if not path.is_file():
        return False, f"Not a file: {filepath}"
    if path.suffix not in ['.jsonl', '.json']:
        return False, f"Expected .jsonl or .json file, got: {path.suffix}"
    
    return True, ""


def stream_jsonl(filepath: str) -> Iterator[Dict[str, Any]]:
    """Stream events from JSONL file or stdin."""
    if filepath == '-':
        # Read from stdin
        for line in sys.stdin:
            line = line.strip()
            if line:
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"Warning: Skipping invalid JSON line: {e}", file=sys.stderr)
                    continue
    else:
        # Read from file
        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError as e:
                        print(f"Warning: Line {line_num}: {e}", file=sys.stderr)
                        continue