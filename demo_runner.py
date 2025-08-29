"""
Demo Runner for Langie Agent
Demonstrates end-to-end customer support workflow execution
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any

from langgraph_agent import LangieAgent
from config import AGENT_CONFIG

# Configure logging for demo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LangieDemo:
    """Demo runner for Langie Agent"""
    
    def __init__(self):
        self.agent = LangieAgent()
        
    async def run_demo(self, sample_input: Dict[str, Any]) -> Dict[str, Any]:
        """Run complete demo workflow"""
        print("\n" + "="*80)
        print("🧩 LANGIE AGENT DEMO - Customer Support Workflow")
        print("="*80)
        
        # Display agent info
        agent_info = self.agent.get_agent_info()
        print(f"\n📋 Agent: {agent_info['name']} v{agent_info['version']}")
        print(f"🎭 Personality: {agent_info['personality']}")
        print(f"🎯 Capabilities: {agent_info['capabilities']['stages']} stages")
        
        # Display input
        print(f"\n📥 INPUT PAYLOAD:")
        print("-" * 40)
        for key, value in sample_input.items():
            print(f"  {key}: {value}")
        
        print(f"\n🚀 Starting workflow execution...")
        print("-" * 80)
        
        # Execute workflow
        start_time = datetime.now()
        result = await self.agent.process_request(sample_input)
        end_time = datetime.now()
        
        # Display results
        print(f"\n✅ WORKFLOW COMPLETED")
        print(f"⏱️  Processing time: {end_time - start_time}")
        print("-" * 80)
        
        # Display final payload
        if "final_payload" in result:
            self._display_final_payload(result["final_payload"])
        
        # Display processing logs
        self._display_processing_logs(result)
        
        return result
    
    def _display_final_payload(self, final_payload: Dict[str, Any]):
        """Display structured final payload"""
        print(f"\n📤 FINAL STRUCTURED PAYLOAD:")
        print("-" * 40)
        
        # Input summary
        input_data = final_payload.get("input", {})
        print(f"📨 Customer: {input_data.get('customer_name')} ({input_data.get('email')})")
        print(f"🎫 Ticket: {input_data.get('ticket_id')} - Priority: {input_data.get('priority')}")
        print(f"❓ Query: {input_data.get('query')}")
        
        # Processing summary
        processing = final_payload.get("processing", {})
        print(f"\n🔄 Processing Summary:")
        print(f"  📊 Stages completed: {len(processing.get('stages_completed', []))}")
        print(f"  🧠 Entities extracted: {len(processing.get('entities_extracted', {}))}")
        print(f"  📚 Knowledge base results: {processing.get('knowledge_base_results', 0)}")
        print(f"  💡 Solutions evaluated: {processing.get('solutions_evaluated', 0)}")
        
        # Decision summary
        decisions = final_payload.get("decisions", {})
        print(f"\n⚖️  Decision Summary:")
        print(f"  🚨 Escalation required: {decisions.get('escalation_required', False)}")
        if decisions.get('escalation_reason'):
            print(f"  📝 Escalation reason: {decisions.get('escalation_reason')}")
        print(f"  📊 Best solution score: {decisions.get('best_solution_score', 0)}")
        
        # Output summary
        output = final_payload.get("output", {})
        print(f"\n📋 Output Summary:")
        print(f"  💬 Response generated: {'Yes' if output.get('generated_response') else 'No'}")
        print(f"  🎬 Actions executed: {len(output.get('actions_executed', []))}")
        print(f"  🏁 Final status: {output.get('final_status', 'unknown')}")
        
        if output.get('generated_response'):
            print(f"\n💬 Generated Response:")
            print(f"  \"{output.get('generated_response')}\"")
    
    def _display_processing_logs(self, result: Dict[str, Any]):
        """Display processing logs"""
        final_payload = result.get("final_payload", {})
        logs = final_payload.get("metadata", {}).get("processing_log", [])
        
        if logs:
            print(f"\n📋 PROCESSING LOG:")
            print("-" * 40)
            
            stage_summary = {}
            for log in logs:
                stage = log.get("stage", "unknown")
                event_type = log.get("event_type", "unknown")
                
                if stage not in stage_summary:
                    stage_summary[stage] = []
                stage_summary[stage].append(event_type)
            
            for stage, events in stage_summary.items():
                print(f"  🎯 {stage}: {len(events)} events")
                for event in events[:3]:  # Show first 3 events per stage
                    print(f"    • {event}")
                if len(events) > 3:
                    print(f"    ... and {len(events) - 3} more")
    
    async def run_multiple_scenarios(self):
        """Run multiple demo scenarios"""
        scenarios = [
            {
                "name": "Order Status Inquiry",
                "input": {
                    "customer_name": "John Doe",
                    "email": "john.doe@email.com",
                    "query": "I need to check the status of my order #12345. It was supposed to arrive yesterday.",
                    "priority": "medium",
                    "ticket_id": "T001"
                }
            },
            {
                "name": "Payment Issue - High Priority",
                "input": {
                    "customer_name": "Sarah Johnson", 
                    "email": "sarah.j@company.com",
                    "query": "My payment failed but I was charged twice. This is urgent!",
                    "priority": "high",
                    "ticket_id": "T002"
                }
            },
            {
                "name": "Account Access Problem",
                "input": {
                    "customer_name": "Mike Chen",
                    "email": "mike.chen@example.org", 
                    "query": "I can't log into my account and I forgot my password",
                    "priority": "low",
                    "ticket_id": "T003"
                }
            }
        ]
        
        results = {}
        
        for scenario in scenarios:
            print(f"\n{'='*60}")
            print(f"📋 SCENARIO: {scenario['name']}")
            print(f"{'='*60}")
            
            result = await self.run_demo(scenario["input"])
            results[scenario["name"]] = result
            
            # Small delay between scenarios
            await asyncio.sleep(1)
        
        # Summary of all scenarios
        print(f"\n{'='*80}")
        print("📊 DEMO SUMMARY - All Scenarios")
        print(f"{'='*80}")
        
        for name, result in results.items():
            final_payload = result.get("final_payload", {})
            decisions = final_payload.get("decisions", {})
            output = final_payload.get("output", {})
            
            print(f"\n📋 {name}:")
            print(f"  🎯 Status: {output.get('final_status', 'unknown')}")
            print(f"  🚨 Escalated: {decisions.get('escalation_required', False)}")
            print(f"  📊 Best Score: {decisions.get('best_solution_score', 0)}")
        
        return results

# Sample test data
SAMPLE_INPUTS = {
    "basic": {
        "customer_name": "Alice Smith",
        "email": "alice.smith@email.com", 
        "query": "My recent order hasn't arrived yet and I need it for tomorrow's meeting",
        "priority": "high",
        "ticket_id": "CS-2024-001"
    },
    "complex": {
        "customer_name": "Bob Wilson",
        "email": "bob.wilson@company.com",
        "query": "I'm having multiple issues: my subscription was charged twice, I can't access my account, and my recent order shows as delivered but I never received it. This is very frustrating!",
        "priority": "critical", 
        "ticket_id": "CS-2024-002"
    },
    "simple": {
        "customer_name": "Emma Davis",
        "email": "emma.d@example.com",
        "query": "How do I update my billing address?",
        "priority": "low",
        "ticket_id": "CS-2024-003"
    }
}

async def main():
    """Main demo function"""
    print("🚀 Initializing Langie Agent Demo...")
    
    demo = LangieDemo()
    
    # Run single demo
    print("\n" + "="*80) 
    print("🎯 SINGLE SCENARIO DEMO")
    print("="*80)
    
    result = await demo.run_demo(SAMPLE_INPUTS["basic"])
    
    # Option to run multiple scenarios
    print(f"\n" + "="*80)
    print("❓ Would you like to run multiple scenarios? (This is automated)")
    print("="*80)
    
    # Automatically run multiple scenarios for complete demo
    await demo.run_multiple_scenarios()
    
    print(f"\n🎉 Demo completed successfully!")
    print(f"📋 Check the logs above for detailed workflow execution")

if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())