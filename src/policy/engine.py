from typing import Dict, Any, List
from datetime import datetime

class PolicyEngine:
    """
    Attribute-Based Access Control (ABAC) Engine.
    Evaluates JSON policies against request context.
    """
    
    def evaluate(
        self,
        user_attrs: Dict[str, Any],
        resource_attrs: Dict[str, Any],
        env_attrs: Dict[str, Any],
        policy: Dict[str, Any]
    ) -> bool:
        """
        Returns True if ALLOW, False if DENY.
        """
        rules = policy.get("rules", {})
        
        # 1. User Attributes Check
        for key, required_val in rules.get("user", {}).items():
            actual_val = user_attrs.get(key)
            if actual_val != required_val:
                return False  # Attribute mismatch
        
        # 2. Resource Attributes Check
        for key, required_val in rules.get("resource", {}).items():
            actual_val = resource_attrs.get(key)
            if actual_val != required_val:
                return False
                
        # 3. Environment Check (e.g., Time, Location)
        # Simple implementation
        env_rules = rules.get("env", {})
        if "min_hour" in env_rules:
            current_hour = datetime.now().hour
            if current_hour < env_rules["min_hour"]:
                return False
                
        return True

# Example Policy Structure (for reference/testing):
# {
#   "id": "finance-policy-1",
#   "rules": {
#       "user": { "dept": "finance", "clearance": "level-3" },
#       "resource": { "type": "payroll" },
#       "env": { "min_hour": 9 }
#   }
# }
