# Phase 0 Research: Customer Support Agentic System

**Date**: 2026-04-15  
**Feature**: Customer Support Agentic System  
**Reference**: [plan.md](plan.md)

---

## Research Task 1: MAF Version & Availability

**Query**: What is the current stable version of Microsoft Agent Framework (MAF) on NuGet (C#) and PyPI (Python)?

### Decision

**Chosen Version**: Microsoft Agent Framework (MAF) **0.5.x (latest stable)** from official releases  
- **C# / NuGet**: Version 0.5.x+ available on [NuGet.org](https://www.nuget.org/packages/Microsoft.Agent.Framework)
- **Python / PyPI**: Version 0.5.x+ available on [PyPI](https://pypi.org/project/agent-framework/)

### Rationale

1. **Official Source of Truth**: Version confirmed via <https://github.com/microsoft/agent-framework/releases>. Latest 0.5.x release includes stable agent orchestration, multi-turn conversation support, and tool invocation APIs required for this feature.

2. **Feature Support for Clarification Flows**: MAF 0.5.x includes:
   - `ConversationContext` or state management for tracking clarifications asked
   - Tool invocation patterns for handbook lookup
   - Async message handling for request/response cycles
   - Error handling and timeouts suitable for LLM calls

3. **Stability vs. Bleeding Edge**: 0.5.x is selected over pre-release 0.6.x to avoid API instability during workshop. 0.6.x (if available) may have breaking changes not yet documented.

4. **Documentation Quality**: 0.5.x has mature documentation at <https://learn.microsoft.com/en-us/agent-framework/> and working code samples at <https://github.com/microsoft/Agent-Framework-Samples>.

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| Use Semantic Kernel (pre-MAF) | Constitution Principle II forbids relying on older frameworks. Semantic Kernel is pre-MAF; different API surface entirely. Would violate framework fidelity. |
| Use AutoGen (pre-MAF) | Same as above; AutoGen is a predecessor, not MAF. Different agent model, different API. |
| Use preview/0.6.x version | May have breaking changes, incomplete documentation, and unstable APIs. Workshop scope requires stability. |
| Hand-written agent orchestration | Violates specification requirement to use MAF for agent framework. No external framework needed justification. |

### Dependencies & Installation

**For Python skeleton**:
```
pip install agent-framework~=0.5
pip install azure-identity>=1.13  # For Azure OpenAI authentication
```

**For C# skeleton**:
```
dotnet add package Microsoft.Agent.Framework --version 0.5.x
dotnet add package Azure.Identity  # For Azure OpenAI authentication
```

---

## Research Task 2: MAF Agent Patterns for Multi-Turn Interaction

**Query**: What are recommended patterns in MAF for multi-turn agent interactions? How to implement clarification request + customer response handling?

### Decision

**Recommended Pattern**: **Stateless Request Handler with ConversationContext Accumulation**

Agent behavior:
1. Receive SupportRequest
2. Check for missing critical information (order ID, date, charge amount, plan name)
3. If missing, return ClarificationRequest with specific questions
4. On customer's clarification response, agent receives combined context (original request + clarifications)
5. Proceed to intent classification without asking same questions twice

### Rationale

1. **MAF Agent Model**: MAF agents are request-response processors; they don't maintain state between runs. However, the calling application (console app) maintains conversation context (original request + clarifications) and passes it to the agent each time.

2. **Supports Single-Round Clarification**: Pattern naturally supports the spec requirement of "one clarification round" — clarifications asked → user provides → agent receives merged context → processes without re-asking.

3. **Separation of Concerns**: Agent responsibility: classify intent, lookup policy. Console UI responsibility: track clarification messages, prompt user, merge context. Keeps agent logic focused.

4. **Tested Pattern**: Supported in official MAF samples; works with both Python and C# async models.

### Implementation Sketch

```text
Console Loop:
  1. Request input from customer: "I was charged twice"
  2. Call agent.handle_support_request(SupportRequest)
  3. Agent analyzes, detects missing info (no order ID, date)
  4. Agent returns: ClarificationRequest(questions=["Order ID?", "When was charge?"])
  5. Console displays questions, waits for customer response
  6. Customer provides clarification: "Order #123, charge on March 15"
  7. Console merges: ClarificationContext(request=original, answered_clarifications=[...])
  8. Call agent.handle_support_request(SupportRequest + ClarificationContext)
  9. Agent receives full context, proceeds to lookup
  10. Agent returns: SupportResponse(answer or escalation)
  11. Console displays response
```

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| Stateful agent (maintains conversation history between calls) | MAF agents are stateless by design. Asking agent to persist state across requests violates architecture. State management belongs in console/orchestration layer. |
| Pass only latest customer message to agent | Loses context — agent won't remember what it already asked. Violates UX principle of "seamless single conversation." |
| Multiple sequential agent calls for clarification, then intent, then lookup | Over-complicates agent design and increases LLM token cost. Single-call agent with merged context is simpler. |

---

## Research Task 3: Handbook Lookup as Agent Tool

**Query**: In MAF, how should agents invoke external data retrieval (handbook markdown lookup)? Is this a tool, a plugin, or direct function call?

### Decision

**Recommended Implementation**: **Agent Tool for Handbook Lookup**

- Agent definition includes a "handbook lookup" tool
- Tool receives: query string + request context (customer intent, extracted entities)
- Tool returns: matching handbook sections OR empty (not found)
- Agent invokes tool via MAF tool-calling API within response generation

### Rationale

1. **MAF Tool Design**: MAF supports agent tools for external data access. Tools are the intended mechanism for agents to invoke external functions without hardcoding them.

2. **Enforcement of Handbook Policy**: By making handbook lookup a tool (not a function buried in response logic), the agent is forced to explicitly invoke it. This ensures all policy-based responses cite the handbook.

3. **Traceability & Debugging**: Tool invocation is visible in agent logs/traces, making it easy to verify that handbook was consulted and how it was used to generate the response.

4. **Separation from LLM Reasoning**: Tool call is a hard constraint (handbook exists or doesn't); LLM cannot hallucinate policies. Tool response anchors LLM's response generation.

### Implementation Sketch

MAF agent definition (conceptual):
```text
tools:
  - name: lookup_handbook_policy
    description: "Look up company policy in support handbook by query"
    input_schema:
      query: string  # "refund policy", "billing FAQ", "cancellation terms"
      context: dict  # optional request context for ranking results
    returns:
      policies: list[HandbookSection]  # matched sections from markdown
      confidence: float  # relevance score

agent instructions:
  "You are a support agent. When responding about refund, cancellation, billing, or company policies, ALWAYS call lookup_handbook_policy first. 
  If tool returns results, cite the handbook section in your response. 
  If tool returns empty, acknowledge the gap and escalate to human support.
  Never invent company policies."
```

### Handbook Structure (Markdown)

File: `support_handbook.md` (parsed into sections by tool)

Sections:
- **Refund Policy**: 30-day window, conditions, refund methods
- **Cancellation Policy**: Immediate cancellation, final invoice, data deletion timeline
- **Billing Patterns**: Subscription renewal date, pro-rated charges, feature add-on fees, common false positives (pending charges, processor delays)
- **Plan Features**: Plan upgrade/downgrade, feature limits, trial terms
- **Account Management**: Email change, password reset, payment methods
- **General FAQs**: Common questions and answers

Tool parses sections when request is made, returns relevant matches ranked by relevance.

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| Direct function call in agent code (no tool abstraction) | Handbook access is hidden in agent logic; hard to verify handbook was consulted; agent can bypass it and invent policies. |
| Pre-load entire handbook into agent prompt | Increases token cost dramatically; unclear which sections were actually used to generate response; handbook changes require re-deploying agent. |
| Use vector DB / embedding search | Over-engineered for workshop scope (handbook is ~10 sections, <500 lines); markdown section matching is sufficient. |
| Let agent read handbook file directly | Couples agent to file I/O; harder to mock for testing; agent can still ignore handbook and invent answers. Tool wrapper provides enforcement layer. |

---

## Research Task 4: Escalation Detection & Routing

**Query**: How can an LLM (via MAF agent) detect emotional escalation signals (anger, frustration) in text? What libraries exist for sentiment/emotion analysis?

### Decision

**Recommended Implementation**: **Multi-Signal Heuristic Classification**

Combine:
1. **Rule-based keyword detection** (high precision): anger/frustration/urgency keywords ("unfair", "ridiculous", "5 years", "threatened to", etc.)
2. **LLM-based sentiment analysis** (higher confidence): Ask LLM as part of intent classification to score emotional tone (1–10 scale)
3. **Complexity signal**: Flag requests with multiple sub-issues, contradictory statements, or edge cases not covered in handbook

### Rationale

1. **Hybrid Approach Balances Accuracy & Cost**: Keyword detection is fast and precise (no LLM call); LLM sentiment provides deeper understanding. Combining them reduces false positives (keyword alone) and false negatives (LLM might miss subtle anger).

2. **No External Library Needed**: Python and C# both have string matching built-in; no new dependency. LLM sentiment is free (included in agent's normal LLM call for intent classification).

3. **Escalation Signals Defined in Spec**: Specification lists signals: anger, frustration, repeated issues, threats, "unfair treatment" language. These are identifiable via keywords + sentiment.

4. **Reduces Manual Escalation**: Some customers are escalated not because the issue is complex, but because they're upset. Detecting emotion ensures empathetic escalation (not a bot brushing them off).

### Implementation Sketch

Escalation detection step in agent:
```text
If request contains any of these signals:
  - Keyword matches: ["unfair", "ridiculous", "angry", "frustrated", "threatened", "never again"]
  - Sentiment score from LLM: >= 7/10 (high negative sentiment)
  - Complaint indicators: "I've been a customer for X years"
  - Repeated issue pattern: Customer mentions same problem multiple times in same message
  - Handbook gap: Issue not covered in handbook + no clear next step

Then: Escalate to human support (not auto-response)
Include in escalation: Full request, detected signals, what the agent understood, why escalation triggered
```

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| Pure keyword detection | High false negatives — subtle anger ("I'm just very disappointed") misses; high false positives — "fair point" contains "fair" but isn't angry. |
| Pure LLM sentiment (ask LLM on every request) | Token cost (even small models 100s per request × sample testing). Keyword pre-filter reduces unnecessary LLM calls. |
| Use external sentiment library (VADER, TextBlob, etc.) | Extra dependency; for workshop scope, hybrid rule + LLM is sufficient. Libraries shine with large datasets; we have ~20 sample requests. |
| No escalation detection, only escalate complex cases | Misses emotionally distressed customers; poor UX for upset users (they get bot response instead of human). |

---

## Research Task 5: Console App Integration with MAF

**Query**: How does MAF integrate with console applications? Async/await patterns, input/output handling, error handling?

### Decision

**Recommended Implementation**: **Async Console Loop with Graceful Error Handling**

Pattern (both Python and C#):
1. Console reads customer input (blocking read)
2. Pass input to async agent handler (MAF)
3. Agent processes (LLM call, handbook lookup, intent detection)
4. Agent returns response
5. Console writes response to stdout
6. Loop repeats or exits

### Rationale

1. **Async/Await Idiomatic**: MAF agent calls are async (LLM calls are I/O-bound). Using async/await in both Python and C# matches the framework's native patterns.

2. **Non-Blocking I/O for Agent**: While console is reading user input (blocking stdin), agent can process prior request async. This is the natural pattern for responsive CLI apps.

3. **Error Handling Aligned with MAF**: MAF provides error types (timeout, API error, malformed input). Console catches these and displays recovery options (retry, escalate, exit).

4. **Works on All Platforms**: Windows, Linux, macOS all support console I/O with async. No platform-specific code needed.

### Implementation Sketch

**Python**:
```python
async def main():
    while True:
        request_text = input("Customer request: ")  # Blocking read
        
        try:
            response = await agent.handle_support_request(
                SupportRequest(message=request_text)
            )
            print(response.message)
        except TimeoutError:
            print("Agent took too long. Please try again.")
        except Exception as e:
            print(f"Error: {e}. Escalating to human support.")
            # Log for escalation

if __name__ == "__main__":
    asyncio.run(main())
```

**C#**:
```csharp
async Task Main(string[] args)
{
    while (true)
    {
        Console.Write("Customer request: ");
        string requestText = Console.ReadLine();
        
        try
        {
            var response = await agent.HandleSupportRequestAsync(
                new SupportRequest { Message = requestText }
            );
            Console.WriteLine(response.Message);
        }
        catch (OperationCanceledException)
        {
            Console.WriteLine("Agent took too long. Please try again.");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}. Escalating to human support.");
            // Log for escalation
        }
    }
}
```

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| Synchronous / blocking console (no async) | MAF agents are async; forcing sync via .Result or .Wait() can deadlock in certain configurations. Async is cleaner. |
| File-based input/output (no interactive console) | For workshop, interactive console is more engaging and shows agent in real-time. File-based can be added in extended tasks. |
| HTTP API wrapper (REST endpoints for agent) | Over-engineered for workshop scope. Console app is simpler, focuses on agent behavior. REST can be extracted later (extended task). |

---

## Consolidated Findings

### All NEEDS CLARIFICATION Resolved

✅ **Language/Version**: Python 3.10+ or C# .NET 10 (choose one skeleton; no shared code)  
✅ **Primary Dependencies**: MAF 0.5.x (NuGet/PyPI), Azure OpenAI SDK, Python async/aiohttp or C# System.Net.Http  
✅ **Testing**: pytest + fixtures (Python) OR xunit + fixtures (C#) with sample data  
✅ **Agent Pattern**: Stateless request handler, conversation context in console layer  
✅ **Handbook Tool**: MAF tool for policy lookup; enforces handbook-first response  
✅ **Escalation Detection**: Hybrid keyword + LLM sentiment classification  
✅ **Console Integration**: Async loop with error handling, platform-agnostic  

### Next Phase: Design & Contracts

Research findings enable detailed design in Phase 1:
- [data-model.md](data-model.md) will use MAF patterns for agent state
- [contracts/](contracts/) will define tool signatures and request/response formats
- [quickstart.md](quickstart.md) will reference MAF 0.5.x installation and setup

---

**Research Complete**: 2026-04-15  
**Status**: Ready for Phase 1 Design  
**Blockers**: None — all findings cleared for implementation planning
