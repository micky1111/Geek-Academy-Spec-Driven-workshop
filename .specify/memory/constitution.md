<!-- 
SYNC IMPACT REPORT
==================
Version Change: Initial → 1.0.0
New Principles:
  • I. Spec-First: Every agent/feature begins with a specification
  • II. Framework Fidelity: Strict adherence to Microsoft Agent Framework (MAF)
  • III. Skeleton Independence: C# and Python implementations remain separate
  • IV. Agent Testability: Agent behavior must be independently testable
  • V. Integration Testing: Real framework interactions must be verified

Added Sections:
  • Framework & Dependencies (authoritative sources, version management)
  • Development Workflow (spec-driven process)

Templates Updated:
  ✅ spec-template.md (constitution check will validate framework alignment)
  ✅ plan-template.md (Technical Context section references MAF versions)
  ✅ tasks-template.md (task categorization aligns with testing tiers)

No Removed Sections.
No Deferred TODOs.
-->

# Agentic Systems Workshop Constitution

## Core Principles

### I. Spec-First Development
Every agent feature, enhancement, or capability MUST begin with a formal specification in the `.specify/` workflow. No code implementation precedes the specification document. Specifications MUST include:
- User scenarios with independent test criteria
- Clear acceptance scenarios using Given/When/Then language
- Technology decisions documented and justified
- Architecture decisions recorded before implementation

**Rationale**: The spec-first approach ensures alignment on requirements before engineering effort is invested, reducing rework and enabling parallel team discussions.

### II. Framework Fidelity (Non-Negotiable)
All Microsoft Agent Framework (MAF) implementations MUST strictly follow current official documentation. Engineers MUST NOT:
- Invent or assume APIs based on semantic kernel or autogen pretraining
- Use framework APIs without verifying against official docs or source
- Depend on examples from older frameworks (autogen, semantic kernel); MAF is a distinct framework with its own API surface

**Required Actions**:
- Verify current package versions on NuGet (C#) or PyPI (Python) before implementation
- Read authoritative sources: <https://github.com/microsoft/agent-framework>, <https://learn.microsoft.com/en-us/agent-framework/>
- When in doubt, verify against official source code before writing code

**Rationale**: MAF merged and renamed concepts from prior frameworks. Assumptions based on older APIs will cause failures and wasted debugging cycles. Official sources are the single source of truth.

### III. Skeleton Independence
This repository contains two independent implementations: `support-agent-csharp/` and `support-agent-python/`. Code MUST remain segregated within these folders. 

- Engineers MUST confirm which skeleton they are working on before editing
- Code reviews MUST verify no cross-skeleton mirroring unless explicitly authorized
- Each skeleton may use language-native patterns and idioms (e.g., Python async, C# Tasks)
- Framework API usage may differ appropriately per language (e.g., C# Tasks vs Python AsyncIO)

**Rationale**: Separate skeletons allow participants to learn language-specific agent patterns without pollution or forced parity.

### IV. Agent Testability
Every agent component (orchestrator, handler, processor) MUST expose independently testable behavior. Agent tests MUST:
- Verify correct tool invocation and message passing
- Use sample data (support handbook, request samples) as test fixtures
- Execute without external service dependencies (mock or stub external integrations)
- Produce reproducible, deterministic results

**Prohibited**: Tests that require live API calls, real-time inference, or interactive debugging to pass.

**Rationale**: Testable agents enable confidence in agent behavior, faster iteration cycles, and reproducible demos.

### V. Integration Testing  
Agent features interconnecting with MAF, tools, or the console UI MUST include integration tests verifying the full contract:
- New agent orchestration logic
- Tool invocation chains
- Request/response round-trips via sample data
- Error handling for malformed or edge-case inputs

**Rationale**: Integration tests catch issues that unit tests cannot (e.g., serialization mismatches, asynchrony problems) before user-facing deployment.

## Framework & Dependencies

**Authoritative Sources**:
- Microsoft Agent Framework: <https://github.com/microsoft/agent-framework>
  - .NET source: <https://github.com/microsoft/agent-framework/tree/main/dotnet>
  - Python source: <https://github.com/microsoft/agent-framework/tree/main/python>
- Release notes: <https://github.com/microsoft/agent-framework/releases>
- Official docs: <https://learn.microsoft.com/en-us/agent-framework/>
- Official samples: <https://github.com/microsoft/Agent-Framework-Samples>

**Version Management**:
- C# skeleton: Check NuGet for latest MAF package versions before implementation
- Python skeleton: Check PyPI for latest MAF package versions before implementation
- Document the MAF version and rationale in `plan.md` Technical Context section (e.g., "MAF 0.5.x required for streaming agent support")

## Development Workflow

1. **Specification** (`/speckit.specify`): User describes a feature → spec.md created with user scenarios, acceptance criteria, and technology decisions
2. **Planning** (`/speckit.plan`): Specification reviewed → Implementation plan created with constitution validation, technical context, and task breakdown
3. **Task Generation** (`/speckit.tasks`): Implementation tasks created with dependencies, testing tiers (unit, integration), and framework-specific guidance
4. **Implementation** (`/speckit.implement`): Tasks executed according to skeleton (C# or Python) with agent tests written alongside code
5. **Validation**: All tests pass, agent behavior verified against sample data, integration tests exercise framework contracts

**Constitution Check Gate**: Every plan MUST verify:
- ✅ Feature is spec-first (spec.md exists and is complete)
- ✅ MAF version documented and sourced from official releases
- ✅ Skeleton confirmed (C# or Python, not both)
- ✅ Integration test strategy includes agent behavior + framework contracts

## Governance

This constitution supersedes all prior practices and guidance. All pull requests MUST:
- Comply with all five core principles (Spec-First, Framework Fidelity, Skeleton Independence, Agent Testability, Integration Testing)
- Include justification for any deviation (open as a new issue for constitutional amendment)
- Pass constitution checks in the implementation plan before task generation

**Amendments**: Constitutional amendments require:
- Issue documenting the need for change and impact analysis
- Amendment proposal with new wording and rationale
- Team approval via PR review
- Version bump: MAJOR for backward-incompatible changes (principle removal/redefinition); MINOR for new principles; PATCH for clarifications

**Version**: 1.0.0 | **Ratified**: 2026-04-15 | **Last Amended**: 2026-04-15
