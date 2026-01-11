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
    
    # Workflow status: 'PROCESSING', 'ESCALATED', 'COMPLETED', 'APPROVED'
    workflow_status: str
    
    # Auditor approval status for Paymaster trigger
    auditor_status: Optional[str]
    
    # MongoDB context retrieved from vector search
    context_data: Optional[List[Dict[str, Any]]]
    
    # Gemini's analysis and recommendation
    analysis: Optional[str]
    
    # Final recommendation
    recommendation: Optional[str]
    
    # Transaction hash from Coinbase AgentKit
    tx_hash: Optional[str]


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
    print("[SCOUT] Detecting Infrastructure Alerts")
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
        
        print(f"[OK] Loaded {len(alerts)} alerts from mock_alerts.json")
        
        # For demo, process the first alert
        # In production, this would track which alerts have been processed
        if alerts:
            current_alert = alerts[0]
            print(f"\n[INFO] Processing Alert: {current_alert['alert_id']}")
            print(f"   Severity: {current_alert['severity'].upper()}")
            print(f"   Resource: {current_alert['resource_name']}")
            print(f"   Type: {current_alert['alert_type']}")
            print(f"   Message: {current_alert['message']}")
            
            # Update state
            state['server_info'] = current_alert
            state['workflow_status'] = 'PROCESSING'
            state['audit_log'].append(f"[{datetime.now(UTC).isoformat()}] Scout: Alert {current_alert['alert_id']} detected")
            state['audit_log'].append(f"[{datetime.now(UTC).isoformat()}] Scout: Resource '{current_alert['resource_name']}' flagged as {current_alert['alert_type']}")
            
            print(f"\n[OK] Scout initialized workflow for {current_alert['alert_id']}")
        else:
            print("[WARNING] No alerts found in mock data")
            state['workflow_status'] = 'COMPLETED'
            state['audit_log'].append(f"[{datetime.now(UTC).isoformat()}] Scout: No alerts to process")
    
    except Exception as e:
        print(f"[FAIL] Error loading alerts: {str(e)}")
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
    print("[AUDIT] AUDITOR NODE - Analyzing Alert with AI")
    print("="*70)
    
    if not state.get('server_info'):
        print("[WARNING] No server info to audit")
        state['workflow_status'] = 'ESCALATED'
        return state
    
    alert = state['server_info']
    resource_name = alert.get('resource_name', '')
    alert_message = alert.get('message', '')
    
    try:
        # Step 1: Query MongoDB for context using vector search
        print(f"\n[1] Searching infrastructure knowledge for: '{resource_name}'")
        db = FinOpsDB()
        
        # Construct a rich query combining resource name and alert context
        search_query = f"{resource_name} {alert_message}"
        results = db.search_infra_context(search_query, limit=3)
        
        if not results:
            print("[WARNING] No context found in MongoDB")
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
        
        print(f"[OK] Found {len(results)} matching documents")
        print(f"   Highest confidence score: {max_score:.4f}")
        
        # Display top match
        top_match = results[0]
        print(f"\n   Top Match: {top_match.get('metadata', {}).get('name', 'Unknown')}")
        print(f"   Priority: {top_match.get('priority', 'N/A')}")
        print(f"   Cost: ${top_match.get('hourly_cost', 0):.2f}/hr")
        
        # Step 2: Check confidence threshold (0.85)
        print(f"\n[2] Checking confidence threshold (required: 0.85)")
        if max_score < 0.85:
            print(f"   [WARNING] THRESHOLD NOT MET: {max_score:.4f} < 0.85")
            print(f"   → Status: ESCALATED")
            state['workflow_status'] = 'ESCALATED'
            state['audit_log'].append(
                f"[{datetime.now(UTC).isoformat()}] Auditor: ESCALATED - "
                f"Confidence {max_score:.4f} below threshold 0.85"
            )
            db.close()
            return state
        
        print(f"   [OK] THRESHOLD MET: {max_score:.4f} >= 0.85")
        
        # Step 3: Use Gemini to analyze the alert with context
        print(f"\n[3] Analyzing with Google Gemini...")
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
        
        print("[OK] Gemini analysis completed")
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
            state['auditor_status'] = "APPROVED"  # Trigger paymaster for decommission
        elif "optimize" in analysis.lower():
            state['recommendation'] = "OPTIMIZE"
            state['auditor_status'] = "REVIEW"
        elif "monitor" in analysis.lower():
            state['recommendation'] = "MONITOR"
            state['auditor_status'] = "REVIEW"
        else:
            state['recommendation'] = "REVIEW"
            state['auditor_status'] = "REVIEW"
        
        db.close()
        
    except Exception as e:
        print(f"\n[FAIL] Error in Auditor: {str(e)}")
        state['workflow_status'] = 'ESCALATED'
        state['audit_log'].append(f"[{datetime.now(UTC).isoformat()}] Auditor: ERROR - {str(e)}")
    
    return state


# ============================================================================
# PAYMASTER NODE
# ============================================================================

def paymaster_node(state: AgentState) -> AgentState:
    """
    Paymaster Node: Issues bounty payments using Coinbase AgentKit.
    
    Responsibilities:
    - Verify auditor_status is 'APPROVED'
    - Extract developer_wallet from context_data
    - Calculate bounty amount based on resource cost
    - Execute ETH transfer on Base Sepolia
    - Save tx_hash to MongoDB reasoning_logs
    """
    print("\n" + "="*70)
    print("[PAYMASTER] Issuing Bounty Payment")
    print("="*70)
    
    # Check if paymaster should trigger
    if state.get('auditor_status') != 'APPROVED':
        print(f"[WARNING] Paymaster skipped: Auditor status is '{state.get('auditor_status', 'UNKNOWN')}'")
        state['audit_log'].append(
            f"[{datetime.now(UTC).isoformat()}] Paymaster: Skipped - Not approved"
        )
        return state
    
    try:
        # Import agent_kit
        from utils.agent_kit import issue_bounty
        
        # Extract recipient wallet from context data
        context_data = state.get('context_data', [])
        if not context_data:
            print("[WARNING] No context data available for wallet extraction")
            state['audit_log'].append(
                f"[{datetime.now(UTC).isoformat()}] Paymaster: Failed - No context data"
            )
            return state
        
        # Get developer wallet from top match
        top_match = context_data[0]
        recipient_wallet = top_match.get('developer_wallet')
        
        if not recipient_wallet:
            print("[WARNING] No developer_wallet found in context data")
            state['audit_log'].append(
                f"[{datetime.now(UTC).isoformat()}] Paymaster: Failed - No wallet address"
            )
            return state
        
        # Calculate bounty amount (e.g., 10% of hourly cost as ETH)
        hourly_cost = top_match.get('hourly_cost', 0)
        bounty_amount = round(hourly_cost * 0.001, 6)  # Small amount for demo
        
        # Set minimum and maximum bounty (max 0.0001 ETH per transaction)
        if bounty_amount < 0.00001:
            bounty_amount = 0.00001
        if bounty_amount > 0.0001:
            bounty_amount = 0.0001
        
        print(f"\n[INFO] Payment Details:")
        print(f"   Recipient: {recipient_wallet}")
        print(f"   Amount: {bounty_amount} ETH")
        print(f"   Resource: {top_match.get('metadata', {}).get('name', 'Unknown')}")
        print(f"   Reason: Decommission bounty")
        
        # Execute payment
        result = issue_bounty(bounty_amount, recipient_wallet)
        
        if result.get('success'):
            tx_hash = result.get('tx_hash')
            tx_link = result.get('tx_link')
            
            print(f"\n[OK] Bounty payment successful!")
            print(f"   TX Hash: {tx_hash}")
            print(f"   TX Link: {tx_link}")
            
            state['tx_hash'] = tx_hash
            state['audit_log'].append(
                f"[{datetime.now(UTC).isoformat()}] Paymaster: Payment successful - "
                f"{bounty_amount} ETH to {recipient_wallet[:10]}... (TX: {tx_hash[:10]}...)"
            )
            
            # Save to MongoDB
            print(f"\n[SAVE] Saving transaction to reasoning_logs...")
            db = FinOpsDB()
            alert_id = state.get('server_info', {}).get('alert_id', 'UNKNOWN')
            
            log_id = db.save_reasoning_log(
                alert_id=alert_id,
                workflow_status='APPROVED',
                recommendation=state.get('recommendation', 'DECOMMISSION'),
                confidence_score=state.get('confidence_score', 0.0),
                tx_hash=tx_hash,
                tx_amount=bounty_amount,
                tx_recipient=recipient_wallet,
                context_data=state.get('context_data'),
                analysis=state.get('analysis'),
                audit_log=state.get('audit_log')
            )
            
            print(f"[OK] Reasoning log saved: {log_id}")
            db.close()
            
        else:
            error = result.get('error', 'Unknown error')
            print(f"\n[FAIL] Bounty payment failed: {error}")
            state['audit_log'].append(
                f"[{datetime.now(UTC).isoformat()}] Paymaster: Payment failed - {error}"
            )
    
    except Exception as e:
        print(f"\n[FAIL] Error in Paymaster: {str(e)}")
        state['audit_log'].append(
            f"[{datetime.now(UTC).isoformat()}] Paymaster: ERROR - {str(e)}"
        )
        import traceback
        traceback.print_exc()
    
    return state


# ============================================================================
# WORKFLOW ROUTER
# ============================================================================

def route_workflow(state: AgentState) -> str:
    """
    Determine next step based on workflow status and auditor approval.
    """
    status = state.get('workflow_status', 'PROCESSING')
    auditor_status = state.get('auditor_status', 'REVIEW')
    
    if status == 'ESCALATED':
        return 'escalate'
    elif status == 'COMPLETED':
        # Check if paymaster should be triggered
        if auditor_status == 'APPROVED':
            return 'paymaster'
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
    print("[ESCALATION] Human Review Required")
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
    print("[COMPLETION] Workflow Finalized")
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
            print("[OK] Using MongoDB persistent checkpointing")
            # Use MongoDBSaver with connection string
            from pymongo import MongoClient
            client = MongoClient(mongodb_uri)
            db = client.get_database()
            checkpointer = MongoDBSaver(db)
        else:
            print("[WARNING] MongoDB URI not found, using in-memory checkpointing")
            checkpointer = MemorySaver()
    else:
        print("[OK] Using in-memory checkpointing")
        checkpointer = MemorySaver()
    
    # Create the state graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("scout", scout_node)
    workflow.add_node("auditor", auditor_node)
    workflow.add_node("paymaster", paymaster_node)
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
            "paymaster": "paymaster",
            "complete": "complete",
            "continue": END
        }
    )
    
    # Paymaster leads to complete
    workflow.add_edge("paymaster", "complete")
    
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
    print("[START] FinOps Multi-Agent System - Core Reasoning Engine")
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
        'recommendation': None,
        'auditor_status': None,
        'tx_hash': None
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
        print("[INFO] AUDIT LOG")
        print("="*70)
        for log_entry in final_state.get('audit_log', []):
            print(log_entry)
        
        print("\n" + "="*70)
        print("[OK] Workflow Execution Complete")
        print("="*70)
        
        return final_state
        
    except Exception as e:
        print(f"\n[FAIL] Workflow execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()
