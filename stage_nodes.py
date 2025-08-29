"""
LangGraph Stage Nodes Implementation
Each stage is implemented as a node function that can be executed by LangGraph
"""

from typing import Dict, Any, List
import logging
from datetime import datetime

from config import STAGES, StageMode
from state_manager import StateManager, AgentState
from mcp_client import CommonMCPClient, AtlasMCPClient, MCPClientError

logger = logging.getLogger(__name__)

class StageExecutor:
    """Executes individual stages in the customer support workflow"""
    
    def __init__(self):
        self.common_client = CommonMCPClient()
        self.atlas_client = AtlasMCPClient()
        self.clients_connected = False
    
    async def setup_clients(self):
        """Connect to MCP clients"""
        if not self.clients_connected:
            common_connected = await self.common_client.connect()
            atlas_connected = await self.atlas_client.connect()
            self.clients_connected = common_connected and atlas_connected
            logger.info(f"MCP Clients connected: {self.clients_connected}")
        return self.clients_connected
    
    async def cleanup_clients(self):
        """Disconnect MCP clients"""
        await self.common_client.disconnect()
        await self.atlas_client.disconnect()
        self.clients_connected = False
    
    def get_client(self, server_type):
        """Get appropriate MCP client"""
        from config import MCPServer
        if server_type == MCPServer.COMMON:
            return self.common_client
        elif server_type == MCPServer.ATLAS:
            return self.atlas_client
        else:
            raise ValueError(f"Unknown server type: {server_type}")
    
    async def execute_stage(self, stage_name: str, state_manager: StateManager) -> Dict[str, Any]:
        """Execute a specific stage"""
        # Find stage configuration
        stage_config = next((s for s in STAGES if s.name == stage_name), None)
        if not stage_config:
            raise ValueError(f"Unknown stage: {stage_name}")
        
        logger.info(f"Executing stage: {stage_name} (mode: {stage_config.mode.value})")
        
        # Update state to current stage
        state_manager.update_stage(stage_name)
        
        # Execute based on stage mode
        if stage_config.mode == StageMode.PAYLOAD_ONLY:
            return await self._execute_payload_stage(stage_config, state_manager)
        elif stage_config.mode == StageMode.DETERMINISTIC:
            return await self._execute_deterministic_stage(stage_config, state_manager)
        elif stage_config.mode == StageMode.NON_DETERMINISTIC:
            return await self._execute_non_deterministic_stage(stage_config, state_manager)
        elif stage_config.mode == StageMode.HUMAN:
            return await self._execute_human_stage(stage_config, state_manager)
        else:
            raise ValueError(f"Unknown stage mode: {stage_config.mode}")

# Individual Stage Node Functions for LangGraph

async def intake_node(state_manager: StateManager) -> Dict[str, Any]:
    """INTAKE Stage - Accept payload"""
    executor = StageExecutor()
    await executor.setup_clients()
    
    try:
        result = await executor.execute_stage("INTAKE", state_manager)
        logger.info("INTAKE stage completed successfully")
        return result
    finally:
        await executor.cleanup_clients()

async def understand_node(state_manager: StateManager) -> Dict[str, Any]:
    """UNDERSTAND Stage - Parse request and extract entities"""
    executor = StageExecutor()
    await executor.setup_clients()
    
    try:
        result = await executor.execute_stage("UNDERSTAND", state_manager)
        logger.info("UNDERSTAND stage completed successfully")
        return result
    finally:
        await executor.cleanup_clients()

async def prepare_node(state_manager: StateManager) -> Dict[str, Any]:
    """PREPARE Stage - Normalize and enrich data"""
    executor = StageExecutor()
    await executor.setup_clients()
    
    try:
        result = await executor.execute_stage("PREPARE", state_manager)
        logger.info("PREPARE stage completed successfully")
        return result
    finally:
        await executor.cleanup_clients()

async def ask_node(state_manager: StateManager) -> Dict[str, Any]:
    """ASK Stage - Request clarification"""
    executor = StageExecutor()
    await executor.setup_clients()
    
    try:
        result = await executor.execute_stage("ASK", state_manager)
        logger.info("ASK stage completed successfully")
        return result
    finally:
        await executor.cleanup_clients()

async def wait_node(state_manager: StateManager) -> Dict[str, Any]:
    """WAIT Stage - Process human responses"""
    executor = StageExecutor()
    await executor.setup_clients()
    
    try:
        result = await executor.execute_stage("WAIT", state_manager)
        logger.info("WAIT stage completed successfully")
        return result
    finally:
        await executor.cleanup_clients()

async def retrieve_node(state_manager: StateManager) -> Dict[str, Any]:
    """RETRIEVE Stage - Search knowledge base"""
    executor = StageExecutor()
    await executor.setup_clients()
    
    try:
        result = await executor.execute_stage("RETRIEVE", state_manager)
        logger.info("RETRIEVE stage completed successfully")
        return result
    finally:
        await executor.cleanup_clients()

async def decide_node(state_manager: StateManager) -> Dict[str, Any]:
    """DECIDE Stage - Evaluate solutions and make escalation decision"""
    executor = StageExecutor()
    await executor.setup_clients()
    
    try:
        result = await executor.execute_stage("DECIDE", state_manager)
        logger.info("DECIDE stage completed successfully")
        return result
    finally:
        await executor.cleanup_clients()

async def update_node(state_manager: StateManager) -> Dict[str, Any]:
    """UPDATE Stage - Update ticket status"""
    executor = StageExecutor()
    await executor.setup_clients()
    
    try:
        result = await executor.execute_stage("UPDATE", state_manager)
        logger.info("UPDATE stage completed successfully")
        return result
    finally:
        await executor.cleanup_clients()

async def create_node(state_manager: StateManager) -> Dict[str, Any]:
    """CREATE Stage - Generate customer response"""
    executor = StageExecutor()
    await executor.setup_clients()
    
    try:
        result = await executor.execute_stage("CREATE", state_manager)
        logger.info("CREATE stage completed successfully")
        return result
    finally:
        await executor.cleanup_clients()

async def do_node(state_manager: StateManager) -> Dict[str, Any]:
    """DO Stage - Execute actions and send notifications"""
    executor = StageExecutor()
    await executor.setup_clients()
    
    try:
        result = await executor.execute_stage("DO", state_manager)
        logger.info("DO stage completed successfully")
        return result
    finally:
        await executor.cleanup_clients()

async def complete_node(state_manager: StateManager) -> Dict[str, Any]:
    """COMPLETE Stage - Output final payload"""
    executor = StageExecutor()
    await executor.setup_clients()
    
    try:
        result = await executor.execute_stage("COMPLETE", state_manager)
        logger.info("COMPLETE stage completed successfully")
        return result
    finally:
        await executor.cleanup_clients()

# Stage Execution Methods for StageExecutor

async def _execute_payload_stage(self, stage_config, state_manager: StateManager) -> Dict[str, Any]:
    """Execute payload-only stages (INTAKE, COMPLETE)"""
    state = state_manager.get_current_state()
    context = self._build_context(state)
    
    results = []
    for ability in stage_config.abilities:
        try:
            client = self.get_client(ability.server)
            result = await client.execute_ability(ability, context)
            results.append(result)
            
            # Special handling for specific abilities
            if ability.name == "accept_payload":
                logger.info(f"Payload accepted for ticket: {state.ticket_id}")
            elif ability.name == "output_payload":
                final_payload = state_manager.export_final_payload()
                result["final_payload"] = final_payload
                logger.info("Final payload generated")
            
        except MCPClientError as e:
            logger.error(f"MCP error executing {ability.name}: {e}")
            results.append({"error": str(e), "ability": ability.name})
    
    return {"stage": stage_config.name, "results": results, "status": "completed"}

async def _execute_deterministic_stage(self, stage_config, state_manager: StateManager) -> Dict[str, Any]:
    """Execute deterministic stages (sequential ability execution)"""
    state = state_manager.get_current_state()
    context = self._build_context(state)
    
    results = []
    for ability in stage_config.abilities:
        try:
            client = self.get_client(ability.server)
            result = await client.execute_ability(ability, context)
            results.append(result)
            
            # Update state based on ability results
            await self._update_state_from_result(ability, result, state_manager, context)
            
            # Update context for next ability
            context = self._build_context(state_manager.get_current_state())
            
        except MCPClientError as e:
            logger.error(f"MCP error executing {ability.name}: {e}")
            results.append({"error": str(e), "ability": ability.name})
    
    return {"stage": stage_config.name, "results": results, "status": "completed"}

async def _execute_non_deterministic_stage(self, stage_config, state_manager: StateManager) -> Dict[str, Any]:
    """Execute non-deterministic stages (dynamic ability orchestration)"""
    state = state_manager.get_current_state()
    context = self._build_context(state)
    
    results = []
    
    # For DECIDE stage, we need to orchestrate abilities based on runtime conditions
    if stage_config.name == "DECIDE":
        # First, evaluate solutions
        solution_ability = next((a for a in stage_config.abilities if a.name == "solution_evaluation"), None)
        if solution_ability:
            client = self.get_client(solution_ability.server)
            eval_result = await client.execute_ability(solution_ability, context)
            results.append(eval_result)
            
            # Update context with solutions
            solutions = eval_result.get("solutions", [])
            for solution in solutions:
                state_manager.add_solution(solution, solution.get("score", 0))
            
            context = self._build_context(state_manager.get_current_state())
        
        # Then, make escalation decision based on scores
        escalation_ability = next((a for a in stage_config.abilities if a.name == "escalation_decision"), None)
        if escalation_ability:
            client = self.get_client(escalation_ability.server)
            escalation_result = await client.execute_ability(escalation_ability, context)
            results.append(escalation_result)
            
            # Update state with escalation decision
            escalation_data = escalation_result.get("escalation_decision", {})
            state_manager.set_escalation(
                escalation_data.get("escalation_required", False),
                escalation_data.get("reason", "")
            )
        
        # Finally, update payload
        update_ability = next((a for a in stage_config.abilities if a.name == "update_payload"), None)
        if update_ability:
            client = self.get_client(update_ability.server)
            update_result = await client.execute_ability(update_ability, context)
            results.append(update_result)
    
    return {"stage": stage_config.name, "results": results, "status": "completed"}

async def _execute_human_stage(self, stage_config, state_manager: StateManager) -> Dict[str, Any]:
    """Execute human interaction stages"""
    state = state_manager.get_current_state()
    context = self._build_context(state)
    
    results = []
    for ability in stage_config.abilities:
        try:
            client = self.get_client(ability.server)
            result = await client.execute_ability(ability, context)
            results.append(result)
            
            # For clarification questions, add to state
            if ability.name == "clarify_question":
                questions = result.get("clarification_questions", [])
                for question in questions:
                    state_manager.add_clarification_question(question)
            
        except MCPClientError as e:
            logger.error(f"MCP error executing {ability.name}: {e}")
            results.append({"error": str(e), "ability": ability.name})
    
    return {"stage": stage_config.name, "results": results, "status": "completed"}

def _build_context(self, state: AgentState) -> Dict[str, Any]:
    """Build execution context from current state"""
    return {
        "customer_name": state.customer_name,
        "email": state.email,
        "query": state.query,
        "priority": state.priority,
        "ticket_id": state.ticket_id,
        "priority_level": state.normalized_fields.get("priority_level", 2),
        "extracted_entities": state.entities,
        "enriched_data": state.enriched_data,
        "kb_results": state.kb_results,
        "solutions": state.solutions,
        "escalation_required": state.escalation_required,
        "human_responses": state.human_responses,
        "generated_response": state.generated_response,
        "actions_taken": state.actions_taken
    }

async def _update_state_from_result(self, ability, result: Dict[str, Any], state_manager: StateManager, context: Dict[str, Any]):
    """Update state manager based on ability execution results"""
    if ability.name == "extract_entities":
        entities = result.get("extracted_entities", {})
        state_manager.update_entities(entities)
    
    elif ability.name == "normalize_fields":
        fields = result.get("normalized_fields", {})
        state_manager.update_normalized_fields(fields)
    
    elif ability.name == "enrich_records":
        data = result.get("enriched_data", {})
        state_manager.add_enriched_data(data)
    
    elif ability.name == "knowledge_base_search":
        kb_results = result.get("kb_results", [])
        for kb_result in kb_results:
            state_manager.add_kb_result(kb_result)
    
    elif ability.name == "response_generation":
        response = result.get("generated_response", "")
        state_manager.set_generated_response(response)
    
    elif ability.name == "extract_answer":
        answer = result.get("extracted_answer", "")
        if answer and answer != "No response provided":
            state_manager.add_human_response(answer)

# Add methods to StageExecutor class
StageExecutor._execute_payload_stage = _execute_payload_stage
StageExecutor._execute_deterministic_stage = _execute_deterministic_stage
StageExecutor._execute_non_deterministic_stage = _execute_non_deterministic_stage
StageExecutor._execute_human_stage = _execute_human_stage
StageExecutor._build_context = _build_context
StageExecutor._update_state_from_result = _update_state_from_result