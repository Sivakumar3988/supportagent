"""
Streamlit Testing Interface for Langie Agent
Interactive web interface for testing the LangGraph Customer Support Agent
"""

import streamlit as st
import asyncio
import json
import pandas as pd
from datetime import datetime
import time
from typing import Dict, Any, List

# Import our agent
from langgraph_agent import LangieAgent
from config import STAGES, StageMode
from state_manager import StateManager

# Configure Streamlit page
st.set_page_config(
    page_title="🧩 Langie Agent Tester",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stage-box {
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        background-color: #f8f9fa;
        margin: 0.5rem 0;
    }
    .success-box {
        border-left-color: #28a745;
        background-color: #d4edda;
    }
    .error-box {
        border-left-color: #dc3545;
        background-color: #f8d7da;
    }
    .warning-box {
        border-left-color: #ffc107;
        background-color: #fff3cd;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitTester:
    """Streamlit testing interface for Langie Agent"""
    
    def __init__(self):
        if 'agent' not in st.session_state:
            st.session_state.agent = LangieAgent()
        if 'test_history' not in st.session_state:
            st.session_state.test_history = []
        if 'current_test' not in st.session_state:
            st.session_state.current_test = None
    
    def render_header(self):
        """Render main header"""
        st.markdown('<h1 class="main-header">🧩 Langie Agent Interactive Tester</h1>', unsafe_allow_html=True)
        
        # Agent info in expandable section
        with st.expander("🤖 Agent Information", expanded=False):
            agent_info = st.session_state.agent.get_agent_info()
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Name:** {agent_info['name']}")
                st.write(f"**Version:** {agent_info['version']}")
                st.write(f"**Stages:** {agent_info['capabilities']['stages']}")
            
            with col2:
                st.write(f"**Personality:** {agent_info['personality']}")
                st.write(f"**MCP Integration:** ✅")
                st.write(f"**State Persistence:** ✅")
    
    def render_quick_test_scenarios(self):
        """Render predefined test scenarios"""
        st.sidebar.markdown("## 🎯 Quick Test Scenarios")
        
        scenarios = {
            "📦 Order Status (Medium)": {
                "customer_name": "Alice Johnson",
                "email": "alice.johnson@email.com",
                "query": "I placed an order 3 days ago but haven't received any tracking information. Order #ORD-2024-001",
                "priority": "medium",
                "ticket_id": "T-ORDER-001"
            },
            "💳 Payment Issue (High)": {
                "customer_name": "Bob Wilson",
                "email": "bob.wilson@company.com", 
                "query": "I was charged twice for my subscription but only received one confirmation. Need immediate refund!",
                "priority": "high",
                "ticket_id": "T-PAYMENT-002"
            },
            "🔐 Account Access (Critical)": {
                "customer_name": "Carol Smith",
                "email": "carol.smith@enterprise.com",
                "query": "Cannot access my business account for 2 days. Password reset not working. Urgent!",
                "priority": "critical", 
                "ticket_id": "T-ACCESS-003"
            },
            "❓ General Inquiry (Low)": {
                "customer_name": "David Lee",
                "email": "david.lee@gmail.com",
                "query": "How do I change my delivery address for future orders?",
                "priority": "low",
                "ticket_id": "T-GENERAL-004"
            },
            "🛒 Complex Issue (High)": {
                "customer_name": "Emma Davis",
                "email": "emma.davis@business.org",
                "query": "Multiple problems: wrong item delivered, charged incorrect amount, and cannot return the item through your website. Account #ACC123456",
                "priority": "high",
                "ticket_id": "T-COMPLEX-005"
            }
        }
        
        selected_scenario = st.sidebar.selectbox(
            "Choose a scenario:",
            ["Custom"] + list(scenarios.keys())
        )
        
        if selected_scenario != "Custom":
            if st.sidebar.button("📋 Load Scenario"):
                scenario_data = scenarios[selected_scenario]
                for key, value in scenario_data.items():
                    st.session_state[f"input_{key}"] = value
                st.rerun()
        
        return selected_scenario, scenarios
    
    def render_input_form(self):
        """Render input form for customer request"""
        st.markdown("## 📝 Customer Request Input")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            customer_name = st.text_input(
                "Customer Name *",
                value=st.session_state.get("input_customer_name", ""),
                key="input_customer_name"
            )
            
            email = st.text_input(
                "Email Address *", 
                value=st.session_state.get("input_email", ""),
                key="input_email"
            )
            
            query = st.text_area(
                "Customer Query *",
                value=st.session_state.get("input_query", ""),
                height=100,
                key="input_query",
                help="Describe the customer's issue or question in detail"
            )
        
        with col2:
            priority = st.selectbox(
                "Priority Level *",
                ["low", "medium", "high", "critical"],
                index=1,
                key="input_priority"
            )
            
            ticket_id = st.text_input(
                "Ticket ID *",
                value=st.session_state.get("input_ticket_id", f"T-{datetime.now().strftime('%Y%m%d-%H%M%S')}"),
                key="input_ticket_id"
            )
            
            # Validation
            valid = all([customer_name, email, query, ticket_id])
            
            if valid:
                st.success("✅ All fields valid")
            else:
                st.error("❌ Please fill all required fields")
        
        return {
            "customer_name": customer_name,
            "email": email,
            "query": query,
            "priority": priority,
            "ticket_id": ticket_id
        }, valid
    
    def render_execution_controls(self, input_data: Dict[str, Any], is_valid: bool):
        """Render execution controls"""
        st.markdown("## 🚀 Execution Controls")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("▶️ Run Full Workflow", disabled=not is_valid, type="primary"):
                return "full", input_data
        
        with col2:
            if st.button("🔍 Step-by-Step Mode", disabled=not is_valid):
                return "step", input_data
        
        with col3:
            if st.button("🧪 Batch Test", disabled=not is_valid):
                return "batch", input_data
        
        return None, input_data
    
    async def execute_full_workflow(self, input_data: Dict[str, Any]):
        """Execute complete workflow with progress tracking"""
        progress_bar = st.progress(0)
        status_container = st.container()
        
        with status_container:
            st.info("🔄 Initializing workflow...")
        
        try:
            # Start execution
            start_time = time.time()
            
            # Create progress callback (simulated)
            def update_progress(stage_num: int, stage_name: str):
                progress = stage_num / 11
                progress_bar.progress(progress)
                status_container.info(f"🎯 Executing Stage {stage_num}/11: {stage_name}")
            
            # Execute workflow
            result = await st.session_state.agent.process_request(input_data)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Complete progress
            progress_bar.progress(1.0)
            status_container.success(f"✅ Workflow completed in {execution_time:.2f} seconds")
            
            return result, execution_time
        
        except Exception as e:
            status_container.error(f"❌ Error: {str(e)}")
            return None, 0
    
    def render_results(self, result: Dict[str, Any], execution_time: float):
        """Render execution results"""
        if not result:
            return
        
        st.markdown("## 📊 Execution Results")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        final_payload = result.get("final_payload", {})
        processing = final_payload.get("processing", {})
        decisions = final_payload.get("decisions", {})
        
        with col1:
            st.metric("⏱️ Execution Time", f"{execution_time:.2f}s")
        
        with col2:
            stages_completed = len(processing.get("stages_completed", []))
            st.metric("🎯 Stages Completed", stages_completed, delta=f"{stages_completed}/11")
        
        with col3:
            best_score = decisions.get("best_solution_score", 0)
            st.metric("📊 Best Solution Score", f"{best_score}%", delta="High" if best_score >= 90 else "Low")
        
        with col4:
            escalated = decisions.get("escalation_required", False)
            st.metric("🚨 Escalated", "Yes" if escalated else "No", delta="⬆️" if escalated else "✅")
        
        # Detailed results in tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Summary", "📋 Stages", "💬 Response", "📊 Data", "📝 Logs"])
        
        with tab1:
            self._render_summary_tab(final_payload)
        
        with tab2:
            self._render_stages_tab(final_payload)
        
        with tab3:
            self._render_response_tab(final_payload)
        
        with tab4:
            self._render_data_tab(final_payload)
        
        with tab5:
            self._render_logs_tab(final_payload)
    
    def _render_summary_tab(self, final_payload: Dict[str, Any]):
        """Render summary tab"""
        input_data = final_payload.get("input", {})
        decisions = final_payload.get("decisions", {})
        output = final_payload.get("output", {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📨 Request Summary")
            st.write(f"**Customer:** {input_data.get('customer_name')}")
            st.write(f"**Email:** {input_data.get('email')}")
            st.write(f"**Priority:** {input_data.get('priority', '').upper()}")
            st.write(f"**Ticket:** {input_data.get('ticket_id')}")
            
            st.markdown("### 📊 Processing Results")
            st.write(f"**Status:** {output.get('final_status', 'Unknown')}")
            st.write(f"**Escalation:** {'Required' if decisions.get('escalation_required') else 'Not Required'}")
            if decisions.get('escalation_reason'):
                st.write(f"**Reason:** {decisions.get('escalation_reason')}")
        
        with col2:
            st.markdown("### ❓ Customer Query")
            st.write(input_data.get('query', 'No query provided'))
            
            st.markdown("### 💬 Generated Response")
            response = output.get('generated_response', 'No response generated')
            st.write(response)
    
    def _render_stages_tab(self, final_payload: Dict[str, Any]):
        """Render stages execution tab"""
        processing = final_payload.get("processing", {})
        stages_completed = processing.get("stages_completed", [])
        
        st.markdown("### 🎯 Stage Execution Flow")
        
        # Create a visual flow
        stage_data = []
        for i, stage_name in enumerate(stages_completed):
            stage_config = next((s for s in STAGES if s.name == stage_name), None)
            if stage_config:
                stage_data.append({
                    "Stage": f"{i+1}. {stage_name}",
                    "Mode": stage_config.mode.value.replace("_", " ").title(),
                    "Abilities": len(stage_config.abilities),
                    "Status": "✅ Completed"
                })
        
        if stage_data:
            df = pd.DataFrame(stage_data)
            st.dataframe(df, use_container_width=True)
        
        # Stage details
        st.markdown("### 📋 Stage Details")
        for stage_name in stages_completed:
            stage_config = next((s for s in STAGES if s.name == stage_name), None)
            if stage_config:
                with st.expander(f"🎯 {stage_name} - {stage_config.mode.value}"):
                    st.write(f"**Description:** {stage_config.description}")
                    st.write(f"**Mode:** {stage_config.mode.value}")
                    st.write(f"**Abilities:** {', '.join([a.name for a in stage_config.abilities])}")
    
    def _render_response_tab(self, final_payload: Dict[str, Any]):
        """Render response tab"""
        output = final_payload.get("output", {})
        decisions = final_payload.get("decisions", {})
        
        st.markdown("### 💬 Customer Response")
        
        response = output.get('generated_response', 'No response generated')
        
        if response:
            st.markdown("#### Generated Response:")
            st.info(response)
            
            # Response analysis
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Word Count", len(response.split()))
            
            with col2:
                st.metric("Character Count", len(response))
            
            with col3:
                sentiment = "Professional" if "Dear" in response else "Casual"
                st.metric("Tone", sentiment)
        
        st.markdown("### 🎬 Actions Executed")
        actions = output.get('actions_executed', [])
        if actions:
            for i, action in enumerate(actions, 1):
                st.write(f"{i}. {action}")
        else:
            st.write("No actions were executed")
    
    def _render_data_tab(self, final_payload: Dict[str, Any]):
        """Render data analysis tab"""
        processing = final_payload.get("processing", {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🧠 Extracted Entities")
            entities = processing.get("entities_extracted", {})
            if entities:
                for key, value in entities.items():
                    st.write(f"**{key.title()}:** {value}")
            else:
                st.write("No entities extracted")
        
        with col2:
            st.markdown("### 📚 Knowledge Base")
            kb_results = processing.get("knowledge_base_results", 0)
            solutions = processing.get("solutions_evaluated", 0)
            
            st.metric("KB Results Found", kb_results)
            st.metric("Solutions Evaluated", solutions)
        
        # Raw data in expandable section
        with st.expander("🔍 Raw Data (JSON)"):
            st.json(final_payload)
    
    def _render_logs_tab(self, final_payload: Dict[str, Any]):
        """Render logs tab"""
        metadata = final_payload.get("metadata", {})
        logs = metadata.get("processing_log", [])
        
        if logs:
            st.markdown("### 📝 Processing Logs")
            
            # Filter options
            col1, col2 = st.columns(2)
            
            with col1:
                event_types = list(set([log.get("event_type", "unknown") for log in logs]))
                selected_events = st.multiselect("Filter by Event Type", event_types, default=event_types)
            
            with col2:
                stages = list(set([log.get("stage", "unknown") for log in logs]))
                selected_stages = st.multiselect("Filter by Stage", stages, default=stages)
            
            # Filter logs
            filtered_logs = [
                log for log in logs 
                if log.get("event_type") in selected_events 
                and log.get("stage") in selected_stages
            ]
            
            # Display logs
            for log in filtered_logs[-20:]:  # Show last 20 logs
                timestamp = log.get("timestamp", "")
                stage = log.get("stage", "unknown")
                event_type = log.get("event_type", "unknown")
                details = log.get("details", {})
                
                with st.expander(f"🕐 {timestamp} - {stage} - {event_type}"):
                    st.json(details)
        else:
            st.write("No logs available")
    
    def render_test_history(self):
        """Render test history sidebar"""
        st.sidebar.markdown("## 📋 Test History")
        
        if st.session_state.test_history:
            for i, test in enumerate(reversed(st.session_state.test_history[-5:])):
                timestamp = test.get("timestamp", "")
                ticket_id = test.get("input", {}).get("ticket_id", "Unknown")
                status = test.get("status", "Unknown")
                
                if st.sidebar.button(f"📋 {ticket_id} ({status})", key=f"history_{i}"):
                    st.session_state.current_test = test
                    st.rerun()
        else:
            st.sidebar.write("No test history yet")
        
        if st.sidebar.button("🗑️ Clear History"):
            st.session_state.test_history = []
            st.rerun()

# Main Streamlit app
def main():
    """Main Streamlit application"""
    tester = StreamlitTester()
    
    # Render header
    tester.render_header()
    
    # Sidebar for quick scenarios and history
    selected_scenario, scenarios = tester.render_quick_test_scenarios()
    tester.render_test_history()
    
    # Main content area
    input_data, is_valid = tester.render_input_form()
    
    # Execution controls
    action, data = tester.render_execution_controls(input_data, is_valid)
    
    if action == "full":
        st.markdown("---")
        
        # Execute workflow
        with st.spinner("🔄 Executing workflow..."):
            result, execution_time = asyncio.run(tester.execute_full_workflow(data))
        
        if result:
            # Save to history
            test_record = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "input": data,
                "result": result,
                "execution_time": execution_time,
                "status": "Completed"
            }
            st.session_state.test_history.append(test_record)
            
            # Render results
            tester.render_results(result, execution_time)
    
    elif action == "step":
        st.info("🔄 Step-by-step mode - Coming soon! This will allow you to execute stages one by one.")
    
    elif action == "batch":
        st.info("🧪 Batch test mode - Coming soon! This will run multiple test scenarios automatically.")

if __name__ == "__main__":
    main()