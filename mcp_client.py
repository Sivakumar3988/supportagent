"""
MCP Client Integration
Handles communication with COMMON and ATLAS MCP servers
"""

from typing import Dict, Any, Optional, List
from enum import Enum
import asyncio
import logging
from datetime import datetime
import json

from config import MCPServer, Ability

class MCPClientError(Exception):
    """Custom exception for MCP client errors"""
    pass

class MCPClient:
    """Base MCP Client for server communication"""
    
    def __init__(self, server_type: MCPServer):
        self.server_type = server_type
        self.connected = False
        self.logger = logging.getLogger(f"MCP_{server_type.value.upper()}")
    
    async def connect(self) -> bool:
        """Connect to MCP server"""
        try:
            # Simulate connection logic
            await asyncio.sleep(0.1)  # Simulate connection delay
            self.connected = True
            self.logger.info(f"Connected to {self.server_type.value} MCP server")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to {self.server_type.value} server: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from MCP server"""
        self.connected = False
        self.logger.info(f"Disconnected from {self.server_type.value} MCP server")
    
    async def execute_ability(self, ability: Ability, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an ability on the MCP server"""
        if not self.connected:
            raise MCPClientError(f"Not connected to {self.server_type.value} server")
        
        if ability.server != self.server_type:
            raise MCPClientError(f"Ability {ability.name} belongs to {ability.server.value}, not {self.server_type.value}")
        
        self.logger.info(f"Executing ability: {ability.name}")
        
        # Route to specific ability handler
        handler_method = f"_handle_{ability.name}"
        if hasattr(self, handler_method):
            result = await getattr(self, handler_method)(context)
        else:
            result = await self._default_handler(ability, context)
        
        self.logger.info(f"Ability {ability.name} completed successfully")
        return result
    
    async def _default_handler(self, ability: Ability, context: Dict[str, Any]) -> Dict[str, Any]:
        """Default handler for abilities"""
        await asyncio.sleep(0.1)  # Simulate processing
        return {
            "ability": ability.name,
            "server": ability.server.value,
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "result": f"Executed {ability.name} successfully"
        }

class CommonMCPClient(MCPClient):
    """MCP Client for COMMON server - handles simple, internal operations"""
    
    def __init__(self):
        super().__init__(MCPServer.COMMON)
    
    async def _handle_accept_payload(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Accept and validate incoming payload"""
        await asyncio.sleep(0.1)
        return {
            "status": "accepted",
            "validated_fields": list(context.keys()),
            "payload_size": len(str(context))
        }
    
    async def _handle_parse_request_text(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse unstructured request text"""
        query = context.get("query", "")
        await asyncio.sleep(0.2)
        
        # Simple text parsing simulation
        parsed_data = {
            "intent": "support_request",
            "sentiment": "neutral",
            "urgency_keywords": [],
            "word_count": len(query.split()) if query else 0
        }
        
        # Check for urgency keywords
        urgency_words = ["urgent", "emergency", "asap", "critical", "immediately"]
        for word in urgency_words:
            if word.lower() in query.lower():
                parsed_data["urgency_keywords"].append(word)
        
        return {
            "parsed_data": parsed_data,
            "original_length": len(query),
            "structured": True
        }
    
    async def _handle_normalize_fields(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize and standardize fields"""
        await asyncio.sleep(0.1)
        
        normalized = {}
        
        # Normalize priority
        priority = context.get("priority", "medium").lower()
        priority_mapping = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        normalized["priority_level"] = priority_mapping.get(priority, 2)
        
        # Normalize email
        email = context.get("email", "").lower().strip()
        normalized["email_normalized"] = email
        
        # Generate standard ticket format
        ticket_id = context.get("ticket_id", "")
        normalized["ticket_format"] = f"CS-{ticket_id}" if ticket_id else "CS-UNKNOWN"
        
        return {
            "normalized_fields": normalized,
            "normalization_rules_applied": len(normalized)
        }
    
    async def _handle_add_flags_calculations(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate flags and risk scores"""
        await asyncio.sleep(0.1)
        
        # Calculate SLA risk based on priority and time
        priority_level = context.get("priority_level", 2)
        sla_risk_score = min(priority_level * 25, 100)
        
        # Calculate complexity score
        query_length = len(context.get("query", ""))
        complexity_score = min(query_length / 10, 100)
        
        flags = {
            "sla_risk_score": sla_risk_score,
            "complexity_score": complexity_score,
            "auto_escalate": sla_risk_score > 75,
            "requires_specialist": complexity_score > 50
        }
        
        return {
            "calculated_flags": flags,
            "risk_assessment": "high" if sla_risk_score > 75 else "medium" if sla_risk_score > 50 else "low"
        }
    
    async def _handle_store_answer(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Store human response in context"""
        await asyncio.sleep(0.1)
        return {
            "stored": True,
            "answer_length": len(context.get("human_response", "")),
            "storage_timestamp": datetime.now().isoformat()
        }
    
    async def _handle_store_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Store retrieved data"""
        await asyncio.sleep(0.1)
        return {
            "stored": True,
            "data_points": len(context.get("kb_results", [])),
            "storage_timestamp": datetime.now().isoformat()
        }
    
    async def _handle_solution_evaluation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate and score potential solutions"""
        await asyncio.sleep(0.3)
        
        kb_results = context.get("kb_results", [])
        solutions = []
        
        for i, result in enumerate(kb_results[:3]):  # Evaluate top 3 results
            # Simulate scoring based on relevance and completeness
            base_score = 60 + (i * 5)  # Base score decreases for lower-ranked results
            
            # Boost score based on context matching
            query = context.get("query", "").lower()
            title = result.get("title", "").lower()
            
            relevance_boost = 0
            if any(word in title for word in query.split()):
                relevance_boost = 20
            
            final_score = min(base_score + relevance_boost, 100)
            
            solutions.append({
                "id": f"sol_{i+1}",
                "title": result.get("title", f"Solution {i+1}"),
                "score": final_score,
                "confidence": final_score / 100,
                "source": "knowledge_base"
            })
        
        return {
            "solutions": solutions,
            "best_score": max([s["score"] for s in solutions]) if solutions else 0,
            "evaluation_method": "relevance_based"
        }
    
    async def _handle_update_payload(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Update payload with decision outcomes"""
        await asyncio.sleep(0.1)
        return {
            "updated": True,
            "decision_recorded": True,
            "update_timestamp": datetime.now().isoformat()
        }
    
    async def _handle_response_generation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate customer response"""
        await asyncio.sleep(0.2)
        
        customer_name = context.get("customer_name", "Customer")
        solutions = context.get("solutions", [])
        
        if solutions and solutions[0].get("score", 0) >= 90:
            response = f"Dear {customer_name}, I've found a solution to your inquiry. Based on our knowledge base, here's how we can help you resolve this issue."
        elif context.get("escalation_required", False):
            response = f"Dear {customer_name}, Thank you for contacting us. Your request has been forwarded to our specialist team who will get back to you within 24 hours."
        else:
            response = f"Dear {customer_name}, Thank you for your inquiry. We're currently reviewing your request and will provide a detailed response soon."
        
        return {
            "generated_response": response,
            "response_type": "automated",
            "word_count": len(response.split())
        }
    
    async def _handle_output_payload(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Output final structured payload"""
        await asyncio.sleep(0.1)
        return {
            "output_generated": True,
            "payload_complete": True,
            "timestamp": datetime.now().isoformat()
        }

class AtlasMCPClient(MCPClient):
    """MCP Client for ATLAS server - handles external system interactions"""
    
    def __init__(self):
        super().__init__(MCPServer.ATLAS)
    
    async def _handle_extract_entities(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract entities using external NLP services"""
        await asyncio.sleep(0.5)  # Simulate external API call
        
        query = context.get("query", "")
        
        # Simulate entity extraction
        entities = {
            "products": [],
            "account_numbers": [],
            "dates": [],
            "locations": []
        }
        
        # Simple entity extraction simulation
        words = query.lower().split()
        
        # Look for common product mentions
        products = ["order", "account", "payment", "subscription", "service"]
        entities["products"] = [word for word in words if word in products]
        
        # Look for potential account numbers (numeric patterns)
        import re
        account_pattern = r'\b\d{6,}\b'
        entities["account_numbers"] = re.findall(account_pattern, query)
        
        return {
            "extracted_entities": entities,
            "confidence": 0.85,
            "extraction_method": "external_nlp"
        }
    
    async def _handle_enrich_records(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich records with historical and SLA data"""
        await asyncio.sleep(0.3)  # Simulate database lookup
        
        customer_email = context.get("email", "")
        priority_level = context.get("priority_level", 2)
        
        # Simulate customer history lookup
        enriched_data = {
            "customer_tier": "standard",
            "previous_tickets": 3,
            "avg_resolution_time": "24h",
            "sla_target": "48h" if priority_level < 3 else "24h",
            "account_status": "active",
            "last_contact": "2024-01-15"
        }
        
        return {
            "enriched_data": enriched_data,
            "data_sources": ["customer_db", "ticket_history", "sla_matrix"],
            "enrichment_confidence": 0.95
        }
    
    async def _handle_clarify_question(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate clarification questions"""
        await asyncio.sleep(0.2)
        
        entities = context.get("extracted_entities", {})
        query = context.get("query", "")
        
        questions = []
        
        # Generate questions based on missing information
        if not entities.get("account_numbers"):
            questions.append("Could you please provide your account number?")
        
        if "order" in query.lower() and not any(char.isdigit() for char in query):
            questions.append("What is your order number?")
        
        if not questions:
            questions.append("Could you provide more details about your specific issue?")
        
        return {
            "clarification_questions": questions,
            "question_count": len(questions),
            "requires_human_input": True
        }
    
    async def _handle_extract_answer(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and process human response"""
        await asyncio.sleep(0.2)
        
        # Simulate waiting for human response
        human_response = context.get("human_response", "No response provided")
        
        return {
            "extracted_answer": human_response,
            "answer_processed": True,
            "contains_useful_info": len(human_response) > 10
        }
    
    async def _handle_knowledge_base_search(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Search external knowledge base"""
        await asyncio.sleep(0.4)  # Simulate KB search
        
        query = context.get("query", "")
        entities = context.get("extracted_entities", {})
        
        # Simulate KB search results
        kb_results = [
            {
                "id": "kb_001",
                "title": "How to track your order status",
                "content": "You can track your order by logging into your account...",
                "relevance": 0.92,
                "category": "orders"
            },
            {
                "id": "kb_002", 
                "title": "Resolving payment issues",
                "content": "If you're experiencing payment problems...",
                "relevance": 0.78,
                "category": "payments"
            },
            {
                "id": "kb_003",
                "title": "Account access troubleshooting",
                "content": "For account access issues, please try...",
                "relevance": 0.65,
                "category": "account"
            }
        ]
        
        return {
            "kb_results": kb_results,
            "total_results": len(kb_results),
            "search_method": "semantic_search"
        }
    
    async def _handle_escalation_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make escalation decision based on solution scores"""
        await asyncio.sleep(0.2)
        
        solutions = context.get("solutions", [])
        best_score = max([s.get("score", 0) for s in solutions]) if solutions else 0
        
        escalate = best_score < 90
        
        escalation_data = {
            "escalation_required": escalate,
            "reason": f"Best solution score ({best_score}) below threshold (90)" if escalate else "Sufficient solution found",
            "assigned_to": "specialist_team" if escalate else "automated_system",
            "priority": "high" if best_score < 70 else "medium"
        }
        
        return {
            "escalation_decision": escalation_data,
            "decision_confidence": 0.9,
            "threshold_used": 90
        }
    
    async def _handle_update_ticket(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Update ticket in external system"""
        await asyncio.sleep(0.3)  # Simulate API call
        
        ticket_id = context.get("ticket_id", "")
        escalation_required = context.get("escalation_required", False)
        
        update_data = {
            "ticket_id": ticket_id,
            "status": "escalated" if escalation_required else "in_progress",
            "last_updated": datetime.now().isoformat(),
            "updated_by": "langie_agent"
        }
        
        return {
            "ticket_updated": True,
            "update_data": update_data,
            "external_system": "crm_system"
        }
    
    async def _handle_close_ticket(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Close ticket in external system"""
        await asyncio.sleep(0.2)
        
        ticket_id = context.get("ticket_id", "")
        
        return {
            "ticket_closed": True,
            "ticket_id": ticket_id,
            "closure_timestamp": datetime.now().isoformat(),
            "resolution_method": "automated"
        }
    
    async def _handle_execute_api_calls(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute external API calls"""
        await asyncio.sleep(0.4)  # Simulate API calls
        
        actions = context.get("actions_taken", [])
        api_calls = []
        
        # Simulate different API calls based on context
        if context.get("escalation_required"):
            api_calls.append({
                "api": "notification_service",
                "action": "notify_specialist_team",
                "status": "success"
            })
        
        api_calls.append({
            "api": "crm_system",
            "action": "update_customer_record",
            "status": "success"
        })
        
        return {
            "api_calls_executed": api_calls,
            "total_calls": len(api_calls),
            "all_successful": True
        }
    
    async def _handle_trigger_notifications(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger customer notifications"""
        await asyncio.sleep(0.3)
        
        customer_email = context.get("email", "")
        generated_response = context.get("generated_response", "")
        
        notifications = [
            {
                "type": "email",
                "recipient": customer_email,
                "subject": f"Re: Your Support Request {context.get('ticket_id', '')}",
                "status": "sent",
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        # Add SMS notification for high priority
        if context.get("priority_level", 0) > 3:
            notifications.append({
                "type": "sms",
                "recipient": "customer_phone",
                "message": "Your support request has been received and is being processed.",
                "status": "sent",
                "timestamp": datetime.now().isoformat()
            })
        
        return {
            "notifications_sent": notifications,
            "total_notifications": len(notifications),
            "delivery_status": "all_sent"
        }