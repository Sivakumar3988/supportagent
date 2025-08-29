"""
Main LangGraph Agent Implementation
Orchestrates the customer support workflow using LangGraph
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# LangGraph imports (simulated - in real implementation, use actual LangGraph)
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from config import AGENT_CONFIG, STAGES
from state_manager import StateManager
from stage_nodes import (
    intake_node, understand_node, prepare_node, ask_node, wait_node,
    retrieve_node, decide_node, update_node, create_node, do_node, complete_node
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LangieAgent:
    """
    Langie - The LangGraph Customer Support Agent
    
    A structured and logical agent that processes customer support requests
    through 11 defined stages with state persistence and MCP client integration.
    """
    
    def __init__(self):
        self.name = AGENT_CONFIG["name"]
        self.version = AGENT_CONFIG["version"]
        self.personality = AGENT_CONFIG["personality"]
        
        self.state_manager = StateManager()
        self.graph = None
        self.memory = MemorySaver()
        
        # Build the workflow graph
        self._build_graph()
        
        logger.info(f"Initialized {self.name} v{self.version}")
    
    def _build_graph(self):
        """Build the LangGraph workflow"""
        # Create state graph
        workflow = StateGraph(Dict[str, Any])
        
        # Add all stage nodes
        workflow.add_node("intake", self._wrap_node(intake_node))
        workflow.add_node("understand", self._wrap_node(understand_node))
        workflow.add_node("prepare", self._wrap_node(prepare_node))
        workflow.add_node("ask", self._wrap_node(ask_node))
        workflow.add_node("wait", self._wrap_node(wait_node))
        workflow.add_node("retrieve", self._wrap_node(retrieve_node))
        workflow.add_node("decide", self._wrap_node(decide_node))
        workflow.add_node("update", self._wrap_node(update_node))
        workflow.add_node("create", self._wrap_node(create_node))
        workflow.add_node("do", self._wrap_node(do_node))
        workflow.add_node("complete", self._wrap_node(complete_node))
        
        # Define the workflow edges (linear flow with conditional routing)
        workflow.set_entry_point("intake")
        workflow.add_edge("intake", "understand")
        workflow.add_edge("understand", "prepare")
        workflow.add_edge("prepare", "ask")
        workflow.add_edge("ask", "wait")
        workflow.add_edge("wait", "retrieve")
        workflow.add_edge("retrieve", "decide")
        
        # Conditional routing after DECIDE stage
        workflow.add_conditional_edges(
            "decide",
            self._should_escalate,
            {
                "escalate": "update",
                "continue": "update"
            }
        )
        
        workflow.add_edge("update", "create")
        workflow.add_edge("create", "do")
        workflow.add_edge("do", "complete")
        workflow.add_edge("complete", END)
        
        # Compile the graph
        self.graph = workflow.compile(checkpointer=self.memory)
        
        logger.info("LangGraph workflow built successfully")
    
    def _wrap_node(self, node_func):
        """Wrap node function to pass state manager"""
        async def wrapped_node(state):
            logger.info(f"Executing node: {node_func.__name__}")
            try:
                result = await node_func(self.state_manager)
                # Update the graph state with results
                state.update(result)
                return state
            except Exception as e:
                logger.error(f"Error in node {node_func.__name__}: {e}")
                state["error"] = str(e)
                return state
        
        return wrapped_node
    
    def _should_escalate(self, state: Dict[str, Any]) -> str:
        """Determine if case should be escalated based on current state"""
        # Check if escalation was decided in DECIDE stage
        agent_state = self.state_manager.get_current_state()
        
        if agent_state.escalation_required:
            logger.info("Case marked for escalation")
            return "escalate"
        else:
            logger.info("Case can be resolved automatically")
            return "continue"
    
    async def process_request(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a customer support request through the complete workflow
        
        Args:
            input_data: Customer request data containing name, email, query, priority, ticket_id
            
        Returns:
            Final structured payload with processing results
        """
        logger.info(f"Starting to process request for ticket: {input_data.get('ticket_id', 'UNKNOWN')}")
        
        try:
            # Initialize state with input data
            self.state_manager.initialize_state(input_data)
            
            # Create initial graph state
            initial_state = {
                "request_id": input_data.get("ticket_id", f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                "input_data": input_data,
                "processing_started": datetime.now().isoformat()
            }
            
            # Execute the workflow
            config = {"configurable": {"thread_id": initial_state["request_id"]}}
            
            logger.info("Executing LangGraph workflow...")
            final_state = await self.graph.ainvoke(initial_state, config)
            
            # Get final payload from state manager
            final_payload = self.state_manager.export_final_payload()
            final_state["final_payload"] = final_payload
            
            logger.info("Workflow completed successfully")
            return final_state
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            error_payload = {
                "error": str(e),
                "status": "failed",
                "timestamp": datetime.now().isoformat(),
                "input_data": input_data
            }
            return error_payload
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information and capabilities"""
        return {
            "name": self.name,
            "version": self.version,
            "personality": self.personality,
            "capabilities": {
                "stages": len(STAGES),
                "stage_names": [stage.name for stage in STAGES],
                "deterministic_stages": [s.name for s in STAGES if s.mode.value == "deterministic"],
                "non_deterministic_stages": [s.name for s in STAGES if s.mode.value == "non_deterministic"],
                "human_interaction_stages": [s.name for s in STAGES if s.mode.value == "human"],
                "mcp_integration": True,
                "state_persistence": True
            }
        }
    
    async def simulate_human_interaction(self, questions: list, responses: list = None) -> Dict[str, Any]:
        """
        Simulate human interaction for ASK/WAIT stages
        In production, this would integrate with actual human agent interface
        """
        if responses is None:
            # Default responses for simulation
            responses = [
                "My account number is 123456789",
                "The order number is ORD-2024-001",
                "This happened yesterday around 3 PM"
            ]
        
        interaction_data = {
            "questions_asked": questions,
            "responses_received": responses[:len(questions)],
            "interaction_completed": True,
            "timestamp": datetime.now().isoformat()
        }
        
        # Update state with human responses
        for response in responses[:len(questions)]:
            self.state_manager.add_human_response(response)
        
        logger.info(f"Simulated human interaction: {len(questions)} questions, {len(responses)} responses")
        return interaction_data

# Workflow configuration for external systems
LANGIE_WORKFLOW_CONFIG = {
    "agent_name": "Langie",
    "workflow_version": "1.0.0",
    "stages": [
        {
            "name": "INTAKE",
            "mode": "payload_only",
            "abilities": ["accept_payload"],
            "prompt": "Accept and validate incoming customer request payload"
        },
        {
            "name": "UNDERSTAND", 
            "mode": "deterministic",
            "abilities": ["parse_request_text", "extract_entities"],
            "prompt": "Execute abilities in sequence to understand customer request"
        },
        {
            "name": "PREPARE",
            "mode": "deterministic", 
            "abilities": ["normalize_fields", "enrich_records", "add_flags_calculations"],
            "prompt": "Execute abilities in sequence to prepare and enrich data"
        },
        {
            "name": "ASK",
            "mode": "human",
            "abilities": ["clarify_question"],
            "prompt": "Request clarification from human if needed"
        },
        {
            "name": "WAIT",
            "mode": "deterministic",
            "abilities": ["extract_answer", "store_answer"], 
            "prompt": "Execute abilities in sequence to process human responses"
        },
        {
            "name": "RETRIEVE",
            "mode": "deterministic",
            "abilities": ["knowledge_base_search", "store_data"],
            "prompt": "Execute abilities in sequence to search knowledge base"
        },
        {
            "name": "DECIDE",
            "mode": "non_deterministic",
            "abilities": ["solution_evaluation", "escalation_decision", "update_payload"],
            "prompt": "Score solutions and escalate if best score <90"
        },
        {
            "name": "UPDATE",
            "mode": "deterministic",
            "abilities": ["update_ticket", "close_ticket"],
            "prompt": "Execute abilities in sequence to update ticket status"
        },
        {
            "name": "CREATE",
            "mode": "deterministic", 
            "abilities": ["response_generation"],
            "prompt": "Execute abilities in sequence to generate customer response"
        },
        {
            "name": "DO",
            "mode": "deterministic",
            "abilities": ["execute_api_calls", "trigger_notifications"],
            "prompt": "Execute abilities in sequence to perform actions and notifications"
        },
        {
            "name": "COMPLETE",
            "mode": "payload_only",
            "abilities": ["output_payload"],
            "prompt": "Output final structured payload"
        }
    ],
    "mcp_server_mapping": {
        "COMMON": [
            "accept_payload", "parse_request_text", "normalize_fields", 
            "add_flags_calculations", "store_answer", "store_data",
            "solution_evaluation", "update_payload", "response_generation", 
            "output_payload"
        ],
        "ATLAS": [
            "extract_entities", "enrich_records", "clarify_question",
            "extract_answer", "knowledge_base_search", "escalation_decision",
            "update_ticket", "close_ticket", "execute_api_calls", 
            "trigger_notifications"
        ]
    },
    "input_schema": {
        "customer_name": "string",
        "email": "string", 
        "query": "string",
        "priority": "string (low|medium|high|critical)",
        "ticket_id": "string"
    }
}

# Export the main agent class
__all__ = ["LangieAgent", "LANGIE_WORKFLOW_CONFIG"]