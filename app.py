"""
ArmorIQ — Production-Level Autonomous Control Dashboard
Streamlit UI: dark theme, categorized sidebar, simulation mode,
risk badges, pipeline visualization, execution timeline.
"""

import streamlit as st
import json
import os
import io
import sys
import time

from supervisor import Supervisor

# ─────────────────────────────────────────────────────────────
# Page Config (MUST be first Streamlit call)
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ArmorIQ Mission Control",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# CSS — Dark Premium Theme
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global ─────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0d1117;
    color: #e6edf3;
    font-family: 'Segoe UI', sans-serif;
}
[data-testid="stSidebar"] {
    background-color: #161b22;
    border-right: 1px solid #30363d;
}
[data-testid="stSidebar"] * { color: #e6edf3 !important; }

/* ── Metric Cards ─────────────────────────────────────────── */
.metric-card {
    background: linear-gradient(145deg, #161b22, #1c2230);
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 18px 22px;
    text-align: center;
    margin-bottom: 12px;
    transition: transform .2s;
}
.metric-card:hover { transform: translateY(-3px); }
.metric-value { font-size: 36px; font-weight: 700; }
.metric-label { font-size: 12px; color: #8b949e; letter-spacing: 1.5px; text-transform: uppercase; margin-top: 4px; }
.metric-allowed .metric-value { color: #3fb950; }
.metric-blocked .metric-value { color: #f85149; }
.metric-total   .metric-value { color: #58a6ff; }

/* ── Console Box ──────────────────────────────────────────── */
.console-box {
    background: #010409;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 16px;
    font-family: 'Courier New', monospace;
    font-size: 13px;
    color: #3fb950;
    white-space: pre-wrap;
    max-height: 420px;
    overflow-y: auto;
}
.console-placeholder {
    background: #161b22;
    border: 1px dashed #30363d;
    border-radius: 8px;
    padding: 24px;
    text-align: center;
    color: #484f58;
    font-size: 14px;
}

/* ── Risk Badges ──────────────────────────────────────────── */
.badge {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    animation: pulse 2s infinite;
}
.badge-LOW    { background: #0d4429; color: #3fb950; border: 1px solid #238636; }
.badge-MEDIUM { background: #3d2300; color: #e3b341; border: 1px solid #9e6a03; }
.badge-HIGH   { background: #3d0b0b; color: #f85149; border: 1px solid #b22222; }
.badge-BLOCKED { background: #3d0b0b; color: #f85149; border: 1px solid #b22222; }
.badge-ALLOWED { background: #0d4429; color: #3fb950; border: 1px solid #238636; }

@keyframes pulse {
    0%,100% { opacity:1; }
    50%      { opacity:.7; }
}

/* ── Pipeline ─────────────────────────────────────────────── */
.pipeline {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
    padding: 16px;
    background: #161b22;
    border-radius: 10px;
    border: 1px solid #30363d;
    margin: 12px 0;
}
.pipeline-node {
    background: linear-gradient(135deg, #1f6feb, #388bfd);
    color: #fff;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    white-space: nowrap;
    animation: fadeIn .4s ease;
}
.pipeline-node.active  { background: linear-gradient(135deg, #238636, #3fb950); }
.pipeline-node.blocked { background: linear-gradient(135deg, #b22222, #f85149); }
.pipeline-arrow { color: #30363d; font-size: 18px; }

@keyframes fadeIn { from { opacity:0; transform: scale(.9); } to { opacity:1; transform: scale(1); } }

/* ── Section Headers ─────────────────────────────────────── */
.section-header {
    color: #58a6ff;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    border-bottom: 1px solid #21262d;
    padding-bottom: 6px;
    margin: 18px 0 12px;
}

/* ── Simulation Banner ────────────────────────────────────── */
.sim-banner {
    background: #1a1e2e;
    border: 1px solid #58a6ff;
    border-radius: 8px;
    padding: 10px 18px;
    color: #58a6ff;
    font-size: 13px;
    font-weight: 600;
    text-align: center;
    margin-bottom: 14px;
    animation: pulse 2s infinite;
}

/* ── Dataframe overrides ─────────────────────────────────── */
[data-testid="stDataFrame"] { border: 1px solid #30363d; border-radius: 8px; }

/* ── Button ──────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #238636, #2ea043) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100% !important;
    padding: 10px !important;
    transition: all .2s !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2ea043, #3fb950) !important;
    transform: translateY(-1px);
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# Sandbox Setup
# ─────────────────────────────────────────────────────────────
def setup_sandbox():
    os.makedirs("workspace/temp",    exist_ok=True)
    os.makedirs("workspace/logs",    exist_ok=True)
    os.makedirs("workspace/archive", exist_ok=True)
    os.makedirs("system",            exist_ok=True)
    if not os.path.exists("workspace/temp/file.tmp"):
        with open("workspace/temp/file.tmp", 'w') as f:
            f.write("Temporary file.\n")
    if not os.path.exists("workspace/log.txt"):
        with open("workspace/log.txt", 'w') as f:
            f.write("Log file.\n")
    if not os.path.exists("system/config"):
        with open("system/config", 'w') as f:
            f.write("[mock system config]\n")


# ─────────────────────────────────────────────────────────────
# Session State Init
# ─────────────────────────────────────────────────────────────
if 'supervisor' not in st.session_state:
    setup_sandbox()
    st.session_state.supervisor  = Supervisor()

if 'results'         not in st.session_state: st.session_state.results         = []
if 'cmd_history'     not in st.session_state: st.session_state.cmd_history     = []
if 'last_risk'       not in st.session_state: st.session_state.last_risk       = None
if 'last_decision'   not in st.session_state: st.session_state.last_decision   = None
if 'console_output'  not in st.session_state: st.session_state.console_output  = ""

sup = st.session_state.supervisor

# ─────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛡️ ArmorIQ")
    st.markdown("**Production Autonomous Control**")
    st.markdown("---")

    # Simulation Mode
    sim_mode = st.toggle("⚡ Simulation Mode (Dry Run)", value=False)
    if sim_mode:
        st.markdown('<div class="sim-banner">🔵 SIMULATION — No files will be modified</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Operations</div>', unsafe_allow_html=True)
    ops_commands = [
        "clean workspace",
        "organize files",
        "clean and organize workspace",
        "archive logs",
        "create test file",
    ]
    op_choice = st.selectbox("Select Operation", ["— pick —"] + ops_commands, key="ops")

    st.markdown('<div class="section-header">Monitoring</div>', unsafe_allow_html=True)
    mon_commands = ["check workspace status", "preview clean workspace", "show history"]
    mon_choice = st.selectbox("Select Monitor", ["— pick —"] + mon_commands, key="mon")

    st.markdown('<div class="section-header">Security Tests</div>', unsafe_allow_html=True)
    sec_commands = ["delete system config", "access system folder"]
    sec_choice = st.selectbox("Select Security Test", ["— pick —"] + sec_commands, key="sec")

    st.markdown("---")
    manual_input = st.text_input("✏️ Custom Command", placeholder="Type any command…")

    run_btn = st.button("🚀 Execute Command")


# ─────────────────────────────────────────────────────────────
# Resolve command to run
# ─────────────────────────────────────────────────────────────
cmd_to_run = ""
if run_btn:
    for choice in [manual_input, op_choice, mon_choice, sec_choice]:
        if choice and choice not in ("— pick —", ""):
            cmd_to_run = choice
            break

if cmd_to_run:
    st.session_state.cmd_history.append(cmd_to_run)

    old_stdout = sys.stdout
    sys.stdout = buf = io.StringIO()
    try:
        results = sup.process(cmd_to_run, simulation_mode=sim_mode)
    finally:
        sys.stdout = old_stdout

    st.session_state.console_output = buf.getvalue()
    st.session_state.results        = results

    if results:
        last = results[-1]
        st.session_state.last_risk     = last["risk"]
        st.session_state.last_decision = last["decision"]


# ─────────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────────
st.markdown("# 🛡️ ArmorIQ Mission Control")
st.markdown("**Production-Level Autonomous Control Sandbox** — Policy · Risk · Execution · History")

if sim_mode:
    st.markdown('<div class="sim-banner">⚡ SIMULATION MODE ACTIVE — Reasoner runs fully but Executor is bypassed</div>', unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────────────────────
# Row 1: Metrics
# ─────────────────────────────────────────────────────────────
col_t, col_a, col_b, col_w = st.columns(4)
with col_t:
    st.markdown(f"""<div class="metric-card metric-total">
        <div class="metric-value">{sup.total_steps}</div>
        <div class="metric-label">Steps Processed</div></div>""", unsafe_allow_html=True)
with col_a:
    st.markdown(f"""<div class="metric-card metric-allowed">
        <div class="metric-value">{sup.allowed_count}</div>
        <div class="metric-label">Allowed</div></div>""", unsafe_allow_html=True)
with col_b:
    st.markdown(f"""<div class="metric-card metric-blocked">
        <div class="metric-value">{sup.blocked_count}</div>
        <div class="metric-label">Blocked</div></div>""", unsafe_allow_html=True)
with col_w:
    st.markdown(f"""<div class="metric-card metric-total" style="border-color:#9e6a03">
        <div class="metric-value" style="color:#e3b341">{sup.warning_count}</div>
        <div class="metric-label">⚠ Warnings</div></div>""", unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────────────────────
# Row 2: Pipeline + Risk Badge (always visible, updates per run)
# ─────────────────────────────────────────────────────────────
last_risk     = st.session_state.last_risk
last_decision = st.session_state.last_decision

pipe_col, badge_col = st.columns([3, 1])
with pipe_col:
    st.markdown('<div class="section-header">Execution Pipeline</div>', unsafe_allow_html=True)
    exec_cls = "active" if last_decision == "ALLOWED" else ("blocked" if last_decision == "BLOCKED" else "")
    st.markdown(f"""
    <div class="pipeline">
        <div class="pipeline-node">👤 User</div>
        <span class="pipeline-arrow">▶</span>
        <div class="pipeline-node">📋 Planner</div>
        <span class="pipeline-arrow">▶</span>
        <div class="pipeline-node">🤝 Delegation</div>
        <span class="pipeline-arrow">▶</span>
        <div class="pipeline-node">📜 Policy</div>
        <span class="pipeline-arrow">▶</span>
        <div class="pipeline-node">⚠ Risk</div>
        <span class="pipeline-arrow">▶</span>
        <div class="pipeline-node">🧠 Decision</div>
        <span class="pipeline-arrow">▶</span>
        <div class="pipeline-node {exec_cls}">⚙ Executor</div>
    </div>
    """, unsafe_allow_html=True)

with badge_col:
    st.markdown('<div class="section-header">Last Risk Level</div>', unsafe_allow_html=True)
    if last_risk:
        st.markdown(f'<span class="badge badge-{last_risk}">{last_risk}</span>', unsafe_allow_html=True)
    if last_decision:
        st.markdown(f'<span class="badge badge-{last_decision}" style="margin-top:8px">{last_decision}</span>', unsafe_allow_html=True)
    if not last_risk:
        st.markdown('<span style="color:#484f58; font-size:13px">No command run yet</span>', unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────────────────────
# Row 3: Console Output + Per-step Decision Cards
# ─────────────────────────────────────────────────────────────
console_col, detail_col = st.columns([2, 1])

with console_col:
    st.markdown('<div class="section-header">Console Output</div>', unsafe_allow_html=True)
    output = st.session_state.console_output
    if output:
        st.markdown(f'<div class="console-box">{output}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="console-placeholder">🔒 Awaiting command — choose a command from the sidebar and hit Execute</div>', unsafe_allow_html=True)

with detail_col:
    st.markdown('<div class="section-header">Decision Detail</div>', unsafe_allow_html=True)
    results = st.session_state.results
    if results:
        for r in results:
            risk_cls = f"badge-{r['risk']}"
            dec_cls  = f"badge-{r['decision']}"
            sim_tag  = " 🔵 SIM" if r.get("simulation") else ""
            with st.container():
                st.markdown(f"""
                **Agent:** `{r['agent']}`  
                **Action:** `{r['action']}`  
                **Path:** `{r['path']}`  
                <span class="badge {risk_cls}">{r['risk']}</span>  
                <span class="badge {dec_cls}">{r['decision']}{sim_tag}</span>
                """, unsafe_allow_html=True)
                for line in r.get("explanation", []):
                    st.caption(f"• {line}")
                if r.get("exec_output"):
                    st.code(r["exec_output"], language=None)
                st.markdown("---")
    else:
        st.markdown('<span style="color:#484f58; font-size:13px">Run a command to see decision details here.</span>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Row 4: Execution Timeline
# ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="section-header">Live Execution Timeline</div>', unsafe_allow_html=True)

try:
    with open("history.json", "r") as f:
        history_data = json.load(f)

    if history_data:
        import pandas as pd
        df = pd.DataFrame(history_data[::-1])  # newest first
        # Normalize columns
        for col in ["timestamp", "command", "agent", "action", "path", "risk", "decision", "reason"]:
            if col not in df.columns:
                df[col] = "—"
        df = df[["timestamp", "command", "agent", "action", "path", "risk", "decision", "reason"]]
        df.columns = ["Timestamp", "Command", "Agent", "Action", "Path", "Risk", "Decision", "Reason"]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.markdown('<span style="color:#484f58; font-size:13px">No history records yet.</span>', unsafe_allow_html=True)
except Exception:
    st.markdown('<span style="color:#484f58; font-size:13px">History file not found — run a command to generate records.</span>', unsafe_allow_html=True)
