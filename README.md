# ArmorIQ Supervisor

**Intent-Aware Autonomous Execution with Bounded Delegation**

Built for **Claw&Shield 2026 – IIT Delhi**
Track: **ArmorIQ – Safe Autonomous AI Systems**

---

## Overview

ArmorIQ Supervisor is a secure autonomous control framework that enables AI agents to perform real system actions while enforcing strict safety boundaries.

The system demonstrates how autonomous agents can operate independently **without losing user control** by validating intent, enforcing policies, and blocking unsafe operations at runtime.

**Core Principle**

> Autonomous reasoning must never directly trigger system execution without passing through validation and safety enforcement layers.

---

## Key Features

* Multi-Agent Architecture

  * CleanerAgent
  * OrganizerAgent

* Plan–Delegate–Validate–Execute Pipeline

* Bounded Delegation
  Each agent operates within a restricted scope and permission set.

* Policy-Based Enforcement
  Actions are validated against predefined agent permissions.

* Risk Classification

  * LOW – Safe operations
  * MEDIUM – Allowed with warning
  * HIGH – Blocked

* Deterministic Blocking
  Unauthorized or high-risk actions are prevented before execution.

* Execution Sandbox
  All operations are restricted to a controlled `workspace/` directory.

* Audit & Traceability
  Every action is logged with timestamp, risk level, and decision.

---

## System Architecture

```
User Input
    ↓
Planner
    ↓
Supervisor
    ↓
Delegation Manager
    ↓
Policy Engine
    ↓
Risk Engine
    ↓
Decision Engine (Allow / Block)
    ↓
Execution Sandbox (workspace/)
    ↓
Audit Logger & History
```

This ensures clear separation between **reasoning** and **execution**.

---

## Project Structure

```
armoriq/
│
├── main.py
├── planner.py
├── supervisor.py
├── policy_engine.py
├── risk_engine.py
├── policies.json
│
├── workspace/
│   └── temp/
├── system/
│
├── README.md
├── LICENSE
├── requirements.txt
└── .gitignore
```

---

## Running the Project

**Requirements:** Python 3.8+

Run the system:

```
python main.py
```

---

## Supported Commands

```
clean workspace
organize files
clean and organize workspace
delete system config
show history
```

---

## Example Scenarios

### Allowed Operation

```
Input: clean workspace
Risk: MEDIUM
Decision: ALLOWED
Execution: Files cleaned inside workspace/temp
```

### Blocked Operation

```
Input: delete system config
Risk: HIGH
Decision: BLOCKED
Reason: Outside allowed scope / High-risk path
```

---

## Execution Summary

After each command, the system reports:

* Total steps
* Allowed actions
* Blocked actions
* Medium-risk warnings

---

## Audit Logging

Each action record contains:

* Timestamp
* Agent
* Action
* Path
* Risk level
* Decision

View history:

```
show history
```

---

## Safety Design Principles

* Plan–Validate–Execute separation
* Bounded agent authority
* Runtime policy enforcement
* Risk-aware execution control
* Sandboxed system interaction
* Full decision transparency

---

## Hackathon Details

**Event:** Claw&Shield 2026
**Organizer:** Indian Institute of Technology (IIT) Delhi
**Theme:** Trustworthy Autonomous AI Systems

---

## License

MIT License
