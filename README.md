# FinOps Multi-Agent System

**Cerebral Valley 2026** | Arjun Gajula

Intelligent infrastructure cost optimization system using LangGraph multi-agent workflows, MongoDB Atlas vector search, and Google Gemini AI.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Note: cdp-sdk requires Visual C++ Build Tools on Windows
# Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Configure environment
cp .env.example .env  # Add your API keys

# Setup agent wallet (Base Sepolia)
python scripts/setup_agent_wallet.py

# Seed knowledge base
python scripts/seed_data.py

# Run workflow
python main.py
```

## Architecture

### Tech Stack
- **LangGraph**: Multi-agent workflow orchestration with persistent checkpointing
- **MongoDB Atlas**: Vector search (Voyage AI embeddings) + state persistence
- **Google Gemini**: AI-powered infrastructure analysis
- **Voyage AI**: Semantic embeddings (voyage-3.5)
- **Coinbase AgentKit**: Cryptocurrency operations

### Workflow (main.py)

**State**: TypedDict tracking `server_info`, `audit_log`, `confidence_score`, `workflow_status`

**Nodes**:
1. **Scout** → Loads alerts from `scripts/mock_alerts.json`
2. **Auditor** → Vector search + Gemini analysis
   - Threshold: score < 0.85 → ESCALATE (stops workflow)
   - Otherwise: AI recommendation (DECOMMISSION/OPTIMIZE/MONITOR)
3. **Router** → Routes to Escalate/Complete based on status
4. **Terminal Nodes** → Finalize or escalate to human review

**Checkpointing**: MongoDBSaver enables crash recovery with unique thread IDs

### Data Pipeline

```
Mock Alerts → Scout → MongoDB Vector Search (0.85 threshold)
                ↓
         Gemini Analysis → Recommendation → Audit Log
```

## Project Structure

```
cvsf-2026/
├── main.py              # LangGraph workflow engine
├── utils/
│   └── mongo_client.py  # MongoDB + Voyage AI integration
├── agents/              # Specialized AI agents
├── scripts/
│   ├── seed_data.py     # Populate infrastructure knowledge (20 documents)
│   ├── mock_alerts.json # Test scenarios
│   └── test_enhanced_search.py  # Vector search validation
└── requirements.txt
```

## Features

✅ **Strategic Knowledge Base**: 20 infrastructure documents including:
- Red herrings (high-priority with deceptive names)
- High-value targets ($23.33/hr potential savings)
- Semantic variations for robust search

✅ **Vector Search**: Voyage AI embeddings with similarity scoring
✅ **AI Analysis**: Gemini-powered recommendations
✅ **Persistent State**: MongoDB checkpointing for reliability
✅ **Rich Output**: Color-coded tables and audit trails

## Example Execution

```
🔍 Scout: Detected ALT-2026-001 (Legacy GPU Training Cluster)
🔎 Auditor: Vector search score 0.8704 ✓ (>0.85 threshold)
🤖 Gemini: CRITICAL risk → DECOMMISSION ($12.24/hr savings)
✅ Complete: Workflow finalized
```

## Prerequisites

- Python 3.9+
- MongoDB Atlas cluster with vector search index
- API Keys: Google Gemini, Voyage AI, Coinbase CDP

## Configuration

Environment variables in `.env`:
```
MONGODB_URI=mongodb+srv://...
GOOGLE_API_KEY=...
VOYAGE_API_KEY=...
CDP_API_KEY=...
CDP_API_SECRET=...
```

## Testing

```bash
# Test vector search
python scripts/test_enhanced_search.py

# Test MongoDB connection
python utils/mongo_client.py
```