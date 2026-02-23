"""
Decision Engine: combines policy and risk to produce a final decision and explanation.
"""

class DecisionEngine:
    @staticmethod
    def decide(policy_allowed: bool, policy_reason: str,
               risk_level: str, risk_reason: str) -> tuple[str, str, list[str]]:
        """
        Returns (decision, final_reason, explanation_lines).
        decision: 'ALLOWED' or 'BLOCKED'
        final_reason: short summary
        explanation_lines: list of strings for detailed output
        """
        explanation = []
        if not policy_allowed:
            decision = "BLOCKED"
            final_reason = f"Policy violation: {policy_reason}"
            explanation.append(f"Policy check failed: {policy_reason}")
        elif risk_level == "HIGH":
            decision = "BLOCKED"
            final_reason = f"High risk: {risk_reason}"
            explanation.append(f"Risk assessment: {risk_reason} (HIGH)")
        else:
            decision = "ALLOWED"
            final_reason = f"Policy allowed, risk {risk_level}"
            explanation.append(f"Policy check passed")
            explanation.append(f"Risk level: {risk_level} – {risk_reason}")
            if risk_level == "MEDIUM":
                explanation.append("WARNING: Medium-risk operation permitted")
        return decision, final_reason, explanation
