"""
History Manager: stores and retrieves decision history in history.json.
Stores command, agent, action, path, risk, decision, reason, timestamp.
"""

import json
import os
from datetime import datetime


class HistoryManager:
    def __init__(self, history_file="history.json"):
        self.history_file = history_file
        self.history = self._load()

    def _load(self) -> list:
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)

    def add_entry(self, command: str, agent: str, action_type: str, path: str,
                  risk: str, decision: str, reason: str):
        """Add a history entry with all observability fields."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "agent": agent,
            "action": action_type,
            "path": path,
            "risk": risk,
            "decision": decision,
            "reason": reason
        }
        self.history.append(entry)
        self._save()

    def get_all(self) -> list:
        """Return all history entries (newest first)."""
        return list(reversed(self.history))

    def show_history(self):
        """Print history to console with backward-compatible field access."""
        if not self.history:
            print("No history available.")
            return
        print("\n--- Execution History ---")
        for idx, entry in enumerate(self.history, 1):
            timestamp = entry.get("timestamp", "N/A")
            command   = entry.get("command",   entry.get("action", "N/A"))
            agent     = entry.get("agent",     "N/A")
            action    = entry.get("action",    "N/A")
            risk      = entry.get("risk",      "N/A")
            decision  = entry.get("decision",  "N/A")

            # Backward compatibility: path may live under old 'details' key
            path = entry.get("path")
            if path is None:
                details = entry.get("details", {})
                act     = details.get("action")
                if act in ("delete", "create"):
                    path = details.get("path", "N/A")
                elif act == "move":
                    src = details.get("source", "N/A")
                    dst = details.get("dest",   "N/A")
                    path = f"{src} -> {dst}"
                else:
                    path = "N/A"

            print(f"{idx}. [{timestamp}] | Cmd: {command} | Agent: {agent} | "
                  f"Action: {action} | Path: {path} | Risk: {risk} | Decision: {decision}")
        print()
