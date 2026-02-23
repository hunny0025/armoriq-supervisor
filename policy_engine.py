"""
Policy Engine: validates an action against a scope token.
"""

import os

class PolicyEngine:
    @staticmethod
    def validate(action: dict, scope_token: dict) -> tuple[bool, str]:
        """
        Returns (allowed, reason).
        """
        if not scope_token:
            return False, "No scope token provided (agent unknown)"

        allowed_actions = scope_token.get("allowed_actions", [])
        allowed_paths = scope_token.get("allowed_paths", [])
        action_type = action.get("action")

        if action_type not in allowed_actions:
            return False, f"Action '{action_type}' not allowed for this agent"

        # Collect paths to check
        paths_to_check = []
        if action_type in ("delete", "create"):
            if "path" in action:
                paths_to_check.append(action["path"])
            else:
                return False, "Missing path for action"
        elif action_type == "move":
            if "source" in action and "dest" in action:
                paths_to_check.append(action["source"])
                paths_to_check.append(action["dest"])
            else:
                return False, "Missing source or dest for move"
        else:
            return False, f"Unknown action type: {action_type}"

        for path in paths_to_check:
            if not PolicyEngine._is_path_allowed(path, allowed_paths):
                return False, f"Path '{path}' is outside allowed scope: {allowed_paths}"

        return True, "Policy check passed"

    @staticmethod
    def _is_path_allowed(path: str, allowed_paths: list) -> bool:
        norm_path = os.path.normpath(path)
        for allowed in allowed_paths:
            norm_allowed = os.path.normpath(allowed)
            if norm_path == norm_allowed or norm_path.startswith(norm_allowed + os.sep):
                return True
        return False
