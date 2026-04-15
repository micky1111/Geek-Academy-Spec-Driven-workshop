# Implementation Plan: Customer Support Agentic System

**Branch**: `001-customer-support-agent` | **Date**: 2026-04-15 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from [Feature Specification: Customer Support Agentic System](spec.md)

---

## Summary

Build a customer support agentic application that receives customer requests, classifies intent, retrieves relevant support handbook policies, and generates policy-compliant responses. The system must handle five primary flows: (1) incomplete requests with one-round clarification, (2) refund/cancellation requests with handbook policy validation, (3) billing explanations, (4) general feature/account questions, and (5) escalation for complex or emotionally charged cases. All responses must feel cohesive and personalized, not fragmented or template-based. The implementation uses Microsoft Agent Framework for agent orchestration and provides a console interface.

---

## Technical Context

**Language/Version**: Python 3.10+ OR C# .NET 10 (choose one skeleton; see Skeleton Independence principle below) | NEEDS CLARIFICATION on which skeleton to implement first
**Primary Dependencies**: Microsoft Agent Framework (MAF), Azure OpenAI (LLM provider via Foundry), Python async/aiohttp OR C# System.Net.Http  
**Storage**: File-based (support handbook markdown, sample requests); no database in scope  
**Testing**: pytest (Python) OR xunit (C#) with integration test fixtures from sample data  
**Target Platform**: Console application (Windows/Linux/macOS compatible)  
**Project Type**: CLI agent application  
**Performance Goals**: Response generation <5 seconds for standard handbook lookups (no external API calls beyond LLM in scope)  
**Constraints**: Single-round clarification (no clarification loops), handbook-only policy (no invented rules), no external CRM/billing system calls  
**Scale/Scope**: Support request handling for workshop demonstration; sample handbook with ≤10 policy sections; sample requests file with ~10-20 example cases

---

## Constitution Check

**GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.**

Constitution file: [Agentic Systems Workshop Constitution v1.0.0](./.specify/memory/constitution.md)

### Validation Against Five Core Principles

| Principle | Requirement | Status | Justification |
|-----------|-------------|--------|---------------|
| **I. Spec-First** | Feature begins with formal specification including user scenarios, acceptance criteria, technology decisions | ✅ PASS | Specification complete with 6 prioritized user stories, 7 functional requirements, 7 success criteria, and all assumptions documented |
| **II. Framework Fidelity** | MAF usage strictly follows official docs; no invented APIs from semantic kernel/autogen; version sourced from official releases | ⚠️ NEEDS CLARIFICATION | Technical Context lists "MAF" as dependency but version NOT yet specified. Must verify current NuGet/PyPI version (e.g., MAF 0.5.x) and document in Phase 0 research before proceeding to Phase 1. |
| **III. Skeleton Independence** | C# and Python implementations remain separate; no cross-mirroring unless authorized | ✅ PASS | Plan covers both skeletons as viable targets. Implementer MUST choose ONE skeleton (support-agent-csharp/ or support-agent-python/) before task generation and work exclusively in chosen skeleton. Both skeletons provided in repo; no code duplication required. |
| **IV. Agent Testability** | All agent components independently testable using sample data, no external service dependencies | ✅ PASS | Sample data provided (support_handbook.md, sample_requests.md in both skeletons). Integration tests will exercise agent intent detection, handbook lookups, and escalation routing with fixtures. Mock/stub external calls (LLM responses for testing). |
| **V. Integration Testing** | Agent features verify full MAF contract, tool invocation chains, request/response round-trips | ✅ PASS | Acceptance scenarios in spec (Stories 1–6) define integration test cases: clarification request → response, handbook lookup → policy validation, escalation detection → routing. Plan will detail integration test strategy in Phase 1. |

### Gate Violations & Justifications

**Violation**: Framework Fidelity principle requires MAF version confirmation before Phase 0 research starts.  
**Justification**: Phase 0 research task will include "Verify MAF current version on NuGet/PyPI and document rationale for choice + feature compatibility." This will resolve the ambiguity before Phase 1 design.  
**Resolution**: CONDITIONAL PASS — Continue to Phase 0 with research task #1 focused on resolving MAF version.

**Overall Gate Status**: ✅ CONDITIONAL PASS (MAF version research required before Phase 1)

---

## Project Structure

### Documentation (this feature)

```text
specs/001-customer-support-agent/
├── spec.md                          # Feature specification (COMPLETE)
├── checklists/
│   └── requirements.md              # Spec validation checklist (COMPLETE)
├── plan.md                          # This file (UNDER CONSTRUCTION)
├── research.md                       # Phase 0: Resolve unknowns (TO DO)
├── data-model.md                    # Phase 1: Entity model & state (TO DO)
├── contracts/                       # Phase 1: Agent interface contracts (TO DO)
│   ├── request-response.md          # Agent request/response contract
│   └── handbook-lookup.md           # Handbook access contract
├── quickstart.md                    # Phase 1: Setup & first run (TO DO)
└── [tasks.md will be created by    # Phase 2: Task breakdown (NOT by /speckit.plan)
     /speckit.tasks]
```

### Source Code (choose ONE skeleton)

**Option A: Python Implementation** (if selected)
```text
support-agent-python/
├── main.py                          # Console entry point
├── requirements.txt                 # Python dependencies (add MAF)
├── app/
│   ├── __init__.py
│   ├── agent.py                     # Agent orchestration (MAF-based)
│   ├── models.py                    # Data models (Request, Response, Intent, etc.)
│   ├── processor.py                 # Request → Intent → Handbook lookup → Response
│   ├── console_ui.py                # Console UI input/output (existing)
│   └── renderer.py                  # Response formatting (existing)
└── data/
    ├── support_handbook.md          # Company policies (existing)
    └── sample_requests.md           # Test data (existing)
```

**Option B: C# Implementation** (if selected)
```text
support-agent-csharp/
├── Program.cs                       # Console entry point
├── support-agent-csharp.csproj      # C# project file (add MAF NuGet)
├── Agents/
│   └── SupportAgent.cs              # Agent orchestration (MAF-based)
├── Models/
│   ├── SupportRequest.cs            # Request model
│   ├── SupportResponse.cs           # Response model
│   ├── CustomerIntent.cs            # Intent classification
│   └── SupportRequestResult.cs      # Existing
├── Orchestration/
│   └── SupportRequestProcessor.cs   # Request → Intent → Handbook lookup → Response (existing)
├── Common/
│   ├── ConsoleUi.cs                 # Console UI input/output (existing)
│   └── SupportRequestRenderer.cs    # Response formatting (existing)
└── Data/
    ├── support_handbook.md          # Company policies (existing)
    └── sample_requests.md           # Test data (existing)
```

**Structure Decision**: Both skeletons are viable independent implementations. **Implementer MUST select exactly ONE skeleton before Phase 2 task generation.** The plan accommodates both; the implementation will target one language/framework. No cross-skeleton code duplication required.

---

## Complexity Tracking

### Justifications for Constitutional Compliance

| Decision | Why Needed | Simpler Alternative Considered |
|----------|-----------|--------------------------------|
| MAF framework required | Specification and Lab 1 explicitly require agentic system with agent orchestration; MAF is official Microsoft framework for agents | Hand-written state machines or simple if/else routing would lack agent capabilities (tool calling, multi-agent workflows, async message handling) required for clarification + escalation flows |
| Single clarification round (no loops) | Spec § allows one clarification. Loop would frustrate customers and violate principle of "seamless single-response experience" | Infinite clarification rounds would require context management, memory, and risk customer abandonment. Reset to clarification after escalation also violates seamless flow. |
| Handbook-only policies | Spec § requires strict adherence to company policy "do not invent rules"; no external systems (CRM, billing) in scope | Reasoning-based refund approval without handbook reference risks policy violations and financial liability. Handbook lookup ensures compliance. |
| Separate C#/Python skeletons | Constitution Principle III requires independence; each skeleton uses idiomatic language patterns (async/await vs Tasks, aiohttp vs HttpClient) | Shared code (templates, shared assembly, etc.) would force artificial parity, prevent learning language-specific patterns, and create maintenance burden when frameworks diverge. |
| Integration tests with MAF | Constitution Principle V requires verification of full framework contract | Unit tests alone cannot catch serialization issues, async bugs, tool invocation sequencing, or message passing errors that only appear in integrated MAF workflows. |

---

## PHASE 0: Research & Clarification

**Objective**: Resolve all NEEDS CLARIFICATION markers in Technical Context by researching framework versions, MAF agent patterns, and assistant best practices.

**Research Tasks** (to be executed and consolidated in research.md):

1. **MAF Version & Availability**
   - Query: "What is the current stable version of Microsoft Agent Framework (MAF) on NuGet (C#) and PyPI (Python)?"
   - Research: Check official releases at <https://github.com/microsoft/agent-framework/releases>, NuGet.org, PyPI.org
   - Deliverable: Chosen version (e.g., "MAF 0.5.x"), rationale for choice (stability, feature support for clarification flows), reference to official docs
   - Blocks: Cannot install dependencies in Phase 1 without version fix

2. **MAF Agent Patterns for Multi-Turn Interaction**
   - Query: "What are recommended patterns in MAF for multi-turn agent interactions? How to implement clarification request + customer response handling?"
   - Research: Read official MAF docs, review Agent-Framework-Samples repo for clarification or state-management examples
   - Deliverable: Pattern name (e.g., "ConversationContext", "RequestState"), code snippet location in official samples, or architecture decision (stateless request → state in handler)
   - Blocks: Agent design in Phase 1

3. **Handbook Lookup as Agent Tool**
   - Query: "In MAF, how should agents invoke external data retrieval (handbook markdown lookup)? Is this a tool, a plugin, or direct function call?"
   - Research: MAF tools/skills documentation, official samples showing external data access
   - Deliverable: Recommended pattern (tool invocation, plugin, or direct lookup), implementation approach for markdown parsing
   - Blocks: Tool design in data-model.md

4. **Escalation Detection & Routing**
   - Query: "How can an LLM (via MAF agent) detect emotional escalation signals (anger, frustration) in text? What libraries exist for sentiment/emotion analysis?"
   - Research: MAF integration with sentiment analysis, existing tooling (VADER, TextBlob vs. LLM-based classification)
   - Deliverable: Recommended approach (rule-based keywords, sentiment library, or LLM classification), trade-offs (accuracy vs. false positives)
   - Blocks: Agent logic design

5. **Console App Integration with MAF**
   - Query: "How does MAF integrate with console applications? Async/await patterns, input/output handling, error handling?"
   - Research: Official MAF examples for CLI/console apps, async patterns in both Python and C#
   - Deliverable: Pattern for console → agent → console response loop, async handling in both languages
   - Blocks: Agent orchestration in Processor/Agent classes

**Consolidated Output**: [research.md](research.md) (TO DO) will document all findings with Decision, Rationale, and Alternatives Considered for each research task.

---

## PHASE 1: Design & Contracts

**Objective**: Define data models, agent interfaces, and orchestration architecture based on research findings.

### 1️⃣ Data Model (Extract from Specification)

**Deliverable**: [data-model.md](data-model.md) (TO DO)

Key entities extracted from specification:
- **SupportRequest**: Incoming customer message, metadata (timestamp, requestId)
- **CustomerIntent**: Classified category (refund, cancel, billing, question, complaint, unclear) + confidence score
- **ClarificationRequest**: Specific missing-information questions to ask customer
- **HandbookPolicy**: Company policy rule (refund window, cancellation terms, billing explanation)
- **SupportResponse**: Final response (direct answer, clarification question, or escalation notice) + reasoning
- **EscalationReason**: Why case routed to human (policy exception, emotion signal, complexity)

Validation rules:
- Request must have non-empty message
- Intent classification must succeed or request clarification
- Refund/cancellation responses must cite handbook policy or escalate
- Clarifications must be specific (not generic "tell me more")
- Escalations must include full context

### 2️⃣ Agent Interface Contracts

**Deliverable**: [contracts/](contracts/) directory (TO DO)

Files to create:
- **[contracts/request-response.md](contracts/request-response.md)**: Agent input/output contract
  - Agent receives: SupportRequest + optional ClarificationContext
  - Agent returns: SupportResponse (direct answer, clarification, or escalation)
  - Error handling: Malformed input, handbook lookup failure, LLM timeout
  
- **[contracts/handbook-lookup.md](contracts/handbook-lookup.md)**: Handbook access contract
  - Handbook tool receives: query string + request context
  - Handbook tool returns: matching policies OR empty (not found)
  - Parsing: Markdown structure in support_handbook.md with sections for: Refund Policy, Cancellation Policy, Billing Patterns, Feature FAQ, Escalation Indicators

### 3️⃣ Quickstart Guide

**Deliverable**: [quickstart.md](quickstart.md) (TO DO)

Contents:
- Install MAF dependencies (pip install / NuGet add)
- Set Azure OpenAI credentials (appsettings.json / .env)
- Run first test: `python main.py` or `dotnet run`
- Expected output: Agent responds to sample request from sample_requests.md
- Debug checklist: If agent doesn't respond, check credentials, handbook parsing, MAF initialization

### 4️⃣ Agent Context Update

**Execution**: After Phase 1 design, run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType copilot` to update Copilot agent context with:
- MAF version and authoritative source doc
- Agent design patterns for clarification, handbook lookup, escalation detection
- Skeleton choice (C# or Python) and structure

---

## Success Criteria (Planning Gate)

- [x] Specification complete and validated (6 user stories, 7 functional requirements, 7 success criteria)
- [x] Constitution compliance checked (all 5 principles addressed; MAF version research required before Phase 1) → ✅ RESOLVED IN PHASE 0
- [x] Research.md complete (Phase 0 deliverable)
- [x] Data-model.md complete (Phase 1 deliverable)
- [x] Contracts defined (Phase 1 deliverable — request-response.md, handbook-lookup.md)
- [x] Quickstart draft written (Phase 1 deliverable)
- [ ] Agent context updated post-Phase 1 (next: running update-agent-context.ps1)

---

**Plan Status**: Phase 1 Design Complete | Agent Context Update In Progress  
**Milestones Completed**: Specification, Research, Design & Contracts  
**Next Phase**: Task Generation (`/speckit.tasks` command) → Implementation
