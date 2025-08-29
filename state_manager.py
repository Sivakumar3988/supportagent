"""
State Manager for LangGraph Agent
Handles state persistence and updates across all stages
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import json
import copy

@dataclass
class AgentState:
    """Central state object that persists across all stages"""
    
    # Original input
    customer_name: str = ""
    email: str = ""
    query: str = ""
    priority: str = ""
    ticket_id: str = ""
    
    # Processing state
    current_stage: str = "INTAKE"
    stage_history: List[str] = field(default_factory=list)
    
    # Extracted information
    entities: Dict[str, Any] = field(default_factory=dict)
    normalized_fields: Dict[str, Any] = field(default_factory=dict)
    enriched_data: Dict[str, Any] = field(default_factory=dict)
    
    # Knowledge base and solutions
    kb_results: List[Dict[str, Any]] = field(default_factory=list)
    solutions: List[Dict[str, Any]] = field(default_factory=list)
    solution_scores: List[float] = field(default_factory=list)
    
    # Decisions and actions
    escalation_required: bool = False
    escalation_reason: str = ""
    actions_taken: List[str] = field(default_factory=list)
    
    # Communication
    clarification_questions: List[str] = field(default_factory=list)
    human_responses: List[str] = field(default_factory=list)
    generated_response: str = ""
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    processing_log: List[Dict[str, Any]] = field(default_factory=list)

class StateManager:
    """Manages agent state persistence and updates"""
    
    def __init__(self):
        self.state = AgentState()
    
    def initialize_state(self, input_data: Dict[str, Any]) -> AgentState:
        """Initialize state with input data"""
        self.state.customer_name = input_data.get("customer_name", "")
        self.state.email = input_data.get("email", "")
        self.state.query = input_data.get("query", "")
        self.state.priority = input_data.get("priority", "medium")
        self.state.ticket_id = input_data.get("ticket_id", "")
        
        self.log_event("STATE_INITIALIZED", {"input_keys": list(input_data.keys())})
        return self.state
    
    def update_stage(self, stage_name: str) -> None:
        """Update current stage and add to history"""
        if self.state.current_stage:
            self.state.stage_history.append(self.state.current_stage)
        
        self.state.current_stage = stage_name
        self.state.updated_at = datetime.now()
        
        self.log_event("STAGE_UPDATED", {
            "from": self.state.stage_history[-1] if self.state.stage_history else None,
            "to": stage_name
        })
    
    def update_entities(self, entities: Dict[str, Any]) -> None:
        """Update extracted entities"""
        self.state.entities.update(entities)
        self.log_event("ENTITIES_UPDATED", {"entities": list(entities.keys())})
    
    def update_normalized_fields(self, fields: Dict[str, Any]) -> None:
        """Update normalized fields"""
        self.state.normalized_fields.update(fields)
        self.log_event("FIELDS_NORMALIZED", {"fields": list(fields.keys())})
    
    def add_enriched_data(self, data: Dict[str, Any]) -> None:
        """Add enriched data"""
        self.state.enriched_data.update(data)
        self.log_event("DATA_ENRICHED", {"data_types": list(data.keys())})
    
    def add_kb_result(self, result: Dict[str, Any]) -> None:
        """Add knowledge base search result"""
        self.state.kb_results.append(result)
        self.log_event("KB_RESULT_ADDED", {"result_id": result.get("id", "unknown")})
    
    def add_solution(self, solution: Dict[str, Any], score: float) -> None:
        """Add solution with score"""
        self.state.solutions.append(solution)
        self.state.solution_scores.append(score)
        self.log_event("SOLUTION_ADDED", {"score": score, "solution_id": solution.get("id", "unknown")})
    
    def set_escalation(self, required: bool, reason: str = "") -> None:
        """Set escalation status"""
        self.state.escalation_required = required
        self.state.escalation_reason = reason
        self.log_event("ESCALATION_SET", {"required": required, "reason": reason})
    
    def add_clarification_question(self, question: str) -> None:
        """Add clarification question"""
        self.state.clarification_questions.append(question)
        self.log_event("CLARIFICATION_ADDED", {"question": question})
    
    def add_human_response(self, response: str) -> None:
        """Add human response"""
        self.state.human_responses.append(response)
        self.log_event("HUMAN_RESPONSE_ADDED", {"response_length": len(response)})
    
    def set_generated_response(self, response: str) -> None:
        """Set generated customer response"""
        self.state.generated_response = response
        self.log_event("RESPONSE_GENERATED", {"response_length": len(response)})
    
    def add_action(self, action: str) -> None:
        """Add executed action"""
        self.state.actions_taken.append(action)
        self.log_event("ACTION_EXECUTED", {"action": action})
    
    def log_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Log an event to processing log"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "stage": self.state.current_stage,
            "event_type": event_type,
            "details": details
        }
        self.state.processing_log.append(log_entry)
    
    def get_current_state(self) -> AgentState:
        """Get current state"""
        return copy.deepcopy(self.state)
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get state summary for logging"""
        return {
            "ticket_id": self.state.ticket_id,
            "customer_name": self.state.customer_name,
            "current_stage": self.state.current_stage,
            "stages_completed": len(self.state.stage_history),
            "escalation_required": self.state.escalation_required,
            "solutions_found": len(self.state.solutions),
            "actions_taken": len(self.state.actions_taken),
            "processing_time": str(self.state.updated_at - self.state.created_at)
        }
    
    def export_final_payload(self) -> Dict[str, Any]:
        """Export final structured payload"""
        return {
            "input": {
                "customer_name": self.state.customer_name,
                "email": self.state.email,
                "query": self.state.query,
                "priority": self.state.priority,
                "ticket_id": self.state.ticket_id
            },
            "processing": {
                "stages_completed": self.state.stage_history + [self.state.current_stage],
                "entities_extracted": self.state.entities,
                "enriched_data": self.state.enriched_data,
                "knowledge_base_results": len(self.state.kb_results),
                "solutions_evaluated": len(self.state.solutions)
            },
            "decisions": {
                "escalation_required": self.state.escalation_required,
                "escalation_reason": self.state.escalation_reason,
                "best_solution_score": max(self.state.solution_scores) if self.state.solution_scores else 0
            },
            "output": {
                "generated_response": self.state.generated_response,
                "actions_executed": self.state.actions_taken,
                "final_status": "escalated" if self.state.escalation_required else "resolved"
            },
            "metadata": {
                "created_at": self.state.created_at.isoformat(),
                "completed_at": self.state.updated_at.isoformat(),
                "processing_log": self.state.processing_log
            }
        }