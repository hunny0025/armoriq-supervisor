"""
Planner: converts user input into a multi-step plan.
Supports all original commands plus new operational, monitoring, and security test commands.
"""

from datetime import datetime


class Planner:
    def parse(self, user_input: str) -> list[dict]:
        """
        Return a list of action dictionaries.
        Each action contains agent, action, and relevant paths.
        """
        inp = user_input.lower().strip()
        actions = []

        # ─────────────── ORIGINAL COMMANDS ───────────────
        if "clean and organize workspace" in inp:
            actions.append({
                "agent": "CleanerAgent",
                "action": "delete",
                "path": "workspace/temp/file.tmp"
            })
            actions.append({
                "agent": "OrganizerAgent",
                "action": "move",
                "source": "workspace/log.txt",
                "dest": "workspace/logs/log.txt"
            })

        elif "clean workspace" in inp:
            actions.append({
                "agent": "CleanerAgent",
                "action": "delete",
                "path": "workspace/temp"
            })

        elif "organize files" in inp or "organize workspace" in inp:
            actions.append({
                "agent": "OrganizerAgent",
                "action": "move",
                "source": "workspace/log.txt",
                "dest": "workspace/logs/log.txt"
            })

        elif "delete system" in inp or "delete system config" in inp:
            actions.append({
                "agent": "CleanerAgent",
                "action": "delete",
                "path": "system/config"
            })

        # ─────────────── OPERATIONS ───────────────
        elif "archive logs" in inp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            actions.append({
                "agent": "OrganizerAgent",
                "action": "move",
                "source": "workspace/logs",
                "dest": f"workspace/archive/logs_{timestamp}"
            })

        elif "create test file" in inp:
            actions.append({
                "agent": "OrganizerAgent",
                "action": "create",
                "path": "workspace/test.txt"
            })

        # ─────────────── MONITORING ───────────────
        elif "check workspace status" in inp:
            actions.append({
                "agent": "MonitorAgent",
                "action": "read",
                "path": "workspace",
                "read_mode": "status"
            })

        elif "preview clean workspace" in inp:
            actions.append({
                "agent": "MonitorAgent",
                "action": "read",
                "path": "workspace/temp",
                "read_mode": "preview"
            })

        # ─────────────── SECURITY TEST ───────────────
        elif "access system folder" in inp:
            actions.append({
                "agent": "MonitorAgent",
                "action": "read",
                "path": "system/",
                "read_mode": "status"
            })

        return actions
