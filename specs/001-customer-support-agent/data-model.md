# Phase 1 Design: Data Model

**Date**: 2026-04-15  
**Feature**: Customer Support Agentic System  
**Reference**: [research.md](research.md)

---

## Overview

This document defines the core data entities for the customer support agent system, their relationships, validation rules, and state transitions.

---

## Core Entities

### 1. SupportRequest

**Description**: Incoming customer message and metadata.

**Fields**:
- `request_id: str` — Unique request identifier (UUID or timestamp-based)
- `message: str` — Customer's message (non-empty, plain text or structured formats accepted)
- `timestamp: datetime` — When request was received
- `metadata: dict` — Optional (order ID, customer ID, session ID if available)

**Validation**:
- `message` must be non-empty and <10,000 characters
- `request_id` must be unique within session
- `timestamp` defaults to current UTC time if not provided

**Python Definition**:
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class SupportRequest:
    message: str
    request_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if not self.message or len(self.message) > 10000:
            raise ValueError("Message must be non-empty and <10KB")
        self.request_id = self.request_id or str(uuid.uuid4())
        self.timestamp = self.timestamp or datetime.utcnow()
```

**C# Definition**:
```csharp
public record SupportRequest
{
    public string Message { get; init; }
    public string RequestId { get; init; } = Guid.NewGuid().ToString();
    public DateTime Timestamp { get; init; } = DateTime.UtcNow;
    public Dictionary<string, object>? Metadata { get; init; }
}
```

---

### 2. CustomerIntent

**Description**: Classified intent/category of the customer's request.

**Enum Values**:
- `REFUND` — Customer requests a refund
- `CANCELLATION` — Customer wants to cancel subscription/plan
- `BILLING_EXPLANATION` — Customer confused about a charge or billing
- `FEATURE_QUESTION` — General question about features, account, or company
- `COMPLAINT_ESCALATION` — Emotional or complex case requiring human attention
- `UNCLEAR` — Intent could not be determined; clarification needed

**Fields**:
- `intent: CustomerIntent` — Classified category (enum)
- `confidence: float` — Confidence score (0.0–1.0); confidence >= 0.7 preferred for high-confidence classifications
- `reasoning: str` — Brief explanation of why this intent was chosen (for debugging)
- `detected_entities: dict` — Extracted entities (order ID, charge amount, date, plan name, emotion signals)

**Python Definition**:
```python
from enum import Enum

class IntentType(Enum):
    REFUND = "refund"
    CANCELLATION = "cancellation"
    BILLING_EXPLANATION = "billing_explanation"
    FEATURE_QUESTION = "feature_question"
    COMPLAINT_ESCALATION = "complaint_escalation"
    UNCLEAR = "unclear"

@dataclass
class CustomerIntent:
    intent: IntentType
    confidence: float
    reasoning: str
    detected_entities: Dict[str, Any]
    
    def __post_init__(self):
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("Confidence must be between 0 and 1")
```

**C# Definition**:
```csharp
public enum IntentType
{
    Refund,
    Cancellation,
    BillingExplanation,
    FeatureQuestion,
    ComplaintEscalation,
    Unclear
}

public record CustomerIntent
{
    public IntentType Intent { get; init; }
    public float Confidence { get; init; }
    public string Reasoning { get; init; }
    public Dictionary<string, object> DetectedEntities { get; init; }
}
```

---

### 3. ClarificationRequest

**Description**: Specific missing-information questions asked by agent when request is incomplete.

**Fields**:
- `clarification_id: str` — Unique ID for this clarification round
- `questions: list[str]` — Specific questions (e.g., ["What is your order ID?", "When was the charge date?"])
- `reason: str` — Why clarification is needed (e.g., "Cannot determine refund eligibility without order ID and purchase date")
- `required_fields: list[str]` — Field names being asked for (e.g., ["order_id", "charge_date"])

**Validation**:
- `questions` must be non-empty and <5 items (spec: one clarification round)
- Each question must be specific (not generic "tell me more")
- `required_fields` must align with questions

**Python Definition**:
```python
@dataclass
class ClarificationRequest:
    clarification_id: str
    questions: List[str]
    reason: str
    required_fields: List[str]
    
    def __post_init__(self):
        if not self.questions or len(self.questions) > 5:
            raise ValueError("Clarification must have 1-5 questions")
        if not all(q and len(q) < 200 for q in self.questions):
            raise ValueError("Questions must be non-empty and <200 chars")
```

**C# Definition**:
```csharp
public record ClarificationRequest
{
    public string ClarificationId { get; init; } = Guid.NewGuid().ToString();
    public List<string> Questions { get; init; }
    public string Reason { get; init; }
    public List<string> RequiredFields { get; init; }
}
```

---

### 4. HandbookPolicy

**Description**: Company policy rule extracted from support handbook.

**Fields**:
- `policy_id: str` — Unique identifier within handbook
- `section: str` — Handbook section (e.g., "Refund Policy", "Billing FAQ")
- `title: str` — Policy title (e.g., "30-Day Money-Back Guarantee")
- `content: str` — Markdown content of policy
- `tags: list[str]` — Keywords for matching (e.g., ["refund", "30-day", "money-back"])

**No Validation Beyond Content Length**: Handbook is authoritative; validation happens at lookup time (tool validates policy applicability to customer's situation).

**Python Definition**:
```python
@dataclass
class HandbookPolicy:
    policy_id: str
    section: str
    title: str
    content: str
    tags: List[str]
    relevance_score: float = 1.0  # Set by lookup tool when matching
```

**C# Definition**:
```csharp
public record HandbookPolicy
{
    public string PolicyId { get; init; }
    public string Section { get; init; }
    public string Title { get; init; }
    public string Content { get; init; }
    public List<string> Tags { get; init; }
    public float RelevanceScore { get; init; } = 1.0f;
}
```

---

### 5. SupportResponse

**Description**: Agent's final response to the customer (direct answer, clarification request, or escalation).

**Enum for Response Type**:
- `DIRECT_ANSWER` — Agent can answer directly (e.g., refund approved, charge explained)
- `CLARIFICATION_NEEDED` — Agent needs more information (returns ClarificationRequest)
- `ESCALATION` — Agent cannot handle; escalating to human support

**Fields**:
- `request_id: str` — Link to original SupportRequest
- `response_type: ResponseType` — DIRECT_ANSWER | CLARIFICATION_NEEDED | ESCALATION
- `message: str` — Human-readable response message to display to customer
- `clarification: Optional[ClarificationRequest]` — If response_type == CLARIFICATION_NEEDED
- `escalation_reason: Optional[EscalationReason]` — If response_type == ESCALATION
- `handbook_policies_cited: list[HandbookPolicy]` — Policies used to generate answer (for DIRECT_ANSWER)
- `agent_reasoning: str` — Internal reasoning (for debugging; not shown to customer)

**Validation**:
- `response_type` determines which optional fields are required
- If DIRECT_ANSWER and intent was refund/cancellation, at least one handbook policy must be cited
- `message` must be non-empty and <2000 characters

**Python Definition**:
```python
from enum import Enum
from typing import Optional, List

class ResponseType(Enum):
    DIRECT_ANSWER = "direct_answer"
    CLARIFICATION_NEEDED = "clarification_needed"
    ESCALATION = "escalation"

@dataclass
class SupportResponse:
    request_id: str
    response_type: ResponseType
    message: str
    clarification: Optional[ClarificationRequest] = None
    escalation_reason: Optional['EscalationReason'] = None
    handbook_policies_cited: Optional[List[HandbookPolicy]] = None
    agent_reasoning: str = ""
    
    def __post_init__(self):
        if not self.message or len(self.message) > 2000:
            raise ValueError("Message must be non-empty and <2KB")
        
        if self.response_type == ResponseType.CLARIFICATION_NEEDED and not self.clarification:
            raise ValueError("CLARIFICATION_NEEDED response must include clarification")
        
        if self.response_type == ResponseType.ESCALATION and not self.escalation_reason:
            raise ValueError("ESCALATION response must include escalation_reason")
```

**C# Definition**:
```csharp
public enum ResponseType
{
    DirectAnswer,
    ClarificationNeeded,
    Escalation
}

public record SupportResponse
{
    public string RequestId { get; init; }
    public ResponseType ResponseType { get; init; }
    public string Message { get; init; }
    public ClarificationRequest? Clarification { get; init; }
    public EscalationReason? EscalationReason { get; init; }
    public List<HandbookPolicy>? HandbookPoliciesCited { get; init; }
    public string AgentReasoning { get; init; } = "";
}
```

---

### 6. EscalationReason

**Description**: Why agent escalated a case to human support.

**Enum Values**:
- `POLICY_EXCEPTION` — Request doesn't cleanly match handbook; edge case or custom contract
- `EMOTIONAL_ESCALATION` — Customer expressed anger, frustration, or urgency
- `COMPLEXITY` — Multi-part request, conflicting information, or requires negotiation
- `HANDBOOK_GAP` — Issue not covered in handbook; no clear answer exists
- `REPEATED_ISSUE` — Customer mentions same problem/complaint multiple times

**Fields**:
- `reason: EscalationReason` — Enum value
- `description: str` — Human-readable explanation of why escalation triggered
- `context_summary: str` — Summary of customer's situation for human support (what was understood, what handbook was checked, why it failed)
- `recommended_action: str` — Optional suggestion for human support (e.g., "Consider policy exception", "Offer 50% refund as goodwill")

**Python Definition**:
```python
from enum import Enum

class EscalationReasonType(Enum):
    POLICY_EXCEPTION = "policy_exception"
    EMOTIONAL_ESCALATION = "emotional_escalation"
    COMPLEXITY = "complexity"
    HANDBOOK_GAP = "handbook_gap"
    REPEATED_ISSUE = "repeated_issue"

@dataclass
class EscalationReason:
    reason: EscalationReasonType
    description: str
    context_summary: str
    recommended_action: str = ""
```

**C# Definition**:
```csharp
public enum EscalationReasonType
{
    PolicyException,
    EmotionalEscalation,
    Complexity,
    HandbookGap,
    RepeatedIssue
}

public record EscalationReason
{
    public EscalationReasonType Reason { get; init; }
    public string Description { get; init; }
    public string ContextSummary { get; init; }
    public string RecommendedAction { get; init; } = "";
}
```

---

## Data Relationships

```
SupportRequest
    ├── CustomerIntent (classified from message)
    ├── ClarificationRequest (generated if intent unclear/info missing)
    │   └── [Customer provides clarification_response]
    │       └── SupportRequest + ClarificationContext (merged for second agent call)
    └── SupportResponse
        ├── HandbookPolicy[] (cited if DIRECT_ANSWER to refund/cancellation/billing)
        ├── ClarificationRequest (if CLARIFICATION_NEEDED)
        └── EscalationReason (if ESCALATION)
```

---

## State Transitions

### Happy Path: Direct Answer

```
SupportRequest (message: "Refund question")
    ↓
CustomerIntent (REFUND, confidence: 0.9, entities: {order_id: "123"})
    ↓
HandbookPolicy lookup: "Refund Policy" matches
    ↓
SupportResponse (type: DIRECT_ANSWER, 
                 message: "Your order #123 qualifies for refund...",
                 policies_cited: [HandbookPolicy(...)])
    ↓
DISPLAY TO CUSTOMER
```

### Clarification Path

```
SupportRequest (message: "Why was I charged?")
    ↓
CustomerIntent (BILLING_EXPLANATION, confidence: 0.8, missing: {order_id, date})
    ↓
SupportResponse (type: CLARIFICATION_NEEDED,
                 message: "To help, I need...",
                 clarification: ClarificationRequest(questions: [...]))
    ↓
DISPLAY TO CUSTOMER → WAIT FOR INPUT
    ↓
Customer response: "Order #456, March 15"
    ↓
[Console merges requests]
    ↓
SupportRequest (message: combined + clarification context)
    ↓
[Agent processes again with full context]
    ↓
SupportResponse (type: DIRECT_ANSWER, 
                 message: "Your charge on March 15 was...")
    ↓
DISPLAY TO CUSTOMER
```

### Escalation Path

```
SupportRequest (message: "I've been a customer 5 years and this is ridiculous!")
    ↓
CustomerIntent (COMPLAINT_ESCALATION, confidence: 0.95, signals: [anger, loyalty_mention])
    ↓
SupportResponse (type: ESCALATION,
                 message: "I understand you're frustrated...",
                 escalation_reason: EscalationReason(
                     reason: EMOTIONAL_ESCALATION,
                     description: "Customer expressed frustration...",
                     context_summary: "Long-time customer experiencing issue..."
                 ))
    ↓
DISPLAY TO CUSTOMER + LOG FOR HUMAN SUPPORT
```

---

## Validation & Error Handling

### DataValidationError

Raised when entity fields violate constraints (e.g., message too long, confidence out of range). **Agent should not catch and ignore; let crash propagate.** During testing, use fixtures that pass validation.

### IntentClassificationError

Raised when intent cannot be classified with reasonable confidence. **Agent should catch and return INTENT_UNCLEAR**, triggering clarification or escalation.

### HandbookLookupError

Raised when handbook lookup tool fails (e.g., malformed query, IO error reading handbook file). **Agent should catch and escalate with HANDBOOK_GAP reason**, informing customer "I couldn't check our policies; escalating..."

---

## Testing Considerations

### Unit Test Fixtures

- **Valid SupportRequest**: `SupportRequest(message="I want a refund")`
- **Invalid SupportRequest**: `SupportRequest(message="")` → ValueError
- **Valid CustomerIntent**: `CustomerIntent(intent=REFUND, confidence=0.95, ...)`
- **Invalid CustomerIntent**: `CustomerIntent(intent=REFUND, confidence=1.5)` → ValueError

### Integration Test Fixtures

- **Refund Scenario**: SupportRequest → CustomerIntent (REFUND) → HandbookPolicy (cited) → SupportResponse (DIRECT_ANSWER) ✓
- **Clarification Scenario**: SupportRequest (missing order ID) → SupportResponse (CLARIFICATION_NEEDED) → [merge] → SupportResponse (DIRECT_ANSWER) ✓
- **Escalation Scenario**: SupportRequest (angry) → SupportResponse (ESCALATION, EMOTIONAL_ESCALATION) ✓

---

**Data Model Status**: Complete  
**Next**: [contracts/request-response.md](contracts/request-response.md) and [contracts/handbook-lookup.md](contracts/handbook-lookup.md) will define MAF agent interfaces
