"""
Streamlit Web Architecture for ArmorIQ 
Provides a modern visual dashboard interacting with the Supervisor backend.
"""

import streamlit as st
import json
import streamlit as st
import json
import os
import io
import sys
from datetime import datetime

# Import backend classes
from supervisor import Supervisor

def setup_sandbox():
    """Create required directories and dummy files inside the sandbox."""
    os.makedirs("workspace/temp", exist_ok=True)
    os.makedirs("workspace/logs", exist_ok=True)
    os.makedirs("system", exist_ok=True)  # simulated protected area

    # Dummy files
    if not os.path.exists("workspace/temp/file.tmp"):
        with open("workspace/temp/file.tmp", 'w') as f:
            f.write("Temporary file content.\n")

    if not os.path.exists("workspace/log.txt"):
        with open("workspace/log.txt", 'w') as f:
            f.write("This is a log file.\n")

    # Create a dummy system file to demonstrate blocking (but not used by executor)
    if not os.path.exists("system/config"):
        with open("system/config", 'w') as f:
            f.write("[mock system config]\n")

# Configure page settings
st.set_page_config(
    page_title="ArmorIQ Mission Control", 
    page_icon="🛡️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a clean, professional aesthetic
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        border-top: 4px solid #4CAF50;
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        color: #2e3b4e;
    }
    .metric-label {
        font-size: 14px;
        color: #6b7c93;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .blocked-metric {
        border-top-color: #F44336;
    }
    .warning-metric {
        border-top-color: #FF9800;
    }
    
    /* Console Output Styling */
    .console-output {
        font-family: 'Courier New', Courier, monospace;
        background-color: #1e1e1e;
        color: #00ff00;
        padding: 15px;
        border-radius: 5px;
        max-height: 400px;
        overflow-y: auto;
        white-space: pre-wrap;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------
# Application State & Initialization
# -----------------------------------------

if 'supervisor' not in st.session_state:
    setup_sandbox()  # Ensure testing directories exist
    st.session_state.supervisor = Supervisor()

if 'command_history' not in st.session_state:
    st.session_state.command_history = []

if 'console_log' not in st.session_state:
    st.session_state.console_log = ""

# -----------------------------------------
# UI Components
# -----------------------------------------

st.title("🛡️ ArmorIQ Supervisor Dashboard")
st.markdown("Production-Level Autonomous Control Sandbox")

# Side Panel for Commands
with st.sidebar:
    st.header("Terminal Input")
    st.markdown("Enter agent commands to execute via the pipeline.")
    
    # Pre-built examples for demo purposes
    example_commands = [
        "Select a command...",
        "clean workspace",
        "organize files",
        "clean and organize workspace",
        "delete system config",
    ]
    
    selected_option = st.selectbox("Quick Commands", example_commands)
    
    # Manual Text Input
    user_input = st.text_input("Manual Command Entry:", placeholder="Type command here...")
    
    # Determine the execution command
    cmd_to_run = ""
    if st.button("Execute Command", type="primary"):
        if selected_option != "Select a command...":
            cmd_to_run = selected_option
        elif user_input:
            cmd_to_run = user_input
            
        if cmd_to_run:
            st.session_state.command_history.append(cmd_to_run)
            
            # Capture stdio from supervisor directly into a string buffer
            old_stdout = sys.stdout
            captured_output = io.StringIO()
            sys.stdout = captured_output
            
            try:
                # Process the command through our backend!
                st.session_state.supervisor.process(cmd_to_run)
            finally:
                sys.stdout = old_stdout
            
            # Store output 
            output_str = captured_output.getvalue()
            st.session_state.console_log = output_str

# -----------------------------------------
# Main Content Area
# -----------------------------------------

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Console Output")
    if st.session_state.console_log:
        st.markdown(f'<div class="console-output">{st.session_state.console_log}</div>', unsafe_allow_html=True)
    else:
        st.info("Awaiting command execution...")

with col2:
    st.subheader("Session Statistics")
    
    # Fetch live stats from the supervisor object instance
    sup = st.session_state.supervisor
    
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(st.session_state.command_history)}</div>
            <div class="metric-label">Commands Processed</div>
        </div>
        <br>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{sup.allowed_count}</div>
            <div class="metric-label">Policies Allowed</div>
        </div>
        <br>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="metric-card blocked-metric">
            <div class="metric-value">{sup.blocked_count}</div>
            <div class="metric-label">Actions Blocked</div>
        </div>
    """, unsafe_allow_html=True)


# -----------------------------------------
# Realtime History Database View
# -----------------------------------------
st.markdown("---")
st.subheader("Live Secure Execution Log")

try:
    with open('history.json', 'r') as f:
        history_data = json.load(f)
        if history_data:
            # Reverse to show newest first!
            st.dataframe(history_data[::-1], use_container_width=True)
        else:
            st.write("No history records yet.")
except Exception as e:
    st.warning("Could not load history.json. It may not exist yet.")
