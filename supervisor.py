"""
Supervisor: coordinates Plan–Delegate–Validate–Execute pipeline.
Maintains statistics and prints execution summary.
"""

from planner import Planner
from delegation import DelegationManager
from policy_engine import PolicyEngine
from risk_engine import RiskEngine
from decision_engine import DecisionEngine
from executor import Executor
from logger import Logger
from history_manager import HistoryManager

class Supervisor:
    def __init__(self):
        self.planner = Planner()
        self.delegation = DelegationManager()
        self.policy_engine = PolicyEngine()
        self.risk_engine = RiskEngine()
        self.decision_engine = DecisionEngine()
        self.executor = Executor()
        self.logger = Logger()
        self.history = HistoryManager()
        # Statistics counters
        self.total_steps = 0
        self.allowed_count = 0
        self.blocked_count = 0
        self.warning_count = 0

    def process(self, user_input: str):
        """Process a command."""
        if user_input.lower() == "show history":
            self.history.show_history()
            return

        actions = self.planner.parse(user_input)
        if not actions:
            self.logger.info(f"No actions parsed from: {user_input}")
            return

        # Reset counters for this command
        self.total_steps = 0
        self.allowed_count = 0
        self.blocked_count = 0
        self.warning_count = 0

        # --- Plan Preview ---
        print("\n--- Planned Actions ---")
        for i, act in enumerate(actions, 1):
            agent = act["agent"]
            act_type = act["action"]
            if act_type in ("delete", "create"):
                print(f"{i}. {agent} → {act_type} {act['path']}")
            elif act_type == "move":
                print(f"{i}. {agent} → move {act['source']} → {act['dest']}")
        print()

        # --- Step-by-step execution with risk first ---
        for action in actions:
            self.total_steps += 1
            agent_name = action["agent"]

            # 1. Risk assessment (always performed, even if agent unknown)
            risk_level, risk_reason = self.risk_engine.assess(action)
            if risk_level == "MEDIUM":
                self.warning_count += 1

            # 2. Delegation: get scope token
            scope_token = self.delegation.get_scope_token(agent_name)
            if not scope_token:
                decision = "BLOCKED"
                final_reason = "Agent unknown"
                explanation = [f"Agent '{agent_name}' not found in policies"]
                self.blocked_count += 1
                self._print_decision_block(agent_name, action, risk_level, decision, explanation)
                self.logger.decision_log(agent_name, action, risk_level, decision, final_reason)
                self._add_history(agent_name, action, risk_level, decision, final_reason)
                continue

            # 3. Policy check
            policy_allowed, policy_reason = self.policy_engine.validate(action, scope_token)

            # 4. Decision (combines policy and risk)
            decision, final_reason, explanation = self.decision_engine.decide(
                policy_allowed, policy_reason, risk_level, risk_reason
            )

            # Update counters
            if decision == "ALLOWED":
                self.allowed_count += 1
            else:
                self.blocked_count += 1

            # 5. Display security decision block
            self._print_decision_block(agent_name, action, risk_level, decision, explanation)

            # 6. Log decision
            self.logger.decision_log(agent_name, action, risk_level, decision, final_reason)
            self._add_history(agent_name, action, risk_level, decision, final_reason)

            # 7. Execute if allowed
            if decision == "ALLOWED":
                success, msg = self.executor.execute(action)
                if success:
                    self.logger.info(f"Execution success: {msg}")
                else:
                    if "file not found" in msg.lower():
                        self.logger.info(f"Execution skipped: {msg}")
                    else:
                        self.logger.error(f"Execution failed: {msg}")

        # --- Execution Summary ---
        self._print_summary()

    def _print_decision_block(self, agent: str, action: dict, risk: str, decision: str, explanation_lines: list):
        """Print the security decision block with bullet points."""
        print("--- SECURITY DECISION ---")
        print(f"Agent: {agent}")
        print(f"Action: {action['action']}")
        if "path" in action:
            print(f"Path: {action['path']}")
        if "source" in action and "dest" in action:
            print(f"Source: {action['source']} -> Destination: {action['dest']}")
        print(f"Risk: {risk}")
        print(f"Decision: {decision}")
        print("Reason:")
        for line in explanation_lines:
            print(f"• {line}")
        print("-----------------------------------------------")

    def _print_summary(self):
        """Print execution summary after processing all steps."""
        print("\nExecution Summary:")
        print(f"Total Steps: {self.total_steps}")
        print(f"Allowed: {self.allowed_count}")
        print(f"Blocked: {self.blocked_count}")
        print(f"Warnings (Medium Risk): {self.warning_count}")
        print()

    def _add_history(self, agent: str, action: dict, risk: str, decision: str, reason: str):
        """Helper to add history with proper path extraction."""
        # Determine path string for history
        act_type = action.get("action")
        if act_type in ("delete", "create") and "path" in action:
            path = action["path"]
        elif act_type == "move" and "source" in action and "dest" in action:
            path = f"{action['source']} -> {action['dest']}"
        else:
            path = action.get("path", "N/A")
            
        self.history.add_entry(agent, action.get("action", "unknown"), path, risk, decision, reason)
