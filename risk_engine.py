"""
Risk Engine: classifies action risk level with structured reasoning.
LOW: read-only operations inside workspace.
MEDIUM: file create / move / delete inside workspace.
HIGH: any access outside workspace or to system directory.
"""


class RiskEngine:
    @staticmethod
    def assess(action: dict) -> tuple[str, str]:
        """
        Returns (risk_level, reason):
          risk_level: 'LOW' | 'MEDIUM' | 'HIGH'
          reason:     human-readable structured rationale
        """
        action_type = action.get("action", "")
        paths = []

        if action_type in ("delete", "create", "read"):
            if "path" in action:
                paths.append(action["path"])
        elif action_type == "move":
            if "source" in action:
                paths.append(action["source"])
            if "dest" in action:
                paths.append(action["dest"])

        # ── HIGH risk checks ──────────────────────────────
        for p in paths:
            if not p:
                continue
            p_norm = p.rstrip("/")
            p_low = p_norm.lower()

            # System directory
            if p_low.startswith("system") or "system/" in p_low:
                return "HIGH", f"Access to protected system directory: '{p}'"

            # Outside sandbox
            if not p_norm.startswith("workspace"):
                return "HIGH", f"Path escapes sandbox boundary: '{p}'"

            # Attempt to delete workspace root itself
            if action_type == "delete" and p_norm in ("workspace", "workspace/"):
                return "HIGH", "Attempt to delete workspace root directory"

        # ── MEDIUM risk checks ────────────────────────────
        if action_type == "delete":
            return "MEDIUM", "Destructive delete operation inside workspace"
        if action_type == "move":
            return "MEDIUM", "File move operation inside workspace"
        if action_type == "create":
            return "MEDIUM", "File creation operation inside workspace"

        # ── LOW (read-only) ───────────────────────────────
        if action_type == "read":
            return "LOW", "Read-only monitoring operation inside sandbox"

        return "LOW", "No significant risk identified"
