# FinOps Multi-Agent System

**Cerebral Valley 2026** | Arjun Gajula

Intelligent infrastructure cost optimization system using LangGraph multi-agent workflows, MongoDB Atlas vector search, Google Gemini AI, and automated blockchain-based bounty payments via Coinbase AgentKit.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Features](#features)
- [Paymaster Integration](#paymaster-integration)
- [Configuration](#configuration)
- [Testing](#testing)
- [Dashboard](#dashboard)

---

## Quick Start

### Installation

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

# Run real-time dashboard (optional)
python scripts/dashboard.py
```

### 5-Minute Setup for Paymaster

```bash
# 1. Install dependencies
pip install cdp-sdk coinbase-agentkit

# 2. Add to .env file:
CDP_API_KEY=organizations/.../apiKeys/...
CDP_API_SECRET=-----BEGIN EC PRIVATE KEY-----\n...\n-----END EC PRIVATE KEY-----\n

# 3. Run tests
python scripts/test_paymaster.py

# 4. Run full workflow
python main.py
```

---

## Architecture

### Tech Stack

- **LangGraph**: Multi-agent workflow orchestration with persistent checkpointing
- **MongoDB Atlas**: Vector search (Voyage AI embeddings) + state persistence
- **Google Gemini**: AI-powered infrastructure analysis
- **Voyage AI**: Semantic embeddings (voyage-3.5)
- **Coinbase AgentKit**: Cryptocurrency operations on Base Sepolia
- **Rich Library**: Real-time CLI dashboard visualization

### Workflow

```
Scout → Auditor → [Router] → Paymaster → Complete
                     ↓
                  Escalate → END
```

#### Workflow Nodes

1. **Scout** → Loads alerts from `scripts/mock_alerts.json`
2. **Auditor** → Vector search + Gemini analysis
   - Threshold: score < 0.85 → ESCALATE (stops workflow)
   - Otherwise: AI recommendation (DECOMMISSION/OPTIMIZE/MONITOR)
   - Sets `auditor_status` to APPROVED for decommission recommendations
3. **Paymaster** → Issues bounty payments via Coinbase AgentKit
   - Triggers only if `auditor_status == 'APPROVED'`
   - Transfers ETH on Base Sepolia to developer wallet
   - Saves transaction hash to MongoDB reasoning_logs
   - Bounty: hourly_cost * 0.001 (capped at 0.0001 ETH max)
4. **Router** → Routes to Escalate/Paymaster/Complete based on status
5. **Terminal Nodes** → Finalize or escalate to human review

#### State Management

**AgentState Fields:**
- `server_info`: Current alert data
- `audit_log`: Workflow history
- `confidence_score`: Vector search score (0.0-1.0)
- `workflow_status`: PROCESSING/ESCALATED/COMPLETED
- `auditor_status`: APPROVED/REVIEW (triggers Paymaster)
- `context_data`: MongoDB search results
- `analysis`: Gemini AI analysis
- `recommendation`: DECOMMISSION/OPTIMIZE/MONITOR
- `tx_hash`: Transaction hash from payment

**Checkpointing**: MongoDBSaver enables crash recovery with unique thread IDs

### System Flow Diagram

```
┌────────────┐
│   START    │
└─────┬──────┘
      │
┌─────▼──────┐
│   SCOUT    │  Load alerts, initialize state
└─────┬──────┘
      │
┌─────▼──────┐
│  AUDITOR   │  Vector search, Gemini analysis, set status
└─────┬──────┘
      │
      ├─► ESCALATED (confidence < 0.85) ──► ESCALATE ──► END
      │
      ├─► APPROVED (confidence >= 0.85, DECOMMISSION) ──► PAYMASTER
      │                                                      │
      └─► REVIEW (other recommendations) ──────────────────┤
                                                             │
                                                      ┌──────▼──────┐
                                                      │  COMPLETE   │
                                                      └──────┬──────┘
                                                             │
                                                        ┌────▼────┐
                                                        │   END   │
                                                        └─────────┘
```

### Data Pipeline

```
Mock Alerts → Scout → MongoDB Vector Search (0.85 threshold)
                ↓
         Gemini Analysis → Recommendation → Audit Log
                ↓
         Paymaster (if APPROVED) → ETH Transfer → MongoDB
```

---

## Project Structure

```
cvsf-2026/
├── main.py                      # LangGraph workflow engine
├── utils/
│   ├── mongo_client.py          # MongoDB + Voyage AI integration
│   └── agent_kit.py             # Coinbase AgentKit wrapper
├── agents/
│   └── __init__.py              # Specialized AI agents
├── scripts/
│   ├── seed_data.py             # Populate infrastructure knowledge (20 docs)
│   ├── setup_agent_wallet.py   # Setup CDP wallet
│   ├── mock_alerts.json         # Test scenarios
│   ├── test_paymaster.py        # Paymaster integration tests
│   ├── test_enhanced_search.py  # Vector search validation
│   ├── test_search.py           # Basic search tests
│   └── dashboard.py             # Real-time CLI dashboard
├── requirements.txt
├── wallet_data.json             # Agent wallet data
├── .env                         # API keys (not committed)
└── README.md                    # This file
```

---

## Features

### Core Features

✅ **Strategic Knowledge Base**: 20 infrastructure documents including:
- Red herrings (high-priority with deceptive names)
- High-value targets ($23.33/hr potential savings)
- Semantic variations for robust search

✅ **Vector Search**: Voyage AI embeddings with similarity scoring

✅ **AI Analysis**: Gemini-powered recommendations

✅ **Persistent State**: MongoDB checkpointing for reliability

✅ **Automated Payments**: Coinbase AgentKit bounty system
- ETH transfers on Base Sepolia
- Transaction logging in reasoning_logs
- Triggers on approved decommission recommendations
- Configurable bounty amounts (0.00001 - 0.0001 ETH)

✅ **Real-Time Dashboard**: Rich library CLI dashboard
- Live polling of reasoning_logs collection
- Summary panel with total savings and bounties
- Latest activity panel
- Transaction table with color-coded statuses
- 2-second refresh interval

✅ **Rich Output**: Color-coded tables and audit trails

---

## Paymaster Integration

### Overview

The Paymaster integration adds automated bounty payments using **Coinbase AgentKit**. When the Auditor approves a resource for decommission, the Paymaster automatically transfers ETH on Base Sepolia to the developer's wallet.

### Paymaster Trigger Conditions

Paymaster executes only when:
- ✅ `auditor_status == 'APPROVED'`
- ✅ `context_data` contains `developer_wallet`
- ✅ Recommendation is `DECOMMISSION`

### Bounty Calculation

Default: `hourly_cost * 0.001` 
- Minimum: 0.00001 ETH
- Maximum: 0.0001 ETH (user-configured cap)

### Usage Examples

#### Standalone Payment

```python
from utils.agent_kit import issue_bounty

result = issue_bounty(
    amount=0.001,
    recipient_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
)

if result['success']:
    print(f"TX Hash: {result['tx_hash']}")
    print(f"TX Link: {result['tx_link']}")
else:
    print(f"Error: {result['error']}")
```

#### Using PaymasterAgent Class

```python
from utils.agent_kit import PaymasterAgent

# Initialize
agent = PaymasterAgent()
wallet_address = agent.initialize_wallet()

# Check balance
balance = agent.get_wallet_balance()
print(f"Balance: {balance['balance']} ETH")

# Send payment
result = agent.issue_bounty(0.001, "0x742d35...")

# Export wallet for persistence
wallet_data = agent.export_wallet()
```

### MongoDB Storage

Transactions are saved to the `reasoning_logs` collection:

```json
{
  "_id": "677e9c1a2b3c4d5e6f7g8h9i",
  "alert_id": "alert-cpu-high-123",
  "workflow_status": "APPROVED",
  "recommendation": "DECOMMISSION",
  "confidence_score": 0.9234,
  "timestamp": "2026-01-10T12:00:00Z",
  "transaction": {
    "tx_hash": "0xabc123...",
    "amount": 0.0001,
    "recipient": "0x742d35...",
    "network": "base-sepolia",
    "timestamp": "2026-01-10T12:00:30Z"
  },
  "analysis": "...",
  "context_data": [...],
  "audit_log": [...]
}
```

### Configuration Options

#### Customize Bounty Calculation

Edit in [main.py](main.py#L339):
```python
bounty_amount = round(hourly_cost * 0.001, 6)  # Change multiplier
if bounty_amount < 0.00001:
    bounty_amount = 0.00001  # Change minimum
if bounty_amount > 0.0001:
    bounty_amount = 0.0001  # Change maximum
```

#### Change Network

Edit in [utils/agent_kit.py](utils/agent_kit.py#L30):
```python
def initialize_wallet(self, network_id: str = "base-sepolia"):
    # Change to: "base-mainnet", "ethereum", etc.
```

---

## Dashboard

### Real-Time CLI Dashboard

The dashboard provides live monitoring of FinOps agent workflow activities using the Rich library.

#### Features

- **Summary Panel**: Total alerts, approved/escalated counts, potential savings, total bounties paid
- **Latest Activity Panel**: Most recent workflow with analysis snippet
- **Transaction Table**: 7 columns (Time, Alert ID, Status, Recommendation, Confidence, TX Hash, Amount)
- **Color-Coded Status**: Green (APPROVED), Yellow (ESCALATED), Red (DECOMMISSION), Blue (OPTIMIZE)
- **Auto-Refresh**: 2-second polling interval

#### Launch Dashboard

```bash
python scripts/dashboard.py
```

Press `Ctrl+C` to exit.

#### Dashboard Output

```
╭─────────────────────── Summary ───────────────────────╮
│ Total Alerts Processed: 15                            │
│ Approved: 8  |  Escalated: 3                          │
│ Potential Savings: $125.50/hr ($3,012.00/month)       │
│ Total Bounties Paid: 0.0008 ETH                       │
│ Last Refresh: 2026-01-10 12:00:00                     │
╰───────────────────────────────────────────────────────╯

╭─────────────────── Latest Activity ───────────────────╮
│ alert-cpu-high-123 - APPROVED                         │
│ Recommendation: DECOMMISSION                          │
│ Analysis: Critical resource underutilized...          │
╰───────────────────────────────────────────────────────╯

┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Time          ┃ Alert ID      ┃ Status   ┃ TX Hash      ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ 12:00:00      │ alert-123     │ APPROVED │ 0xabc123...  │
│ 11:58:30      │ alert-124     │ ESCALATED│ -            │
└───────────────┴───────────────┴──────────┴──────────────┘
```

---

## Configuration

### Environment Variables

Create a `.env` file:

```env
# MongoDB Atlas
MONGODB_URI=mongodb+srv://...

# Google Gemini API
GOOGLE_API_KEY=...

# Voyage AI
VOYAGE_API_KEY=...

# Coinbase Developer Platform (CDP)
CDP_API_KEY=organizations/.../apiKeys/...
CDP_API_SECRET=-----BEGIN EC PRIVATE KEY-----\n...\n-----END EC PRIVATE KEY-----\n
```

### Prerequisites

- Python 3.9+
- MongoDB Atlas cluster with vector search index
- API Keys: Google Gemini, Voyage AI, Coinbase CDP
- Visual C++ Build Tools (Windows only)

---

## Testing

### Test Paymaster Integration

```bash
python scripts/test_paymaster.py
```

### Test Vector Search

```bash
python scripts/test_enhanced_search.py
```

### Test Full Workflow

```bash
python main.py
```

### Manual Testing

```python
# In Python console
from utils.agent_kit import PaymasterAgent

agent = PaymasterAgent()
agent.initialize_wallet()
balance = agent.get_wallet_balance()
print(balance)
```

---

## Example Execution

```
[SCOUT] Scout: Detected ALT-2026-001 (Legacy GPU Training Cluster)
[SEARCH] Auditor: Vector search score 0.8704 [OK] (>0.85 threshold)
[AI] Gemini: CRITICAL risk → DECOMMISSION ($12.24/hr savings)
[PAYMENT] Paymaster: Issued 0.0001 ETH bounty to 0x742d35... (TX: 0xabc123...)
[OK] MongoDB: Transaction saved to reasoning_logs
[OK] Complete: Workflow finalized
```

---

## Security Notes

1. **Never commit `.env` file** - contains private keys
2. **Wallet export** - use `export_wallet()` for persistence
3. **Test on Sepolia** - always test on testnet first
4. **Monitor balance** - use `get_wallet_balance()` regularly

---

## Future Enhancements

Possible improvements:
- [ ] Dynamic bounty calculation based on resource priority
- [ ] Multi-currency support (USDC, other tokens)
- [ ] Batch payment processing
- [ ] Payment approval workflows
- [ ] Wallet balance monitoring and alerts
- [ ] Mainnet deployment (Base)


## Architecture Diagrams

### Component Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                         main.py                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │              LangGraph Workflow                      │    │
│  │                                                      │    │
│  │  Scout ──► Auditor ──► [Router] ──► Paymaster        │    │
│  │                            │            │            │    │
│  │                            ├─► Escalate │            │    │
│  │                            └─► Complete ◄────────────┘    │
│  └───────────────┬───────────────────┬──────────────────┘    │
└──────────────────┼───────────────────┼───────────────────────┘
                   │                   │
         ┌─────────▼──────┐   ┌────────▼────────┐
         │ utils/         │   │ utils/          │
         │ mongo_client.py│   │ agent_kit.py    │
         │                │   │                 │
         │ • Vector       │   │ • Paymaster     │
         │   Search       │   │   Agent         │
         │ • save_        │   │ • Wallet        │
         │   reasoning_   │   │   Management    │
         │   log()        │   │ • ETH           │
         │                │   │   Transfers     │
         └───────┬────────┘   └────────┬────────┘
                 │                     │
         ┌───────▼─────────────────────▼───────┐
         │     External Services               │
         │                                     │
         │  ┌──────────┐    ┌─────────────┐    │
         │  │ MongoDB  │    │  Coinbase   │    │
         │  │  Atlas   │    │  AgentKit   │    │
         │  │          │    │             │    │
         │  │ • Vector │    │ • CDP API   │    │
         │  │   Search │    │ • Wallet    │    │
         │  │ • Logs   │    │ • Base      │    │
         │  │          │    │   Sepolia   │    │
         │  └──────────┘    └─────────────┘    │
         └─────────────────────────────────────┘
```

### Paymaster Decision Logic

```
┌─────────────────────────────────────────────────────────┐
│           Paymaster Trigger Conditions                  │
└─────────────────────────────────────────────────────────┘

   ┌──────────────────┐
   │ Auditor Status   │
   │   == APPROVED?   │
   └────────┬─────────┘
            │ YES
   ┌────────▼────────┐
   │ Context Data    │
   │  Available?     │
   └────────┬────────┘
            │ YES
   ┌────────▼─────────┐
   │ developer_wallet │
   │    Present?      │
   └────────┬─────────┘
            │ YES
   ┌────────▼─────────┐
   │  Calculate       │
   │  Bounty Amount   │
   │  (0.00001-0.0001)│
   └────────┬─────────┘
            │
   ┌────────▼─────────┐
   │  Execute ETH     │
   │  Transfer        │
   └────────┬─────────┘
            │
   ┌────────▼─────────┐
   │  Save tx_hash    │
   │  to MongoDB      │
   └────────┬─────────┘
            │
      ┌─────▼──────┐
      │   SUCCESS  │
      └────────────┘

   If ANY condition fails → Skip Paymaster
```