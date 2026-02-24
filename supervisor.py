"""
Supervisor: coordinates Plan–Delegate–Validate–Execute pipeline.
Now supports Simulation Mode (dry run) that skips the Executor.
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
        self.planner        = Planner()
        self.delegation     = DelegationManager()
        self.policy_engine  = PolicyEngine()
        self.risk_engine    = RiskEngine()
        self.decision_engine = DecisionEngine()
        self.executor       = Executor()
        self.logger         = Logger()
        self.history        = HistoryManager()
        # Session counters
        self.total_steps   = 0
        self.allowed_count = 0
        self.blocked_count = 0
        self.warning_count = 0

    def process(self, user_input: str, simulation_mode: bool = False) -> list[dict]:
        """
        Process a command through the full pipeline.
        Returns a list of result dicts (one per action) for the UI to consume.
        simulation_mode=True runs all reasoning but skips Executor.
        """
        results = []

        if user_input.lower() == "show history":
            self.history.show_history()
            return results

        actions = self.planner.parse(user_input)
        if not actions:
            self.logger.info(f"No actions parsed from: '{user_input}'")
            return results

        # Reset per-command counters
        self.total_steps   = 0
        self.allowed_count = 0
        self.blocked_count = 0
        self.warning_count = 0

        # Plan preview
        print("\n--- Planned Actions ---")
        for i, act in enumerate(actions, 1):
            agent    = act["agent"]
            act_type = act["action"]
            if act_type in ("delete", "create", "read"):
                print(f"{i}. {agent} → {act_type} {act.get('path','')}")
            elif act_type == "move":
                print(f"{i}. {agent} → move {act.get('source','')} → {act.get('dest','')}")
        print()

        for action in actions:
            self.total_steps += 1
            agent_name = action["agent"]

            # 1. Risk assessment (always first)
            risk_level, risk_reason = self.risk_engine.assess(action)
            if risk_level == "MEDIUM":
                self.warning_count += 1

            # 2. Delegation scope token
            scope_token = self.delegation.get_scope_token(agent_name)
            if not scope_token:
                decision     = "BLOCKED"
                final_reason = f"Agent '{agent_name}' not found in policies"
                explanation  = [final_reason]
                self.blocked_count += 1
                self._log_and_store(user_input, agent_name, action, risk_level, decision, final_reason)
                results.append(self._build_result(agent_name, action, risk_level, decision, explanation, simulation_mode))
                continue

            # 3. Policy check
            policy_allowed, policy_reason = self.policy_engine.validate(action, scope_token)

            # 4. Decision
            decision, final_reason, explanation = self.decision_engine.decide(
                policy_allowed, policy_reason, risk_level, risk_reason
            )

            if decision == "ALLOWED":
                self.allowed_count += 1
            else:
                self.blocked_count += 1

            self._print_decision_block(agent_name, action, risk_level, decision, explanation)
            self._log_and_store(user_input, agent_name, action, risk_level, decision, final_reason)

            exec_output = ""
            # 5. Execute (only if ALLOWED and NOT in simulation mode)
            if decision == "ALLOWED":
                if simulation_mode:
                    exec_output = "Simulation Mode: No changes applied"
                    self.logger.info(f"[SIMULATION] Would execute: {action['action']} on {action.get('path','')}")
                else:
                    success, msg = self.executor.execute(action)
                    exec_output = msg
                    if success:
                        self.logger.info(f"Execution success: {msg}")
                    else:
                        if "file not found" in msg.lower():
                            self.logger.info(f"Execution skipped: {msg}")
                        else:
                            self.logger.error(f"Execution failed: {msg}")

            results.append(self._build_result(
                agent_name, action, risk_level, decision, explanation, simulation_mode, exec_output
            ))

        self._print_summary()
        return results

    def _build_result(self, agent, action, risk, decision, explanation, simulation_mode, exec_output=""):
        act_type = action.get("action", "")
        if act_type in ("delete", "create", "read"):
            path_str = action.get("path", "N/A")
        elif act_type == "move":
            path_str = f"{action.get('source', '')} → {action.get('dest', '')}"
        else:
            path_str = "N/A"

        return {
            "agent":       agent,
            "action":      act_type,
            "path":        path_str,
            "risk":        risk,
            "decision":    decision,
            "explanation": explanation,
            "simulation":  simulation_mode,
            "exec_output": exec_output,
        }

    def _log_and_store(self, command, agent, action, risk, decision, reason):
        self.logger.decision_log(agent, action, risk, decision, reason)
        self._add_history(command, agent, action, risk, decision, reason)

    def _add_history(self, command, agent, action, risk, decision, reason):
        act_type = action.get("action", "unknown")
        if act_type in ("delete", "create", "read") and "path" in action:
            path = action["path"]
        elif act_type == "move" and "source" in action and "dest" in action:
            path = f"{action['source']} -> {action['dest']}"
        else:
            path = action.get("path", "N/A")
        self.history.add_entry(command, agent, act_type, path, risk, decision, reason)

    def _print_decision_block(self, agent, action, risk, decision, explanation_lines):
        print("--- SECURITY DECISION ---")
        print(f"Agent: {agent}")
        print(f"Action: {action['action']}")
        if "path" in action:
            print(f"Path: {action['path']}")
        if "source" in action and "dest" in action:
            print(f"Source: {action['source']} -> Dest: {action['dest']}")
        print(f"Risk: {risk}")
        print(f"Decision: {decision}")
        print("Reason:")
        for line in explanation_lines:
            print(f"  • {line}")
        print("----------------------------------------------")

    def _print_summary(self):
        print("\nExecution Summary:")
        print(f"  Total Steps : {self.total_steps}")
        print(f"  Allowed     : {self.allowed_count}")
        print(f"  Blocked     : {self.blocked_count}")
        print(f"  Warnings    : {self.warning_count}")
        print()
