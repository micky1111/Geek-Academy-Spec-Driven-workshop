# Quickstart: Customer Support Agent

**Date**: 2026-04-15  
**Feature**: Customer Support Agentic System  
**Reference**: [plan.md](plan.md)

---

## What You're Building

A customer support agent that receives requests, classifies intent, looks up company policies, and responds with either a direct answer, clarification question, or escalation to human support. Built on Microsoft Agent Framework (MAF) with Azure OpenAI as the LLM provider.

---

## Prerequisites

### System Requirements
- **Python 3.10+** OR **C# .NET 10 SDK** (choose one)
- Git (for cloning repo)
- Azure subscription with OpenAI deployment (or .env/.appsettings configured)

### Choose Your Skeleton

Both skeletons are independent. **Pick ONE**:

- **Python**: `support-agent-python/` (async/await, pytest)
- **C#**: `support-agent-csharp/` (Tasks, xunit)

---

## Setup: Python

### Step 1: Install Dependencies

```bash
cd support-agent-python

# Create virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install MAF and dependencies
pip install agent-framework~=0.5
pip install azure-identity
pip install python-dotenv  # For .env file support
pip install aiohttp  # For async HTTP calls (if needed)
```

### Step 2: Configure Azure OpenAI

Create `.env` file in `support-agent-python/`:

```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
```

Or set as environment variables:

```bash
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your-key"
export AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o"
```

### Step 3: Verify File Structure

```
support-agent-python/
├── main.py               ← Entry point (implement/enable)
├── requirements.txt      ← Dependencies (add MAF 0.5.x)
├── .env                  ← Your credentials (create)
├── app/
│   ├── __init__.py
│   ├── agent.py          ← Agent orchestration (TO IMPLEMENT)
│   ├── models.py         ← Data models (TO IMPLEMENT)
│   ├── processor.py      ← Request processing (TO IMPLEMENT)
│   ├── console_ui.py     ← Console UI (existing)
│   └── renderer.py       ← Response formatting (existing)
└── data/
    ├── support_handbook.md   ← Company policies (existing)
    └── sample_requests.md    ← Test scenarios (existing)
```

### Step 4: First Run

```bash
# Run the agent
python main.py

# Expected output:
# Customer request: I want a refund
# [Agent processes...]
# Agent: "Great! I can help with your refund request. To check your eligibility..."
```

### Step 5: Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests (to be created as you implement)
pytest tests/
```

---

## Setup: C#

### Step 1: Install MAF Package

```bash
cd support-agent-csharp

# Add NuGet packages
dotnet add package Microsoft.Agent.Framework --version 0.5.x
dotnet add package Azure.Identity
dotnet add package Azure.AI.OpenAI
```

### Step 2: Configure Azure OpenAI

Create `appsettings.Development.json` in `support-agent-csharp/`:

```json
{
  "Azure": {
    "OpenAI": {
      "Endpoint": "https://your-resource.openai.azure.com/",
      "ApiKey": "your-api-key-here",
      "DeploymentName": "gpt-4o"
    }
  }
}
```

Or use environment variables and `IConfiguration`:

```csharp
var endpoint = Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT");
var apiKey = Environment.GetEnvironmentVariable("AZURE_OPENAI_API_KEY");
var deploymentName = Environment.GetEnvironmentVariable("AZURE_OPENAI_DEPLOYMENT_NAME");
```

### Step 3: Verify File Structure

```
support-agent-csharp/
├── Program.cs                          ← Entry point (implement/enable)
├── support-agent-csharp.csproj         ← Project file (add MAF NuGet)
├── appsettings.Development.json        ← Your credentials (create)
├── Agents/
│   └── SupportAgent.cs                 ← Agent orchestration (TO IMPLEMENT)
├── Models/
│   ├── SupportRequest.cs               ← TO IMPLEMENT
│   ├── SupportResponse.cs              ← TO IMPLEMENT
│   └── CustomerIntent.cs               ← TO IMPLEMENT
├── Orchestration/
│   └── SupportRequestProcessor.cs      ← Request processing (existing)
├── Common/
│   ├── ConsoleUi.cs                    ← Console UI (existing)
│   └── SupportRequestRenderer.cs       ← Response formatting (existing)
└── Data/
    ├── support_handbook.md             ← Company policies (existing)
    └── sample_requests.md              ← Test scenarios (existing)
```

### Step 4: First Run

```bash
# Restore dependencies
dotnet restore

# Run the agent
dotnet run

# Expected output:
# Customer request: I want a refund
# [Agent processes...]
# Agent: "Great! I can help with your refund request. To check your eligibility..."
```

### Step 5: Run Tests

```bash
# Create test project (if not exists)
dotnet new xunit -n support-agent-csharp.Tests -o Tests

# Run tests
dotnet test
```

---

## Architecture Overview

### Console Input Loop

```
Console:
  1. Prompt customer for request
  2. Read input → SupportRequest
  3. Call agent.HandleSupportRequest(request)
  4. Agent returns SupportResponse
  5. Display response
  6. If response is CLARIFICATION_NEEDED, loop back to step 1 with merged context
  7. If response is DIRECT_ANSWER or ESCALATION, end conversation or prompt for new request
```

### Agent Processing

```
Agent (MAF):
  1. Receive SupportRequest
  2. Classify intent (refund | cancel | billing | question | complaint | unclear)
  3. Extract entities (order_id, date, amount, etc.)
  4. Call handbook lookup tool if intent is policy-related
  5. Generate response:
     - DIRECT_ANSWER: Answer from handbook + cite policy
     - CLARIFICATION_NEEDED: Ask specific missing-info questions
     - ESCALATION: Detect emotion/complexity and escalate with context
  6. Return SupportResponse
```

### Data Flow

```
SupportRequest
  ↓ (agent.classify_intent)
CustomerIntent
  ↓ (agent.extract_entities)
Entities (order_id, date, etc.)
  ↓ (agent may call handbook tool)
HandbookPolicies
  ↓ (agent.generate_response)
SupportResponse
  ↓
Console displays message
[If CLARIFICATION_NEEDED: merge + resend]
[If ESCALATION: display context]
[If DIRECT_ANSWER: done]
```

---

## Testing the Agent

### Sample Requests (From `data/sample_requests.md`)

Use these to test different intent types:

**Refund Request**:
```
Customer: "I purchased on April 5 and want to return it. Can I get a refund?"
Expected: DIRECT_ANSWER or CLARIFICATION (request order ID if missing)
```

**Vague Billing Question**:
```
Customer: "Why was I charged $50?"
Expected: CLARIFICATION (ask order ID and date)
```

**Escalation Case**:
```
Customer: "I've been a customer for 5 years and this is ridiculous! Your service quality has gone downhill and I'm furious!"
Expected: ESCALATION (emotional_escalation reason)
```

**Feature Question**:
```
Customer: "How do I upgrade my plan?"
Expected: DIRECT_ANSWER (cite Plan Features section from handbook)
```

### Running Tests Manually

**Python**:
```bash
# Test clarification flow
python -c "
from app.agent import SupportAgent
agent = SupportAgent()
result = agent.handle_support_request('I want a refund')
print(result.message)
"
```

**C#**:
```bash
# Test in Program.cs or create a simple test
var agent = new SupportAgent();
var request = new SupportRequest { Message = "I want a refund" };
var response = await agent.HandleSupportRequestAsync(request);
Console.WriteLine(response.Message);
```

---

## Debugging Checklist

### Agent Returns Empty Message

1. Check Azure OpenAI credentials (endpoint, key, deployment name)
2. Check LLM API is responsive: `curl -X GET $AZURE_OPENAI_ENDPOINT/status`
3. Check MAF is installed: `pip list | grep agent` (Python) or `dotnet list package` (C#)
4. Check `support_handbook.md` exists and is readable

### Handbook Lookup Returns No Results

1. Verify `data/support_handbook.md` exists in skeleton directory
2. Test markdown parsing: Print sections from handbook to debug
3. Check query keywords match handbook section titles/tags
4. Consider keyword relevance: "refund" should match "Refund Policy", but "money back" might not if not tagged

### Agent Hangs or Timeout

1. Check LLM timeout settings (default ~30s usually)
2. Try simpler request: `"hello"` instead of complex multi-part query
3. Check Azure OpenAI API quota not exceeded
4. Check network connectivity: Can reach Azure endpoint from your machine?

### Response Format Errors

1. Ensure agent returns structured SupportResponse (not raw string)
2. Check response_type is one of: DIRECT_ANSWER, CLARIFICATION_NEEDED, ESCALATION
3. Verify message is non-empty (<2000 chars)
4. If CLARIFICATION, ensure clarification object is present with questions

---

## Key Files to Review

- **[spec.md](../spec.md)** — What the agent should do (user stories, requirements)
- **[data-model.md](../data-model.md)** — Data structures (SupportRequest, SupportResponse, etc.)
- **[contracts/request-response.md](contracts/request-response.md)** — Agent input/output contract with examples
- **[contracts/handbook-lookup.md](contracts/handbook-lookup.md)** — Handbook tool specification and implementation

---

## Implementation Checklist

- [ ] Dependencies installed (MAF, Azure SDK, async libs)
- [ ] Credentials configured (.env or appsettings.json)
- [ ] First run works (console prompt → agent response)
- [ ] Sample test request processed correctly
- [ ] Handbook lookup tool implemented
- [ ] Intent classification working (refund/cancel/billing/question/escalation)
- [ ] Clarification flow working (asks questions → user responds → agent continues)
- [ ] Escalation detection working (detects anger/complexity)
- [ ] Unit tests pass
- [ ] Integration tests pass (end-to-end request → response)

---

## Next Steps

1. **Start with skeleton**: Choose Python or C#, run first setup ✓
2. **Implement data models**: SupportRequest, SupportResponse, etc. (use [data-model.md](../data-model.md))
3. **Implement agent**: Intent classification, handbook lookup, response generation (use [contracts](contracts))
4. **Test with sample requests**: Try each scenario from [sample_requests.md](../../support-agent-python/data/sample_requests.md) or C# equivalent
5. **Add unit/integration tests**: Verify each flow (refund, clarification, escalation)
6. **Extended tasks (optional)**: Human-in-the-loop approval, multi-agent collaboration, etc.

---

## Getting Help

- **MAF Documentation**: <https://learn.microsoft.com/en-us/agent-framework/>
- **MAF Samples**: <https://github.com/microsoft/Agent-Framework-Samples>
- **Azure OpenAI**: <https://learn.microsoft.com/en-us/azure/ai-services/openai/>
- **Feature Spec**: [spec.md](../spec.md) — Describes what the agent should do
- **Design Docs**: [data-model.md](../data-model.md), [contracts/](contracts/) — Describe how to structure code

---

**Quickstart Status**: Ready to begin implementation  
**Recommended Duration**: 2-4 hours for MVP (clarification, direct answer, basic escalation)
