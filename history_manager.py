"""
History Manager: stores and retrieves decision history in history.json.
Now stores explicit path field.
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
            except:
                return []
        return []

    def _save(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)

    def add_entry(self, agent: str, action_type: str, path: str, risk: str, decision: str, reason: str):
        """Add a history entry with all relevant fields."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "action": action_type,
            "path": path,
            "risk": risk,
            "decision": decision,
            "reason": reason
        }
        self.history.append(entry)
        self._save()

    def show_history(self):
        """Print history to console safely using get() for backward compatibility."""
        if not self.history:
            print("No history available.")
            return
        print("\n--- Execution History ---")
        for idx, entry in enumerate(self.history, 1):
            timestamp = entry.get("timestamp", "N/A")
            agent = entry.get("agent", "N/A")
            action = entry.get("action", "N/A")
            
            # For backward compatibility, check if path exists directly vs inside details
            path = entry.get("path")
            if path is None:
                # Fall back to checking old "details" structure
                details = entry.get("details", {})
                act_type = details.get("action")
                if act_type in ("delete", "create"):
                    path = details.get("path", "N/A")
                elif act_type == "move":
                    src = details.get("source", "N/A")
                    dst = details.get("dest", "N/A")
                    path = f"{src} -> {dst}"
                else:
                    path = "N/A"

            risk = entry.get("risk", "N/A")
            decision = entry.get("decision", "N/A")
            
            print(f"{idx}. [{timestamp}] | Agent: {agent} | Action: {action} | "
                  f"Path: {path} | Risk: {risk} | Decision: {decision}")
        print()
