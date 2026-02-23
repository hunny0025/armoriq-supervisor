"""
Risk Engine: classifies action risk level and provides reason.
Now classifies any path outside 'workspace/' as HIGH risk.
"""

class RiskEngine:
    @staticmethod
    def assess(action: dict) -> tuple[str, str]:
        """
        Returns (risk_level, reason) where risk_level is LOW, MEDIUM, HIGH.
        """
        action_type = action.get("action")
        paths = []

        if action_type in ("delete", "create"):
            if "path" in action:
                paths.append(action["path"])
        elif action_type == "move":
            if "source" in action:
                paths.append(action["source"])
            if "dest" in action:
                paths.append(action["dest"])

        risk_level = "LOW"
        reason = "No significant risk"

        # HIGH risk checks
        for p in paths:
            if not p:
                continue
            p_low = p.lower()
            # Paths outside workspace are HIGH
            if not p.startswith("workspace/"):
                return "HIGH", f"Path outside sandbox: {p}"
            if "system" in p_low or p_low.startswith("system"):
                return "HIGH", "Path involves system directory (simulated)"
            if action_type == "delete" and p.strip('/') == "workspace":
                return "HIGH", "Attempt to delete workspace root"

        # MEDIUM risk checks
        if action_type == "delete" and any(p.startswith("workspace/") for p in paths if p):
            risk_level = "MEDIUM"
            reason = "Deleting files inside workspace"
        elif action_type == "move":
            risk_level = "MEDIUM"
            reason = "Moving files inside workspace"

        return risk_level, reason
