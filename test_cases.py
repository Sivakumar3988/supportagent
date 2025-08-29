"""
Comprehensive Test Cases for Langie Agent
Unit tests, integration tests, and scenario-based testing
"""

import pytest
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List

from langgraph_agent import LangieAgent
from state_manager import StateManager
from config import STAGES, StageMode
from mcp_client import CommonMCPClient, AtlasMCPClient

class TestLangieAgent:
    """Test suite for Langie Agent"""
    
    @pytest.fixture
    async def agent(self):
        """Create agent instance for testing"""
        return LangieAgent()
    
    @pytest.fixture
    def sample_input(self):
        """Sample input data for testing"""
        return {
            "customer_name": "Test Customer",
            "email": "test@example.com",
            "query": "I need help with my order",
            "priority": "medium",
            "ticket_id": "TEST-001"
        }
    
    # Basic functionality tests
    
    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly"""
        assert agent.name == "Langie"
        assert agent.graph is not None
        assert agent.state_manager is not None
        
        info = agent.get_agent_info()
        assert info["capabilities"]["stages"] == 11
        assert "deterministic_stages" in info["capabilities"]
        assert "non_deterministic_stages" in info["capabilities"]
    
    async def test_state_initialization(self, agent, sample_input):
        """Test state initialization with input data"""
        agent.state_manager.initialize_state(sample_input)
        state = agent.state_manager.get_current_state()
        
        assert state.customer_name == sample_input["customer_name"]
        assert state.email == sample_input["email"]
        assert state.query == sample_input["query"]
        assert state.priority == sample_input["priority"]
        assert state.ticket_id == sample_input["ticket_id"]
    
    async def test_full_workflow_execution(self, agent, sample_input):
        """Test complete workflow execution"""
        result = await agent.process_request(sample_input)
        
        assert "final_payload" in result
        final_payload = result["final_payload"]
        
        # Check input preservation
        assert final_payload["input"]["customer_name"] == sample_input["customer_name"]
        
        # Check processing occurred
        assert "processing" in final_payload
        assert len(final_payload["processing"]["stages_completed"]) > 0
        
        # Check decisions were made
        assert "decisions" in final_payload
        assert "escalation_required" in final_payload["decisions"]
        
        # Check output generated
        assert "output" in final_payload
        assert "final_status" in final_payload["output"]

class TestScenarios:
    """Scenario-based testing"""
    
    def __init__(self):
        self.test_scenarios = self._load_test_scenarios()
    
    def _load_test_scenarios(self) -> List[Dict[str, Any]]:
        """Load comprehensive test scenarios"""
        return [
            {
                "name": "Simple Order Inquiry",
                "category": "order_management",
                "expected_escalation": False,
                "expected_stages": 11,
                "input": {
                    "customer_name": "John Smith",
                    "email": "john.smith@email.com",
                    "query": "Where is my order? Order number: ORD123456",
                    "priority": "low",
                    "ticket_id": "SC-ORDER-001"
                },
                "assertions": {
                    "should_find_entities": True,
                    "should_search_kb": True,
                    "min_solution_score": 70
                }
            },
            {
                "name": "Payment Dispute - High Priority",
                "category": "billing",
                "expected_escalation": True,
                "expected_stages": 11,
                "input": {
                    "customer_name": "Sarah Johnson",
                    "email": "sarah.j@business.com",
                    "query": "I was charged twice for subscription #SUB789. Need immediate refund of $99.99!",
                    "priority": "high",
                    "ticket_id": "SC-BILLING-002"
                },
                "assertions": {
                    "should_find_entities": True,
                    "should_escalate": True,
                    "should_notify_customer": True
                }
            },
            {
                "name": "Account Lockout - Critical",
                "category": "security",
                "expected_escalation": True,
                "expected_stages": 11,
                "input": {
                    "customer_name": "Michael Chen",
                    "email": "michael.chen@corp.com",
                    "query": "Account locked after failed login attempts. Cannot access business dashboard for 24 hours. Account: BIZ-ACC-456",
                    "priority": "critical",
                    "ticket_id": "SC-SECURITY-003"
                },
                "assertions": {
                    "should_find_entities": True,
                    "should_escalate": True,
                    "should_generate_urgent_response": True
                }
            },
            {
                "name": "Product Information Request",
                "category": "general_inquiry",
                "expected_escalation": False,
                "expected_stages": 11,
                "input": {
                    "customer_name": "Emma Wilson",
                    "email": "emma.wilson@gmail.com",
                    "query": "What are the features of your premium plan? Is there a student discount?",
                    "priority": "low",
                    "ticket_id": "SC-INFO-004"
                },
                "assertions": {
                    "should_search_kb": True,
                    "should_generate_informative_response": True,
                    "min_solution_score": 85
                }
            },
            {
                "name": "Complex Multi-Issue Case",
                "category": "complex",
                "expected_escalation": True,
                "expected_stages": 11,
                "input": {
                    "customer_name": "Robert Garcia",
                    "email": "robert.garcia@enterprise.org",
                    "query": "Multiple problems: 1) Order #ORD999 wrong items delivered 2) Cannot process return 3) Charged for expedited shipping but received standard 4) Account shows incorrect order history. Need manager involvement.",
                    "priority": "high",
                    "ticket_id": "SC-COMPLEX-005"
                },
                "assertions": {
                    "should_find_multiple_entities": True,
                    "should_escalate": True,
                    "should_flag_complexity": True
                }
            },
            {
                "name": "Incomplete Information Case",
                "category": "clarification_needed",
                "expected_escalation": False,
                "expected_stages": 11,
                "input": {
                    "customer_name": "Lisa Anderson",
                    "email": "lisa.a@email.com",
                    "query": "My thing doesn't work properly",
                    "priority": "medium",
                    "ticket_id": "SC-UNCLEAR-006"
                },
                "assertions": {
                    "should_ask_clarification": True,
                    "should_generate_questions": True
                }
            }
        ]
    
    async def run_scenario_test(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single scenario test"""
        agent = LangieAgent()
        
        print(f"\n🧪 Testing Scenario: {scenario['name']}")
        print(f"📋 Category: {scenario['category']}")
        print(f"🎯 Expected Escalation: {scenario['expected_escalation']}")
        
        # Execute workflow
        start_time = datetime.now()
        result = await agent.process_request(scenario["input"])
        end_time = datetime.now()
        
        execution_time = (end_time - start_time).total_seconds()
        
        # Run assertions
        test_results = self._run_assertions(scenario, result)
        
        return {
            "scenario_name": scenario["name"],
            "category": scenario["category"],
            "execution_time": execution_time,
            "result": result,
            "test_results": test_results,
            "passed": all(test_results.values())
        }
    
    def _run_assertions(self, scenario: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, bool]:
        """Run assertions for a scenario"""
        assertions = scenario.get("assertions", {})
        final_payload = result.get("final_payload", {})
        
        test_results = {}
        
        # Check if entities were found
        if assertions.get("should_find_entities"):
            entities = final_payload.get("processing", {}).get("entities_extracted", {})
            test_results["entities_found"] = bool(entities)
        
        # Check escalation decision
        if assertions.get("should_escalate"):
            escalated = final_payload.get("decisions", {}).get("escalation_required", False)
            test_results["escalation_correct"] = escalated == scenario["expected_escalation"]
        
        # Check knowledge base search
        if assertions.get("should_search_kb"):
            kb_results = final_payload.get("processing", {}).get("knowledge_base_results", 0)
            test_results["kb_searched"] = kb_results > 0
        
        # Check solution score
        if "min_solution_score" in assertions:
            solution_score = final_payload.get("processing", {}).get("solution_score", 0)
            test_results["solution_score_sufficient"] = solution_score >= assertions["min_solution_score"]
        
        # Check if questions were generated
        if assertions.get("should_generate_questions"):
            questions = final_payload.get("processing", {}).get("generated_questions", [])
            test_results["questions_generated"] = bool(questions)
        
        # Check if complexity was flagged
        if assertions.get("should_flag_complexity"):
            complexity_flag = final_payload.get("decisions", {}).get("complexity_flag", False)
            test_results["complexity_flagged"] = complexity_flag
        
        # Check if customer was notified
        if assertions.get("should_notify_customer"):
            notifications = final_payload.get("processing", {}).get("notifications_sent", [])