"""
Logger: writes messages to console and to a log file.
"""

import logging
import sys

class Logger:
    def __init__(self, log_file="logs.txt"):
        self.logger = logging.getLogger("ArmorIQ")
        self.logger.setLevel(logging.INFO)
        self.logger.handlers.clear()

        # File handler
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.INFO)

        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def info(self, message: str):
        self.logger.info(message)

    def error(self, message: str):
        self.logger.error(message)

    def decision_log(self, agent: str, action: dict, risk: str, decision: str, reason: str):
        """Structured log for decisions."""
        action_type = action.get("action")
        if action_type in ("delete", "create"):
            path_str = action.get("path", "N/A")
        elif action_type == "move":
            path_str = f"src={action.get('source')}, dst={action.get('dest')}"
        else:
            path_str = "N/A"

        self.info(
            f"Agent: {agent} | Action: {action_type} | Path: {path_str} | "
            f"Risk: {risk} | Decision: {decision} | Reason: {reason}"
        )
