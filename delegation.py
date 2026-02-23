"""
Delegation Manager: loads agent permissions and issues scope tokens.
"""

import json

class DelegationManager:
    def __init__(self, policies_path="policies.json"):
        with open(policies_path, 'r') as f:
            self.policies = json.load(f)
        self.agents = self.policies.get("agents", {})

    def get_scope_token(self, agent_name: str) -> dict | None:
        """
        Return a scope token for the agent: a dict containing allowed actions and paths.
        """
        perms = self.agents.get(agent_name)
        if perms:
            return {
                "agent": agent_name,
                "allowed_actions": perms["allowed_actions"],
                "allowed_paths": perms["allowed_paths"]
            }
        return None
