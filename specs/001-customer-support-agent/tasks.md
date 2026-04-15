# Tasks: Customer Support Agentic System

**Input**: Design documents from `specs/001-customer-support-agent/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Implementation Target**: Python skeleton in `support-agent-python/`

**Tests**: Include unit/integration tests because specification defines independent tests per story and constitution requires agent integration testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare Python project dependencies and test scaffold.

- [x] T001 Add MAF and runtime dependencies in support-agent-python/requirements.txt
- [x] T002 Create pytest configuration in support-agent-python/pytest.ini
- [x] T003 [P] Create test package marker in support-agent-python/tests/__init__.py
- [x] T004 [P] Create unit test package marker in support-agent-python/tests/unit/__init__.py
- [x] T005 [P] Create integration test package marker in support-agent-python/tests/integration/__init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core plumbing that must exist before any user story implementation.

**CRITICAL**: No user story work starts before this phase is complete.

- [x] T006 Define core request/response entities in support-agent-python/app/models.py
- [x] T007 Implement handbook section parser utility in support-agent-python/app/processor.py
- [x] T008 Implement handbook lookup tool function in support-agent-python/app/agent.py
- [x] T009 [P] Add Azure OpenAI environment validation in support-agent-python/main.py
- [x] T010 [P] Add structured error classes for validation and lookup failures in support-agent-python/app/models.py
- [x] T011 Implement base request processing pipeline (parse -> classify -> route) in support-agent-python/app/processor.py
- [x] T012 Wire async console loop to processor entrypoint in support-agent-python/main.py
- [x] T013 Add shared integration test fixtures for handbook and sample requests in support-agent-python/tests/integration/conftest.py

**Checkpoint**: Foundation ready for independent user story delivery.

---

## Phase 3: User Story 1 - Simple Clarification Request (Priority: P1) 🎯 MVP

**Goal**: Ask one specific clarification round for incomplete requests, then continue without re-asking.

**Independent Test**: Submit an incomplete billing/refund request, receive targeted clarification questions, provide details once, and receive a progressed response without repeated clarification prompts.

### Tests for User Story 1

- [x] T014 [P] [US1] Add unit tests for missing-field detection in support-agent-python/tests/unit/test_clarification_detection.py
- [x] T015 [P] [US1] Add integration test for one-round clarification flow in support-agent-python/tests/integration/test_us1_clarification_flow.py

### Implementation for User Story 1

- [x] T016 [US1] Implement missing information extraction rules in support-agent-python/app/processor.py
- [x] T017 [US1] Implement clarification question builder with required_fields in support-agent-python/app/agent.py
- [x] T018 [US1] Persist single-round clarification context merge in support-agent-python/app/console_ui.py
- [x] T019 [US1] Prevent repeated clarification questions for same request in support-agent-python/app/processor.py
- [x] T020 [US1] Render clarification prompts with rationale in support-agent-python/app/renderer.py

**Checkpoint**: US1 independently functional and testable.

---

## Phase 4: User Story 2 - Policy-Aware Refund/Cancellation Handling (Priority: P1)

**Goal**: Handle refund/cancellation requests strictly from handbook policy and escalate edge cases.

**Independent Test**: Submit refund/cancellation scenarios (in-policy, out-of-policy, partial eligibility, custom-contract edge case) and verify policy-grounded responses or escalation.

### Tests for User Story 2

- [x] T021 [P] [US2] Add unit tests for refund/cancellation policy matching in support-agent-python/tests/unit/test_refund_cancellation_policy.py
- [x] T022 [P] [US2] Add integration test for refund/cancellation decision flow in support-agent-python/tests/integration/test_us2_refund_cancellation_flow.py

### Implementation for User Story 2

- [x] T023 [US2] Implement refund policy lookup query strategy in support-agent-python/app/agent.py
- [x] T024 [US2] Implement cancellation policy lookup query strategy in support-agent-python/app/agent.py
- [x] T025 [US2] Implement policy-window and exception routing logic in support-agent-python/app/processor.py
- [x] T026 [US2] Add handbook citation injection for refund/cancellation responses in support-agent-python/app/renderer.py
- [x] T027 [US2] Implement policy-exception escalation payload construction in support-agent-python/app/models.py

**Checkpoint**: US2 independently functional and testable.

---

## Phase 5: User Story 3 - Billing/Charge Explanation (Priority: P1)

**Goal**: Explain charges using handbook billing patterns and escalate unmatched billing cases.

**Independent Test**: Submit known billing scenarios and receive clear explanations; submit unknown charge scenario and receive escalation with context.

### Tests for User Story 3

- [x] T028 [P] [US3] Add unit tests for billing pattern classification in support-agent-python/tests/unit/test_billing_pattern_classification.py
- [x] T029 [P] [US3] Add integration test for billing explanation flow in support-agent-python/tests/integration/test_us3_billing_explanations.py

### Implementation for User Story 3

- [x] T030 [US3] Implement billing-specific entity extraction (amount/date/descriptor) in support-agent-python/app/processor.py
- [x] T031 [US3] Implement billing handbook query and ranking rules in support-agent-python/app/agent.py
- [x] T032 [US3] Implement known-pattern explanation composer in support-agent-python/app/renderer.py
- [x] T033 [US3] Implement unmatched-billing escalation route in support-agent-python/app/processor.py
- [x] T034 [US3] Add duplicate-charge false-positive handling from handbook in support-agent-python/app/processor.py

**Checkpoint**: US3 independently functional and testable.

---

## Phase 6: User Story 4 - General Account/Feature Questions (Priority: P2)

**Goal**: Answer routine account/feature questions from handbook and ask narrowing clarification when multiple sections match.

**Independent Test**: Ask feature/account questions covered in handbook and receive direct instructions; ambiguous query prompts targeted narrowing question; unknown question escalates.

### Tests for User Story 4

- [x] T035 [P] [US4] Add unit tests for feature/account handbook matching in support-agent-python/tests/unit/test_feature_account_matching.py
- [x] T036 [P] [US4] Add integration test for general question handling in support-agent-python/tests/integration/test_us4_general_questions.py

### Implementation for User Story 4

- [x] T037 [US4] Implement feature/account intent branch in support-agent-python/app/processor.py
- [x] T038 [US4] Implement multi-match narrowing clarification generation in support-agent-python/app/agent.py
- [x] T039 [US4] Implement direct instruction rendering for handbook FAQ answers in support-agent-python/app/renderer.py
- [x] T040 [US4] Implement handbook-gap escalation for general questions in support-agent-python/app/processor.py

**Checkpoint**: US4 independently functional and testable.

---

## Phase 7: User Story 5 - Escalation for Complex or Emotional Cases (Priority: P2)

**Goal**: Detect emotional/complex requests and escalate with full context.

**Independent Test**: Submit angry/complex requests and verify escalation is triggered with reason, context summary, and recommended action.

### Tests for User Story 5

- [x] T041 [P] [US5] Add unit tests for emotional signal detection in support-agent-python/tests/unit/test_emotional_signal_detection.py
- [x] T042 [P] [US5] Add integration test for escalation routing and payload in support-agent-python/tests/integration/test_us5_escalation_routing.py

### Implementation for User Story 5

- [x] T043 [US5] Implement keyword-based escalation signal detection in support-agent-python/app/processor.py
- [x] T044 [US5] Implement LLM sentiment scoring integration for escalation confidence in support-agent-python/app/agent.py
- [x] T045 [US5] Implement escalation reason taxonomy mapping in support-agent-python/app/models.py
- [x] T046 [US5] Render empathetic escalation response with next-steps expectation in support-agent-python/app/renderer.py

**Checkpoint**: US5 independently functional and testable.

---

## Phase 8: User Story 6 - Seamless Single-Response Experience (Priority: P2)

**Goal**: Ensure final responses feel coherent, contextual, and personalized across all branches.

**Independent Test**: For clarification, direct answer, and escalation branches, verify each response summarizes understanding, action taken, and next step in one coherent narrative.

### Tests for User Story 6

- [x] T047 [P] [US6] Add unit tests for response coherence template selection in support-agent-python/tests/unit/test_response_coherence.py
- [x] T048 [P] [US6] Add integration test for single-conversation narrative continuity in support-agent-python/tests/integration/test_us6_single_conversation_experience.py

### Implementation for User Story 6

- [x] T049 [US6] Implement conversation summary synthesis from request context in support-agent-python/app/renderer.py
- [x] T050 [US6] Implement consistent response envelope (understood -> action -> next step) in support-agent-python/app/renderer.py
- [x] T051 [US6] Integrate branch-specific personalization signals into final message generation in support-agent-python/app/processor.py

**Checkpoint**: US6 independently functional and testable.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency, performance, and docs across all user stories.

- [x] T052 [P] Add end-to-end regression tests using sample requests in support-agent-python/tests/integration/test_regression_sample_requests.py
- [x] T053 [P] Add unit tests for handbook parser robustness in support-agent-python/tests/unit/test_handbook_parser_robustness.py
- [x] T054 Optimize handbook lookup performance for <5s response target in support-agent-python/app/agent.py
- [x] T055 Update run instructions and troubleshooting notes in support-agent-python/README.md
- [x] T056 Run quickstart validation and record expected command outputs in specs/001-customer-support-agent/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): No dependencies.
- Foundational (Phase 2): Depends on Setup completion; blocks all user stories.
- User Stories (Phases 3-8): Depend on Foundational completion.
- Polish (Phase 9): Depends on completion of desired user stories.

### User Story Dependencies

- US1 (P1): Starts after Foundational; no dependency on other stories.
- US2 (P1): Starts after Foundational; independent, but reuses shared clarification/context infrastructure.
- US3 (P1): Starts after Foundational; independent, shares handbook lookup utilities.
- US4 (P2): Starts after Foundational; independent, reuses handbook lookup utilities.
- US5 (P2): Starts after Foundational; independent, reuses intent/entity extraction.
- US6 (P2): Starts after US1-US5 because it unifies response style across all branches.

### Recommended Completion Order

1. Phase 1 -> Phase 2
2. Phase 3 (US1 MVP baseline)
3. Phase 4 and Phase 5 (US2/US3, both P1)
4. Phase 6 and Phase 7 (US4/US5, both P2)
5. Phase 8 (US6 coherence layer)
6. Phase 9 polish

---

## Parallel Opportunities

- Setup parallel tasks: T003, T004, T005
- Foundational parallel tasks: T009, T010 (after T006 starts)
- US1 parallel tests: T014, T015
- US2 parallel tests: T021, T022
- US3 parallel tests: T028, T029
- US4 parallel tests: T035, T036
- US5 parallel tests: T041, T042
- US6 parallel tests: T047, T048
- Polish parallel tasks: T052, T053

---

## Parallel Example: User Story 2

```bash
# Run US2 tests in parallel
Task: T021 [US2] support-agent-python/tests/unit/test_refund_cancellation_policy.py
Task: T022 [US2] support-agent-python/tests/integration/test_us2_refund_cancellation_flow.py

# Then implement independent policy query branches
Task: T023 [US2] support-agent-python/app/agent.py
Task: T024 [US2] support-agent-python/app/agent.py
```

## Parallel Example: User Story 5

```bash
# Run US5 tests in parallel
Task: T041 [US5] support-agent-python/tests/unit/test_emotional_signal_detection.py
Task: T042 [US5] support-agent-python/tests/integration/test_us5_escalation_routing.py

# Implement split model/renderer work in parallel
Task: T045 [US5] support-agent-python/app/models.py
Task: T046 [US5] support-agent-python/app/renderer.py
```

---

## Implementation Strategy

### MVP First (US1 only)

1. Complete Setup and Foundational phases.
2. Deliver US1 clarification flow end-to-end.
3. Validate independently via T015 integration test.
4. Demo clarification behavior before expanding scope.

### Incremental Delivery

1. Add US2 and US3 for core policy/billing value (P1 stories).
2. Add US4 and US5 for routine questions and escalation robustness.
3. Add US6 to unify voice and continuity.
4. Finalize with polish and regression suite.

### Execution Note

- Write tests first in each story phase and confirm they fail before implementation.
- Keep changes inside Python skeleton only; do not mirror into C# skeleton.
- Commit after each user story checkpoint.
