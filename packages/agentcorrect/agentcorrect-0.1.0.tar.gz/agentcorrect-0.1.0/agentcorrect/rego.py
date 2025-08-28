"""OPA Rego policy generation for AgentCorrect."""

import json
from pathlib import Path
from typing import Dict, Any, List


def spec_from_findings(findings: List[Dict]) -> Dict[str, Any]:
    """Generate agent spec from findings."""
    spec = {
        "version": "1.0",
        "rules": [],
        "blocked_domains": set(),
        "required_headers": {},
        "sql_restrictions": []
    }
    
    for finding in findings:
        if finding.get("type") == "payment_no_idempotency":
            # Add idempotency requirement
            url = finding.get("url", "")
            if "stripe" in url:
                spec["required_headers"]["stripe.com"] = ["Idempotency-Key"]
            elif "paypal" in url:
                spec["required_headers"]["paypal.com"] = ["PayPal-Request-Id"]
        
        elif finding.get("type") == "sql_unbounded_write":
            spec["sql_restrictions"].append("require_where_clause")
    
    return spec


def emit_rego_bundle(output_dir: Path, spec: Dict[str, Any]) -> bool:
    """Generate OPA Rego policy bundle."""
    try:
        policy = generate_rego_policy(spec)
        
        # Write policy.rego
        with open(output_dir / "policy.rego", "w") as f:
            f.write(policy)
        
        # Write agent_spec.json
        with open(output_dir / "agent_spec.json", "w") as f:
            # Convert sets to lists for JSON serialization
            spec_json = {
                "version": spec.get("version", "1.0"),
                "rules": spec.get("rules", []),
                "blocked_domains": list(spec.get("blocked_domains", [])),
                "required_headers": spec.get("required_headers", {}),
                "sql_restrictions": spec.get("sql_restrictions", [])
            }
            json.dump(spec_json, f, indent=2)
        
        # Write agent_spec.yaml
        with open(output_dir / "agent_spec.yaml", "w") as f:
            f.write(spec_to_yaml(spec))
        
        return True
    
    except Exception as e:
        print(f"Error generating Rego policy: {e}")
        return False


def generate_rego_policy(spec: Dict[str, Any]) -> str:
    """Generate OPA Rego policy from spec."""
    policy = """package agentcorrect

default allow = false

# Allow if no violations found
allow {
    count(violations) == 0
}

violations[msg] {
    # Check for missing idempotency keys
    input.role == "http"
    contains(input.meta.http.url, "stripe.com")
    not input.meta.http.headers["Idempotency-Key"]
    msg := "Missing Idempotency-Key for Stripe payment"
}

violations[msg] {
    # Check for SQL without WHERE
    input.role == "sql"
    contains(upper(input.meta.sql.query), "DELETE FROM")
    not contains(upper(input.meta.sql.query), "WHERE")
    msg := "SQL DELETE without WHERE clause"
}

violations[msg] {
    # Check for Redis FLUSHALL
    input.role == "redis"
    contains(upper(input.meta.redis.command), "FLUSHALL")
    msg := "Redis FLUSHALL detected"
}

violations[msg] {
    # Check for MongoDB drop
    input.role == "mongo"
    input.meta.mongo.op == "dropDatabase"
    msg := "MongoDB dropDatabase detected"
}
"""
    return policy


def spec_to_yaml(spec: Dict[str, Any]) -> str:
    """Convert spec to YAML format."""
    yaml_content = f"""version: {spec.get('version', '1.0')}

rules:
"""
    
    if spec.get("required_headers"):
        yaml_content += "  required_headers:\n"
        for domain, headers in spec["required_headers"].items():
            yaml_content += f"    {domain}:\n"
            for header in headers:
                yaml_content += f"      - {header}\n"
    
    if spec.get("sql_restrictions"):
        yaml_content += "  sql_restrictions:\n"
        for restriction in spec["sql_restrictions"]:
            yaml_content += f"    - {restriction}\n"
    
    if spec.get("blocked_domains"):
        yaml_content += "  blocked_domains:\n"
        for domain in spec["blocked_domains"]:
            yaml_content += f"    - {domain}\n"
    
    return yaml_content