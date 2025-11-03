# DecisionNote Agent 🗂

AI-powered team decision tracking agent for Telex - transforms chat discussions into structured, searchable decision logs.

## 🎯 Features

- **Smart Decision Logging** - AI-validated decision recording
- **Team Voting** - Propose decisions for team approval before logging
- **Search & Retrieval** - Find decisions by keyword or date
- **Edit History** - Track decision changes over time
- **Daily AI Summaries** - Automated insights on team decisions
- **No Delete** - Protect decision integrity with edit-only model

## 🚀 Quick Start

### 1. Clone & Setup

```bash
# Clone repository
git clone <your-repo-url>
cd decisionnote-agent

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your Gemini API key
# Get key from: https://makersuite.google.com/app/apikey
```

### 3. Run Development Server

```bash
python app.py
```

Server will start at `http://localhost:8000`

API documentation available at `http://localhost:8000/docs`

## 📋 Commands

### Direct Commands
- `add "Your decision"` - Log a decision immediately
- `/decision list` - View all recorded decisions
- `/decision search "keyword"` - Search decisions
- `/decision edit <id> "New text"` - Update a decision
- `/decision history <id>` - View edit history

### Voting/Approval
- `/decision propose "Your decision"` - Propose for team approval
- `/decision approve <id>` - Approve a proposal
- `/decision reject <id>` - Reject a proposal

### Help
- `/decision help` - Show all available commands

## 📖 Examples

```bash
# Add a decision directly
/decision add "Use PostgreSQL for the database"

# Propose a decision for team voting
/decision propose "Switch to React for frontend"

# Approve a proposal
/decision approve 3

# Search decisions
/decision search "backend"

# Edit a decision
/decision edit 5 "Use MongoDB instead"

# View history
/decision history 5
```

## 🏗 Project Structure

```
decisionnote-agent/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configuration
│   ├── database.py          # Database connection
│   ├── models.py            # Pydantic models
│   └── schemas.py           # Database schemas
├── routes/
│   ├── __init__.py
│   ├── a2a.py               # A2A endpoint
│   ├── triggers.py          # Trigger endpoints
│   ├── well_known.py        # Agent discovery
│   └── workflow_handlers.py # Command handlers
├── services/
│   ├── __init__.py
│   ├── decision_service.py
│   ├── voting_service.py
│   ├── gemini_service.py
│   ├── summary_service.py
│   └── notification_service.py
├── utils/
│   ├── __init__.py
│   ├── parsers.py
│   ├── formatters.py
│   └── validators.py
├── data/                    # Database files
├── app.py                   # App entry point
├── Dockerfile
├── requirements.txt
├── workflow.json
└── README.md
```

## 🔧 Configuration

Edit `.env` file to customize:

```bash
# Gemini AI
GEMINI_API_KEY=your_key_here

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Voting
VOTING_APPROVAL_THRESHOLD=2
VOTING_TIMEOUT_MINUTES=60
ALLOW_SELF_APPROVE=False

# Daily Summary
SUMMARY_TIME=17:00
SUMMARY_TIMEZONE=Africa/Lagos
```

## 🤖 Daily Summary

The agent automatically posts daily summaries with AI-generated insights:

```
📊 Daily Decision Summary - October 30, 2025

The team made 3 key decisions today focused on technical infrastructure. 
You're modernizing the frontend with React and establishing payment 
capabilities through Stripe, while DevOps is moving forward with AWS 
deployment. This represents a significant push toward production readiness.

Today's Decisions (3):
1. "Switch to React for frontend" (by @Dev, 2:00 PM)
2. "Use Stripe for payments" (by @PM, 3:00 PM)
3. "Deploy on AWS" (by @DevOps, 4:00 PM)
```

To trigger manually:
```bash
curl -X POST http://localhost:8000/trigger/daily-summary
```

## 🧪 Testing

Run tests:
```bash
pytest tests/
```

Test specific endpoint:
```bash
# Test daily summary
curl http://localhost:8000/trigger/test-summary
```

## 🤖 A2A Protocol & Telex Integration

This agent is fully compliant with the Agent-to-Agent (A2A) protocol, allowing it to be integrated with Telex.im and other A2A-compatible platforms.

### Well-Known Endpoint
The agent exposes a `/.well-known/agent.json` endpoint for discovery. This provides metadata about the agent's capabilities, as defined in the A2A specification.

### Workflow
The `workflow.json` file in the root of the project defines a simple workflow for the agent. This can be imported into the Telex.im workflow editor to get started quickly.

### API Request/Response Example

Here is an example of the JSON-RPC communication for adding a new decision.

**Request:**
```json
{
    "jsonrpc": "2.0",
    "id": "request-123",
    "method": "message/send",
    "params": {
        "message": {
            "kind": "message",
            "role": "user",
            "parts": [
                {
                    "kind": "text",
                    "text": "add \"Deploy on Railway for production\""
                }
            ],
            "messageId": "msg-abc",
            "taskId": "task-def",
            "contextId": "context-ghi"
        }
    }
}
```

**Success Response:**
```json
{
    "jsonrpc": "2.0",
    "id": "request-123",
    "result": {
        "id": "task-def",
        "contextId": "context-ghi",
        "status": {
            "state": "completed",
            "timestamp": "2025-11-01T01:15:00.000Z",
            "message": {
                "kind": "message",
                "role": "agent",
                "parts": [
                    {
                        "kind": "text",
                        "text": "✅ Decision #6 added: \"Deploy on Railway for production\" (by unknown)"
                    }
                ],
                "messageId": "generated-msg-id"
            }
        },
        "artifacts": [],
        "history": [
            {...user_message...},
            {...agent_response_message...}
        ],
        "kind": "task"
    }
}
```

## 📦 Deployment

### Using Uvicorn
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Using Docker (optional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🙋 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact: [your-email]

---

Built with ❤️ for better team collaboration
