# ArmorIQ: Production-Level Autonomous Control Documentation 

## 1. Intent Model
The Intent Model in ArmorIQ is responsible for translating human-readable requests into structured, actionable commands. When a user provides a natural language input (e.g., `"clean and organize workspace"`), the **Planner** (`planner.py`) acts as the intent translator. It maps ambiguous inputs into a deterministic list of concrete actions, mapping each step to a specific agent (e.g., `CleanerAgent`, `OrganizerAgent`), an operation type (`delete`, `move`), and explicitly defining the target paths based on the context of the user's intent.

## 2. Policy Model
The Policy Model governs "who can do what and where." It is driven by an external configuration (`policies.json`) and enforced by the **Policy Engine** (`policy_engine.py`) alongside the **Delegation Manager** (`delegation.py`). 
* The **Delegation Manager** issues a "Scope Token" containing an agent's configured permissions upon request. 
* The **Policy Engine** validates the proposed intent against this token, ensuring that the agent is explicitly authorized for the action type (e.g., `delete`) and that the target path falls within their permitted directories. If an un-scoped action is attempted, the policy engine rejects the request.

## 3. Enforcement Mechanism
The Enforcement Mechanism is a multi-layered security and execution pipeline overseen by the **Supervisor** (`supervisor.py`). The pipeline operates in a strict sequence:
1. **Risk Assessment**: The **Risk Engine** (`risk_engine.py`) preemptively evaluates the action's target path. Paths outside the designated `workspace/` sandbox or involving the `system/` directory are immediately flagged as **HIGH** risk.
2. **Policy Checking**: The intent is verified against the agent's Scope Token.
3. **Decision Making**: The **Decision Engine** (`decision_engine.py`) merges the Risk and Policy models. Any policy violation or HIGH-risk flag results in a hard `BLOCKED` decision. Only operations that pass policy checks and are LOW or MEDIUM risk are `ALLOWED`.
4. **Sandboxed Execution**: If allowed, the **Executor** (`executor.py`) performs a final sanity check, strictly resolving paths to ensure they physically reside within `SANDBOX_ROOT`. It then safely executes the file system operation. 
5. **Audit Logging**: Every event is captured by the **History Manager** and **Logger** to trace the exact reasoning behind the enforcement mechanisms.

## 4. Explanation of an Allowed Action
**Scenario:** The user requests `"clean workspace"`.
* **Intent**: Planner maps this to `CleanerAgent` executing a `delete` on `workspace/temp`.
* **Risk**: The Risk Engine flags this as **MEDIUM** risk because it involves deleting files, but it recognizes the path is safely inside the `workspace/` boundary.
* **Policy**: The Delegation Manager confirms `CleanerAgent` is allowed to `delete` inside `workspace/temp`.
* **Decision**: Because the policy passes and the risk is not HIGH, the Decision Engine returns **ALLOWED** with the reason: `Policy allowed, risk MEDIUM`.
* **Execution**: The Executor successfully resolves `workspace/temp` to the local sandbox root and deletes the content.

## 5. Explanation of a Blocked Action
**Scenario:** The user requests `"delete system config"`.
* **Intent**: Planner maps this to `CleanerAgent` attempting a `delete` on `system/config`.
* **Risk**: The Risk Engine identifies the `system/` directory path and immediately flags the action as **HIGH** risk.
* **Policy**: The Policy Engine checks `CleanerAgent`'s token and sees it is only allowed in `workspace/temp`. It flags a policy violation.
* **Decision**: The Decision Engine sees both a policy failure and a HIGH risk flag. It strictly enforces a **BLOCKED** decision, refusing the execution and generating a comprehensive reason explaining the scope violation and the risk assessment.
* **Execution**: The action is blocked at the Supervisor level; the Executor is never even invoked.

## 6. Separation Between Reasoning and Execution
ArmorIQ strictly delineates "thinking" from "doing." The reasoning pipeline—comprising the Planner (Intent), Policy Engine, Risk Engine, and Decision Engine—operates entirely in the abstract layer. It evaluates dictionaries of proposed actions, scopes, and string paths without ever touching the file system. 

Execution logic relies completely on the **Executor** class. The Executor is entirely unaware of policies, risks, or agents; its sole responsibility is to take a validated command, strictly confine it to the physical `SANDBOX_ROOT`, run Python `os` and `shutil` commands, and safely handle missing file exceptions. 

This separation isolates potential vulnerabilities: a logic bug in the reasoning engines cannot directly modify the filesystem, and the executor cannot be easily tricked into breaking out of the sandbox directory by prompt injection, creating a highly resilient and secure architecture.
