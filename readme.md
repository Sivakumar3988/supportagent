**Langie Agent - LangGraph Customer Support Workflow**

A sophisticated customer support agent built with LangGraph that orchestrates 11-stage workflows with MCP client integration for automated and human-assisted customer service.

**🎯 Overview**

Langie is a structured and logical LangGraph Agent that processes customer support requests through a comprehensive 11-stage workflow:

INTAKE 📥 - Accept payload

UNDERSTAND 🧠 - Parse request and extract entities

PREPARE 🛠️ - Normalize and enrich data

ASK ❓ - Request clarification

WAIT ⏳ - Process responses

RETRIEVE 📚 - Search knowledge base

DECIDE ⚖️ - Evaluate solutions and escalate

UPDATE 🔄 - Update ticket status

CREATE ✍️ - Generate customer response

DO 🏃 - Execute actions and notifications

COMPLETE ✅ - Output final payload

**🏗️ Architecture**

Core Components

LangGraph Workflow: Orchestrates stage execution with state persistence

MCP Client Integration: Routes abilities to COMMON or ATLAS servers

State Management: Maintains context across all workflow stages

Stage Orchestration: Supports deterministic and non-deterministic execution

**<!-- Workflow Details -->**

Input Schema

json{
    "customer_name": "string",
    "email": "string", 
    "query": "string",
    "priority": "low|medium|high|critical",
    "ticket_id": "string"
}

Sample Output

json{
    "input": { ... },
    "processing": {
        "stages_completed": ["INTAKE", "UNDERSTAND", ...],
        "entities_extracted": { ... },
        "solutions_evaluated": 3
    },
    "decisions": {
        "escalation_required": false,
        "best_solution_score": 95
    },
    "output": {
        "generated_response": "Dear John, I've found a solution...",
        "final_status": "resolved"
    }
}

🧪 Demo Scenarios
The demo includes three scenarios:

Order Status Inquiry (Medium priority)
Payment Issue (High priority)
Account Access (Low priority)

Each demonstrates different workflow paths and escalation decisions.
0
To Execute: streamlit run streamlit_run.py

<img width="1341" height="626" alt="Screenshot 2025-08-30 091739" src="https://github.com/user-attachments/assets/3abbe939-be9a-45c7-bc3a-aa49012d7d0c" />
<img width="1341" height="616" alt="Screenshot 2025-08-30 091825" src="https://github.com/user-attachments/assets/e753817a-a1a5-4ca4-b159-2928181cbfd6" />
<img width="1000" height="524" alt="Screenshot 2025-08-30 091916" src="https://github.com/user-attachments/assets/da7c476f-b11f-412e-8e41-0dbb18bba6b6" />
<img width="993" height="520" alt="Screenshot 2025-08-30 091950" src="https://github.com/user-attachments/assets/219ba4d3-e622-4d63-845f-dd7c4ac6405b" />




