# ArmorIQ Supervisor — Project Documentation

> **Production-Level Autonomous Control Sandbox**  
> A policy-driven, risk-aware autonomous agent pipeline with a Streamlit Mission Control Dashboard.

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [Intent Model](#3-intent-model)
4. [Policy Model](#4-policy-model)
5. [Risk Intelligence Model](#5-risk-intelligence-model)
6. [Enforcement Mechanism](#6-enforcement-mechanism)
7. [Command Reference](#7-command-reference)
8. [Simulation Mode (Dry Run)](#8-simulation-mode-dry-run)
9. [Observability & History Logging](#9-observability--history-logging)
10. [Streamlit Dashboard](#10-streamlit-dashboard)
11. [Separation of Reasoning and Execution](#11-separation-of-reasoning-and-execution)
12. [Allowed vs Blocked Actions](#12-allowed-vs-blocked-actions)
13. [Running the Project](#13-running-the-project)
14. [File Reference](#14-file-reference)

---

## 1. Project Overview

ArmorIQ is an autonomous control sandbox that simulates how a production AI agent system safely manages file operations. Every command a user issues goes through a structured multi-stage security pipeline before any file is touched. The system is designed to demonstrate:

- **Intent translation** from natural language to structured actions
- **Policy enforcement** based on pre-configured agent permissions
- **Risk assessment** with structured classification (LOW / MEDIUM / HIGH)
- **Decision making** that combines policy and risk into a final verdict
- **Sandboxed execution** that is strictly confined to the `workspace/` directory
- **Full audit trail** logged to `history.json` and displayed live in the dashboard

---

## 2. Architecture

```
User Input
    │
    ▼
┌─────────────────────────────────────────────────────┐
│                     SUPERVISOR                      │
│                                                     │
│  [1] Planner          → Parse intent into actions   │
│  [2] DelegationMgr    → Fetch agent scope token     │
│  [3] Policy Engine    → Validate agent permissions  │
│  [4] Risk Engine      → Classify risk level         │
│  [5] Decision Engine  → Combine policy + risk       │
│  [6] Executor         → Execute (if ALLOWED)        │
│  [7] History Manager  → Persist audit log           │
└─────────────────────────────────────────────────────┘
```

Each stage is implemented as a separate, independently testable Python class. The Supervisor is the only orchestrator — no stage calls another stage directly.

---

## 3. Intent Model

**File:** `planner.py`

The Planner translates raw natural language user input into a deterministic list of **action dictionaries**. Each dictionary contains:

| Field    | Description                                       |
|----------|---------------------------------------------------|
| `agent`  | The agent responsible (e.g., `CleanerAgent`)      |
| `action` | The action type (`delete`, `create`, `move`, `read`) |
| `path`   | Target path (for delete, create, read)            |
| `source` | Source path (for move only)                       |
| `dest`   | Destination path (for move only)                  |

The Planner has no knowledge of permissions, risk, or execution. It purely maps intent to structure.

---

## 4. Policy Model

**Files:** `policies.json`, `delegation.py`, `policy_engine.py`

Policies are defined in `policies.json`. Each agent has:
- **`allowed_actions`**: list of permitted operation types
- **`allowed_paths`**: list of directory scopes it is allowed to operate in

### Registered Agents

| Agent          | Allowed Actions        | Allowed Paths    |
|----------------|------------------------|------------------|
| CleanerAgent   | `delete`               | `workspace/temp` |
| OrganizerAgent | `create`, `move`       | `workspace`      |
| MonitorAgent   | `read`                 | `workspace`      |

**`DelegationManager`** issues a "Scope Token" for a given agent from the policy store.  
**`PolicyEngine`** validates a proposed action against the agent's token, rejecting anything out of scope.

---

## 5. Risk Intelligence Model

**File:** `risk_engine.py`

The Risk Engine independently classifies every action before policy is checked.

| Risk Level | Triggers                                                        | Example                              |
|------------|-----------------------------------------------------------------|--------------------------------------|
| **LOW**    | Read-only operations inside sandbox                             | `check workspace status`             |
| **MEDIUM** | Any file `delete`, `create`, or `move` inside `workspace/`     | `clean workspace`, `archive logs`    |
| **HIGH**   | Any path outside `workspace/`, any access to `system/` directory | `delete system config`, `access system folder` |

Risk is assessed **before** policy checking so that even an unknown or unpermissioned agent gets its operation classified before being blocked.

---

## 6. Enforcement Mechanism

**File:** `supervisor.py`

The Supervisor runs the following steps in strict order for each action:

1. **Risk Assessment** — risk level assigned regardless of agent validity
2. **Delegation** — scope token fetched; action blocked immediately if agent unknown
3. **Policy Check** — action validated against agent's allowed actions and paths
4. **Decision** — Decision Engine combines policy result + risk level:
   - Any policy violation → `BLOCKED`
   - Risk level `HIGH` → `BLOCKED`
   - Risk level `MEDIUM` or `LOW` with valid policy → `ALLOWED`
5. **Execution** — Executor called only if decision is `ALLOWED` (and simulation mode is OFF)
6. **Logging** — every action logged to `history.json` regardless of decision

---

## 7. Command Reference

### Operations
| Command | Agent | Action | Description |
|---------|-------|--------|-------------|
| `clean workspace` | CleanerAgent | `delete` | Deletes all files inside `workspace/temp` |
| `organize files` | OrganizerAgent | `move` | Moves `workspace/log.txt` to `workspace/logs/` |
| `clean and organize workspace` | Both | `delete` + `move` | Combined clean and organize |
| `archive logs` | OrganizerAgent | `move` | Moves `workspace/logs/` to `workspace/archive/logs_<timestamp>` |
| `create test file` | OrganizerAgent | `create` | Creates `workspace/test.txt` |

### Monitoring
| Command | Agent | Action | Description |
|---------|-------|--------|-------------|
| `check workspace status` | MonitorAgent | `read` | Reports total files, temp files, and total size |
| `preview clean workspace` | MonitorAgent | `read` | Lists files that _would_ be deleted — no changes applied |
| `show history` | — | — | Prints full execution history to console |

### Security Tests
| Command | Agent | Action | Outcome |
|---------|-------|--------|---------|
| `delete system config` | CleanerAgent | `delete` | Always **BLOCKED** — path outside CleanerAgent scope |
| `access system folder` | MonitorAgent | `read` | Always **BLOCKED** — `system/` is HIGH risk, outside MonitorAgent scope |

---

## 8. Simulation Mode (Dry Run)

Activated via the toggle in the Streamlit sidebar.

When **ON**:
- The full pipeline runs — Planner, Delegation, PolicyEngine, RiskEngine, DecisionEngine
- The **Executor is skipped entirely**
- Output displays: `"Simulation Mode: No changes applied"`
- All decisions and reasoning are still logged to history

This allows safe demonstration and testing of the pipeline logic without any filesystem side effects.

---

## 9. Observability & History Logging

**File:** `history_manager.py` → `history.json`

Every processed action is stored with the following fields:

| Field      | Description                                    |
|------------|------------------------------------------------|
| `timestamp`| ISO 8601 datetime of when the action ran       |
| `command`  | The original user input string                 |
| `agent`    | Agent that processed the action                |
| `action`   | Operation type (`delete`, `create`, `move`, `read`) |
| `path`     | Target path or `source → dest` for moves       |
| `risk`     | Risk classification (`LOW` / `MEDIUM` / `HIGH`)|
| `decision` | Final verdict (`ALLOWED` / `BLOCKED`)          |
| `reason`   | Human-readable combined rationale              |

The Streamlit dashboard streams this file into a live sortable table.

---

## 10. Streamlit Dashboard

**File:** `app.py`  
**Boot:** `streamlit run app.py`  
**Cloud:** `armoriq-supervisor.streamlit.app`

### Layout

| Section | Description |
|---------|-------------|
| **Sidebar** | Categorized command selector (Operations / Monitoring / Security Tests), manual text input, Simulation Mode toggle |
| **Metric Cards** | Real-time: Steps Processed, Allowed, Blocked, Warnings |
| **Pipeline Visualization** | Animated stage-by-stage flowchart — Executor turns green (ALLOWED) or red (BLOCKED) |
| **Risk Badge** | Animated badge showing last risk level and decision |
| **Console Output** | Terminal-style box with full pipeline print output |
| **Decision Detail** | Per-step cards with risk badge, decision badge, explanation bullets, execution output |
| **Execution Timeline** | Live table from `history.json` — newest records first |

---

## 11. Separation of Reasoning and Execution

The system strictly separates two layers:

**Reasoning Layer** _(abstract — no filesystem access)_:
- `Planner` → `DelegationManager` → `PolicyEngine` → `RiskEngine` → `DecisionEngine`

These classes only process Python dictionaries and strings. They perform zero file I/O.

**Execution Layer** _(sandboxed — no knowledge of policies or risk)_:
- `Executor` — the only class that calls `os` / `shutil`
- All paths are resolved to absolute and validated against `SANDBOX_ROOT` before any operation
- Raises `ValueError` if a path attempts to escape the sandbox

This means:
- A bug in the reasoning layer **cannot** modify the filesystem
- The executor **cannot** be coerced into leaving the sandbox via logic tricks

---

## 12. Allowed vs Blocked Actions

### Example: ALLOWED
**Command:** `clean workspace`
- **Planner:** → `CleanerAgent`, `delete`, `workspace/temp`
- **Risk:** MEDIUM — destructive delete inside workspace
- **Policy:** CleanerAgent is explicitly allowed to `delete` in `workspace/temp` ✅
- **Decision:** ALLOWED — policy passes, risk not HIGH
- **Execution:** Files under `workspace/temp/` deleted

### Example: BLOCKED (Policy Violation)
**Command:** `delete system config`
- **Planner:** → `CleanerAgent`, `delete`, `system/config`
- **Risk:** HIGH — `system/` path detected
- **Policy:** `system/config` is outside CleanerAgent's allowed paths (`workspace/temp`) ❌
- **Decision:** BLOCKED — both policy and risk fail
- **Execution:** Executor never called

### Example: BLOCKED (Risk)
**Command:** `access system folder`
- **Planner:** → `MonitorAgent`, `read`, `system/`
- **Risk:** HIGH — `system/` access detected
- **Policy:** `system/` outside MonitorAgent scope (`workspace`) ❌
- **Decision:** BLOCKED
- **Execution:** Executor never called

---

## 13. Running the Project

### Local Terminal Mode
```bash
python main.py
```

### Web Dashboard (Local)
```bash
streamlit run app.py
# Open: http://localhost:8501
```

### Web Dashboard (Cloud)
Deployed at: `https://armoriq-supervisor.streamlit.app`

### Dependencies
```
streamlit
pandas
```
Install: `pip install streamlit pandas`

---

## 14. File Reference

| File | Role |
|------|------|
| `main.py` | CLI entry point; sets up sandbox and starts REPL |
| `planner.py` | Translates user input into structured action list |
| `delegation.py` | Loads `policies.json`; issues scope tokens per agent |
| `policy_engine.py` | Validates actions against agent scope tokens |
| `risk_engine.py` | Classifies actions as LOW / MEDIUM / HIGH risk |
| `decision_engine.py` | Combines policy + risk into final ALLOWED/BLOCKED verdict |
| `executor.py` | Sandboxed file operations (`delete`, `create`, `move`, `read`) |
| `logger.py` | Writes structured logs to `logs.txt` |
| `history_manager.py` | Persists audit trail to `history.json` |
| `supervisor.py` | Orchestrates the full pipeline; supports simulation mode |
| `app.py` | Streamlit web dashboard |
| `policies.json` | Agent permission config |
| `history.json` | Persistent audit log (auto-generated) |
| `logs.txt` | Session logs (auto-generated) |
| `workspace/` | Sandboxed working directory |
| `system/` | Simulated protected system directory (always blocked) |
| `.streamlit/config.toml` | Disables Streamlit telemetry |
| `requirements.txt` | Python dependencies for Streamlit Cloud |
