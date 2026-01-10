"""
FinOps Multi-Agent System - Core Reasoning Engine
LangGraph-based workflow with Scout and Auditor nodes
"""

import os
import json
from typing import TypedDict, List, Dict, Any, Optional, Annotated
from datetime import datetime, UTC
from dotenv import load_dotenv

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.mongodb import MongoDBSaver

# Google Gemini
from google import genai

# Local imports
from utils.mongo_client import FinOpsDB

# Load environment variables
load_dotenv()


# ============================================================================
# STATE DEFINITION
# ============================================================================

class AgentState(TypedDict):
    """
    State tracked throughout the LangGraph workflow.
    """
    # Current alert being processed
    server_info: Optional[Dict[str, Any]]
    
    # Audit trail of actions and decisions
    audit_log: List[str]
    
    # Confidence score from vector search (0.0 to 1.0)
    confidence_score: Optional[float]
    
    # Workflow status: 'PROCESSING', 'ESCALATED', 'COMPLETED'
    workflow_status: str
    
    # MongoDB context retrieved from vector search
    context_data: Optional[List[Dict[str, Any]]]
    
    # Gemini's analysis and recommendation
    analysis: Optional[str]
    
    # Final recommendation
    recommendation: Optional[str]


# ============================================================================
# SCOUT NODE
# ============================================================================

def scout_node(state: AgentState) -> AgentState:
    """
    Scout Node: Reads mock alerts from local JSON file.
    
    Responsibilities:
    - Load alerts from mock_alerts.json
    - Select the first unprocessed alert
    - Initialize the workflow state
    """
    print("\n" + "="*70)
    print("🔍 SCOUT NODE - Detecting Infrastructure Alerts")
    print("="*70)
    
    # Load mock alerts
    alerts_path = os.path.join(os.path.dirname(__file__), 'scripts', 'mock_alerts.json')
    
    # Try alternative path if not found
    if not os.path.exists(alerts_path):
        alerts_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'mock_alerts.json')
    
    if not os.path.exists(alerts_path):
        alerts_path = 'scripts/mock_alerts.json'
    
    try:
        with open(alerts_path, 'r') as f:
            alerts = json.load(f)
        
        print(f"✓ Loaded {len(alerts)} alerts from mock_alerts.json")
        
        # For demo, process the first alert
        # In production, this would track which alerts have been processed
        if alerts:
            current_alert = alerts[0]
            print(f"\n📋 Processing Alert: {current_alert['alert_id']}")
            print(f"   Severity: {current_alert['severity'].upper()}")
            print(f"   Resource: {current_alert['resource_name']}")
            print(f"   Type: {current_alert['alert_type']}")
            print(f"   Message: {current_alert['message']}")
            
            # Update state
            state['server_info'] = current_alert
            state['workflow_status'] = 'PROCESSING'
            state['audit_log'].append(f"[{datetime.now(UTC).isoformat()}] Scout: Alert {current_alert['alert_id']} detected")
            state['audit_log'].append(f"[{datetime.now(UTC).isoformat()}] Scout: Resource '{current_alert['resource_name']}' flagged as {current_alert['alert_type']}")
            
            print(f"\n✓ Scout initialized workflow for {current_alert['alert_id']}")
        else:
            print("⚠ No alerts found in mock data")
            state['workflow_status'] = 'COMPLETED'
            state['audit_log'].append(f"[{datetime.now(UTC).isoformat()}] Scout: No alerts to process")
    
    except Exception as e:
        print(f"✗ Error loading alerts: {str(e)}")
        state['workflow_status'] = 'ESCALATED'
        state['audit_log'].append(f"[{datetime.now(UTC).isoformat()}] Scout: Error loading alerts - {str(e)}")
    
    return state


# ============================================================================
# AUDITOR NODE
# ============================================================================

def auditor_node(state: AgentState) -> AgentState:
    """
    Auditor Node: Uses Gemini to compare alert against MongoDB context.
    
    Responsibilities:
    - Query MongoDB Atlas using vector search
    - Check if confidence score meets 0.85 threshold
    - Use Gemini to analyze the alert with retrieved context
    - Set status to 'ESCALATED' if confidence < 0.85
    """
    print("\n" + "="*70)
    print("🔎 AUDITOR NODE - Analyzing Alert with AI")
    print("="*70)
    
    if not state.get('server_info'):
        print("⚠ No server info to audit")
        state['workflow_status'] = 'ESCALATED'
        return state
    
    alert = state['server_info']
    resource_name = alert.get('resource_name', '')
    alert_message = alert.get('message', '')
    
    try:
        # Step 1: Query MongoDB for context using vector search
        print(f"\n1️⃣ Searching infrastructure knowledge for: '{resource_name}'")
        db = FinOpsDB()
        
        # Construct a rich query combining resource name and alert context
        search_query = f"{resource_name} {alert_message}"
        results = db.search_infra_context(search_query, limit=3)
        
        if not results:
            print("⚠ No context found in MongoDB")
            state['confidence_score'] = 0.0
            state['workflow_status'] = 'ESCALATED'
            state['audit_log'].append(f"[{datetime.now(UTC).isoformat()}] Auditor: ESCALATED - No matching context found")
            db.close()
            return state
        
        # Get the highest confidence score
        max_score = max(result.get('score', 0.0) for result in results)
        state['confidence_score'] = max_score
        
        # Convert results to serializable format (remove ObjectId)
        serializable_results = []
        for result in results:
            clean_result = {k: v for k, v in result.items() if k != '_id'}
            serializable_results.append(clean_result)
        
        state['context_data'] = serializable_results
        
        print(f"✓ Found {len(results)} matching documents")
        print(f"   Highest confidence score: {max_score:.4f}")
        
        # Display top match
        top_match = results[0]
        print(f"\n   Top Match: {top_match.get('metadata', {}).get('name', 'Unknown')}")
        print(f"   Priority: {top_match.get('priority', 'N/A')}")
        print(f"   Cost: ${top_match.get('hourly_cost', 0):.2f}/hr")
        
        # Step 2: Check confidence threshold (0.85)
        print(f"\n2️⃣ Checking confidence threshold (required: 0.85)")
        if max_score < 0.85:
            print(f"   ⚠ THRESHOLD NOT MET: {max_score:.4f} < 0.85")
            print(f"   → Status: ESCALATED")
            state['workflow_status'] = 'ESCALATED'
            state['audit_log'].append(
                f"[{datetime.now(UTC).isoformat()}] Auditor: ESCALATED - "
                f"Confidence {max_score:.4f} below threshold 0.85"
            )
            db.close()
            return state
        
        print(f"   ✓ THRESHOLD MET: {max_score:.4f} >= 0.85")
        
        # Step 3: Use Gemini to analyze the alert with context
        print(f"\n3️⃣ Analyzing with Google Gemini...")
        client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
        model_name = 'gemini-2.5-flash'
        
        # Construct prompt with context
        context_text = "\n\n".join([
            f"Resource: {r.get('metadata', {}).get('name', 'Unknown')}\n"
            f"Priority: {r.get('priority', 'N/A')}\n"
            f"Cost: ${r.get('hourly_cost', 0):.2f}/hr\n"
            f"Environment: {r.get('metadata', {}).get('environment', 'N/A')}\n"
            f"Description: {r.get('content', 'N/A')[:200]}..."
            for r in results[:2]
        ])
        
        prompt = f"""You are a FinOps AI assistant analyzing infrastructure alerts.

ALERT DETAILS:
- Alert ID: {alert.get('alert_id')}
- Severity: {alert.get('severity')}
- Resource: {resource_name}
- Type: {alert.get('alert_type')}
- Message: {alert_message}
- Metrics: {json.dumps(alert.get('metrics', {}), indent=2)}

INFRASTRUCTURE CONTEXT (from knowledge base):
{context_text}

CONFIDENCE SCORE: {max_score:.4f}

Please analyze this alert and provide:
1. Is this a legitimate concern or a false positive?
2. What is the risk level (Critical/High/Medium/Low)?
3. Recommended action (e.g., decommission, optimize, monitor, ignore)
4. Rationale for your recommendation

Keep your response concise and actionable."""

        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        analysis = response.text
        
        print("✓ Gemini analysis completed")
        print(f"\n{'-'*70}")
        print("GEMINI ANALYSIS:")
        print(f"{'-'*70}")
        print(analysis)
        print(f"{'-'*70}")
        
        state['analysis'] = analysis
        state['workflow_status'] = 'COMPLETED'
        state['audit_log'].append(
            f"[{datetime.now(UTC).isoformat()}] Auditor: Analysis completed - "
            f"Confidence {max_score:.4f}, Status COMPLETED"
        )
        
        # Extract recommendation (simple parsing)
        if "decommission" in analysis.lower():
            state['recommendation'] = "DECOMMISSION"
        elif "optimize" in analysis.lower():
            state['recommendation'] = "OPTIMIZE"
        elif "monitor" in analysis.lower():
            state['recommendation'] = "MONITOR"
        else:
            state['recommendation'] = "REVIEW"
        
        db.close()
        
    except Exception as e:
        print(f"\n✗ Error in Auditor: {str(e)}")
        state['workflow_status'] = 'ESCALATED'
        state['audit_log'].append(f"[{datetime.now(UTC).isoformat()}] Auditor: ERROR - {str(e)}")
    
    return state


# ============================================================================
# WORKFLOW ROUTER
# ============================================================================

def route_workflow(state: AgentState) -> str:
    """
    Determine next step based on workflow status.
    """
    status = state.get('workflow_status', 'PROCESSING')
    
    if status == 'ESCALATED':
        return 'escalate'
    elif status == 'COMPLETED':
        return 'complete'
    else:
        return 'continue'


# ============================================================================
# TERMINAL NODES
# ============================================================================

def escalate_node(state: AgentState) -> AgentState:
    """
    Handle escalated cases that require human review.
    """
    print("\n" + "="*70)
    print("⚠️  ESCALATION NODE - Human Review Required")
    print("="*70)
    
    alert = state.get('server_info', {})
    print(f"\nAlert {alert.get('alert_id', 'UNKNOWN')} requires human review.")
    print(f"Reason: Confidence score {state.get('confidence_score', 0):.4f} below threshold")
    print(f"\nEscalating to operations team...")
    
    state['audit_log'].append(
        f"[{datetime.now(UTC).isoformat()}] System: Alert escalated to human review"
    )
    
    return state


def complete_node(state: AgentState) -> AgentState:
    """
    Finalize successfully processed alerts.
    """
    print("\n" + "="*70)
    print("✅ COMPLETION NODE - Workflow Finalized")
    print("="*70)
    
    alert = state.get('server_info', {})
    print(f"\nAlert {alert.get('alert_id', 'UNKNOWN')} processed successfully.")
    print(f"Recommendation: {state.get('recommendation', 'REVIEW')}")
    print(f"Confidence Score: {state.get('confidence_score', 0):.4f}")
    
    state['audit_log'].append(
        f"[{datetime.now(UTC).isoformat()}] System: Workflow completed successfully"
    )
    
    return state


# ============================================================================
# GRAPH CONSTRUCTION
# ============================================================================

def create_workflow_graph(use_mongodb_checkpointer: bool = False):
    """
    Create the LangGraph workflow with Scout and Auditor nodes.
    
    Args:
        use_mongodb_checkpointer: If True, use MongoDBSaver for persistent checkpointing
    """
    # Initialize checkpointer
    if use_mongodb_checkpointer:
        mongodb_uri = os.getenv('MONGODB_URI')
        if mongodb_uri:
            print("✓ Using MongoDB persistent checkpointing")
            # Use MongoDBSaver with connection string
            from pymongo import MongoClient
            client = MongoClient(mongodb_uri)
            db = client.get_database()
            checkpointer = MongoDBSaver(db)
        else:
            print("⚠ MongoDB URI not found, using in-memory checkpointing")
            checkpointer = MemorySaver()
    else:
        print("✓ Using in-memory checkpointing")
        checkpointer = MemorySaver()
    
    # Create the state graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("scout", scout_node)
    workflow.add_node("auditor", auditor_node)
    workflow.add_node("escalate", escalate_node)
    workflow.add_node("complete", complete_node)
    
    # Set entry point
    workflow.set_entry_point("scout")
    
    # Add edges
    workflow.add_edge("scout", "auditor")
    
    # Add conditional routing from auditor
    workflow.add_conditional_edges(
        "auditor",
        route_workflow,
        {
            "escalate": "escalate",
            "complete": "complete",
            "continue": END
        }
    )
    
    # Terminal nodes
    workflow.add_edge("escalate", END)
    workflow.add_edge("complete", END)
    
    # Compile with checkpointer
    return workflow.compile(checkpointer=checkpointer)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main execution function.
    """
    print("\n" + "="*70)
    print("🚀 FinOps Multi-Agent System - Core Reasoning Engine")
    print("="*70)
    print("\nInitializing LangGraph workflow...")
    
    # Create workflow graph with MongoDB checkpointing
    graph = create_workflow_graph(use_mongodb_checkpointer=True)
    
    # Initialize state
    initial_state: AgentState = {
        'server_info': None,
        'audit_log': [],
        'confidence_score': None,
        'workflow_status': 'PROCESSING',
        'context_data': None,
        'analysis': None,
        'recommendation': None
    }
    
    # Configuration for checkpointing
    config = {
        "configurable": {
            "thread_id": f"finops-workflow-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}"
        }
    }
    
    print(f"Thread ID: {config['configurable']['thread_id']}")
    
    # Execute workflow
    try:
        final_state = graph.invoke(initial_state, config=config)
        
        # Display audit log
        print("\n" + "="*70)
        print("📋 AUDIT LOG")
        print("="*70)
        for log_entry in final_state.get('audit_log', []):
            print(log_entry)
        
        print("\n" + "="*70)
        print("✓ Workflow Execution Complete")
        print("="*70)
        
        return final_state
        
    except Exception as e:
        print(f"\n✗ Workflow execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()
