"""
Agent Configuration File
Contains all configuration settings for the LangGraph Customer Support Agent
"""

from enum import Enum
from typing import Dict, List, Any
from dataclasses import dataclass

class MCPServer(Enum):
    COMMON = "common"
    ATLAS = "atlas"

class StageMode(Enum):
    DETERMINISTIC = "deterministic"
    NON_DETERMINISTIC = "non_deterministic"
    HUMAN = "human"
    PAYLOAD_ONLY = "payload_only"

@dataclass
class Ability:
    name: str
    server: MCPServer
    description: str

@dataclass
class Stage:
    name: str
    mode: StageMode
    abilities: List[Ability]
    description: str

# Agent Configuration
AGENT_CONFIG = {
    "name": "Langie",
    "version": "1.0.0",
    "personality": "structured and logical Lang Graph Agent",
    "description": "Customer support workflow orchestrator"
}

# Input Schema
INPUT_SCHEMA = {
    "customer_name": str,
    "email": str,
    "query": str,
    "priority": str,
    "ticket_id": str
}

# Stage Definitions
STAGES = [
    Stage(
        name="INTAKE",
        mode=StageMode.PAYLOAD_ONLY,
        abilities=[
            Ability("accept_payload", MCPServer.COMMON, "Capture incoming request payload")
        ],
        description="Accept and validate incoming customer request"
    ),
    Stage(
        name="UNDERSTAND",
        mode=StageMode.DETERMINISTIC,
        abilities=[
            Ability("parse_request_text", MCPServer.COMMON, "Convert unstructured request to structured data"),
            Ability("extract_entities", MCPServer.ATLAS, "Identify product, account, dates")
        ],
        description="Parse and understand customer request"
    ),
    Stage(
        name="PREPARE",
        mode=StageMode.DETERMINISTIC,
        abilities=[
            Ability("normalize_fields", MCPServer.COMMON, "Standardize dates, codes, IDs"),
            Ability("enrich_records", MCPServer.ATLAS, "Add SLA, historical ticket info"),
            Ability("add_flags_calculations", MCPServer.COMMON, "Compute priority or SLA risk")
        ],
        description="Normalize and enrich customer data"
    ),
    Stage(
        name="ASK",
        mode=StageMode.HUMAN,
        abilities=[
            Ability("clarify_question", MCPServer.ATLAS, "Request missing information")
        ],
        description="Ask clarifying questions if needed"
    ),
    Stage(
        name="WAIT",
        mode=StageMode.DETERMINISTIC,
        abilities=[
            Ability("extract_answer", MCPServer.ATLAS, "Wait and capture concise response"),
            Ability("store_answer", MCPServer.COMMON, "Update payload with response")
        ],
        description="Wait for and process human responses"
    ),
    Stage(
        name="RETRIEVE",
        mode=StageMode.DETERMINISTIC,
        abilities=[
            Ability("knowledge_base_search", MCPServer.ATLAS, "Lookup KB or FAQ"),
            Ability("store_data", MCPServer.COMMON, "Attach retrieved info to payload")
        ],
        description="Search knowledge base for solutions"
    ),
    Stage(
        name="DECIDE",
        mode=StageMode.NON_DETERMINISTIC,
        abilities=[
            Ability("solution_evaluation", MCPServer.COMMON, "Score potential solutions 1-100"),
            Ability("escalation_decision", MCPServer.ATLAS, "Assign to human agent if score <90"),
            Ability("update_payload", MCPServer.COMMON, "Record decision outcomes")
        ],
        description="Evaluate solutions and make escalation decisions"
    ),
    Stage(
        name="UPDATE",
        mode=StageMode.DETERMINISTIC,
        abilities=[
            Ability("update_ticket", MCPServer.ATLAS, "Modify status, fields, priority"),
            Ability("close_ticket", MCPServer.ATLAS, "Mark issue resolved")
        ],
        description="Update ticket status and information"
    ),
    Stage(
        name="CREATE",
        mode=StageMode.DETERMINISTIC,
        abilities=[
            Ability("response_generation", MCPServer.COMMON, "Draft customer reply")
        ],
        description="Generate customer response"
    ),
    Stage(
        name="DO",
        mode=StageMode.DETERMINISTIC,
        abilities=[
            Ability("execute_api_calls", MCPServer.ATLAS, "Trigger CRM/order system actions"),
            Ability("trigger_notifications", MCPServer.ATLAS, "Notify customer")
        ],
        description="Execute actions and send notifications"
    ),
    Stage(
        name="COMPLETE",
        mode=StageMode.PAYLOAD_ONLY,
        abilities=[
            Ability("output_payload", MCPServer.COMMON, "Print final structured payload")
        ],
        description="Output final results"
    )
]

# Stage prompts for different modes
STAGE_PROMPTS = {
    StageMode.DETERMINISTIC: "Execute abilities in sequence",
    StageMode.NON_DETERMINISTIC: "Score solutions and escalate if <90",
    StageMode.HUMAN: "Request clarification from human",
    StageMode.PAYLOAD_ONLY: "Process payload data only"
}