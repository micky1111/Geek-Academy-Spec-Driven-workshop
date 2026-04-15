# Agent Request/Response Contract

**Date**: 2026-04-15  
**Reference**: [data-model.md](../data-model.md)

---

## Overview

This contract defines the external interface of the support agent as exposed to the console application. The agent is a stateless request/response processor; conversation state (clarifications, context merging) is managed by the console layer.

---

## Agent Interface

### Agent Handler Signature

**Input**: 
- `SupportRequest` — Customer message + optional clarification context

**Output**: 
- `SupportResponse` — Response type (direct answer, clarification, escalation) + message + optional policy/escalation details

---

## Request Contract

### SupportRequest (Input)

```
{
  "request_id": "uuid-or-timestamp",
  "message": "customer message text, non-empty, <10KB",
  "timestamp": "2026-04-15T10:30:00Z",
  "metadata": {
    "clarification_context": {
      "original_request_id": "uuid",
      "customer_clarifications": [
        {"field": "order_id", "value": "12345"},
        {"field": "charge_date", "value": "2026-03-15"}
      ]
    }
  }
}
```

### Valid Request Examples

**Example 1: Simple refund request**
```json
{
  "request_id": "req-001",
  "message": "I want to request a refund for my recent purchase.",
  "timestamp": "2026-04-15T10:30:00Z"
}
```

**Example 2: Vague billing question (missing details)**
```json
{
  "request_id": "req-002",
  "message": "Why was I charged $50 last week?",
  "timestamp": "2026-04-15T10:31:00Z"
}
```
→ Agent should respond: CLARIFICATION_NEEDED (need order ID and exact date)

**Example 3: Request with merged clarification context**
```json
{
  "request_id": "req-003",
  "message": "Why was I charged $50 last week? My order ID is #456, and the charge was March 15.",
  "timestamp": "2026-04-15T10:31:00Z",
  "metadata": {
    "clarification_context": {
      "original_request_id": "req-002",
      "customer_clarifications": [
        {"field": "order_id", "value": "456"},
        {"field": "charge_date", "value": "2026-03-15"}
      ]
    }
  }
}
```
→ Agent should respond: DIRECT_ANSWER (charge explained from handbook)

---

## Response Contract

### SupportResponse (Output)

```
{
  "request_id": "uuid-or-timestamp",
  "response_type": "direct_answer | clarification_needed | escalation",
  "message": "human-readable response message, <2KB",
  "clarification": {
    "clarification_id": "uuid",
    "questions": ["Question 1?", "Question 2?"],
    "reason": "why clarification is needed",
    "required_fields": ["field_1", "field_2"]
  } | null,
  "escalation_reason": {
    "reason": "policy_exception | emotional_escalation | complexity | handbook_gap | repeated_issue",
    "description": "why escalated",
    "context_summary": "summary of what agent understood and tried",
    "recommended_action": "optional suggestion for human support"
  } | null,
  "handbook_policies_cited": [
    {
      "policy_id": "policy-001",
      "section": "Refund Policy",
      "title": "30-Day Money-Back Guarantee",
      "content": "...",
      "tags": ["refund", "30-day", "money-back"],
      "relevance_score": 0.95
    }
  ] | null,
  "agent_reasoning": "internal reasoning for debugging (not shown to customer)"
}
```

### Response Type Specifics

#### 1. DIRECT_ANSWER

**When**: Agent can answer directly from handbook or standard operating procedure.

**Required Fields**: 
- `message` (customer-facing answer)
- `handbook_policies_cited` (if answer cites policy, e.g., refund/cancellation/billing)

**Optional Fields**: 
- `agent_reasoning` (internal notes; for debugging logs)

**Example: Refund Approval**
```json
{
  "request_id": "req-001",
  "response_type": "direct_answer",
  "message": "Good news! Your order #456 qualifies for a full refund. You purchased on March 1, which is within our 30-day money-back window. To proceed with your refund: 1) Reply with your preferred refund method (original card/bank account), 2) Your refund will be processed within 5-7 business days. Is there anything else I can help with?",
  "handbook_policies_cited": [
    {
      "policy_id": "refund-001",
      "section": "Refund Policy",
      "title": "30-Day Money-Back Guarantee",
      "content": "Purchases within 30 days of purchase are eligible for a full refund...",
      "tags": ["refund", "30-day"],
      "relevance_score": 0.98
    }
  ],
  "agent_reasoning": "Customer order date (March 1) is within 30-day window (today April 15 = 45 days... WAIT, outside window). Should be ESCALATION or policy exception."
}
```

**Wait**: Agent reasoning says this is outside the 30-day window. This response should actually be a policy-based denial or escalation. Example correction:

```json
{
  "request_id": "req-001",
  "response_type": "escalation",
  "message": "Thank you for your refund request. Your purchase on March 1 is 45 days old, which is outside our standard 30-day refund window. However, I'm escalating your request to our support team, as they may be able to help in special circumstances.",
  "escalation_reason": {
    "reason": "policy_exception",
    "description": "Refund request outside 30-day window; potential goodwill exception",
    "context_summary": "Customer requested refund for order #456 purchased March 1 (45 days ago). Outside standard 30-day window. May qualify for exception or alternative resolution.",
    "recommended_action": "Consider customer tenure, complaint tone, and offer alternative (partial refund, discount, etc.)"
  },
  "handbook_policies_cited": [
    {
      "policy_id": "refund-001",
      "section": "Refund Policy",
      "title": "30-Day Money-Back Guarantee",
      "content": "Purchases within 30 days of purchase are eligible for a full refund...",
      "tags": ["refund", "30-day"],
      "relevance_score": 0.98
    }
  ]
}
```

**Example: Billing Explanation**
```json
{
  "request_id": "req-003",
  "response_type": "direct_answer",
  "message": "Your charge of $50 on March 15 was your monthly subscription renewal. Your plan renews automatically on the 15th of each month at $50. Future charges will occur on the same date unless you cancel or change your plan.",
  "handbook_policies_cited": [
    {
      "policy_id": "billing-001",
      "section": "Billing Patterns",
      "title": "Monthly Subscription Renewal",
      "content": "Subscriptions renew automatically...",
      "tags": ["billing", "subscription", "renewal"],
      "relevance_score": 0.99
    }
  ]
}
```

#### 2. CLARIFICATION_NEEDED

**When**: Request lacks critical information needed to proceed.

**Required Fields**: 
- `message` (explanation of what info is needed)
- `clarification` (ClarificationRequest object with specific questions)

**Example: Missing Details for Refund**
```json
{
  "request_id": "req-101",
  "response_type": "clarification_needed",
  "message": "I'd like to help with your refund request. To check your eligibility, I need a bit more information:",
  "clarification": {
    "clarification_id": "clarify-101",
    "questions": [
      "What is your order ID or invoice number?",
      "What is the date of your original purchase?"
    ],
    "reason": "Need order ID and purchase date to verify 30-day refund window and process refund",
    "required_fields": ["order_id", "purchase_date"]
  }
}
```

#### 3. ESCALATION

**When**: Issue is complex, customer is upset, handbook didn't match, or policy exception needed.

**Required Fields**: 
- `message` (explanation for customer, empathetic tone)
- `escalation_reason` (EscalationReason object with reason + context)

**Optional Fields**: 
- `handbook_policies_cited` (policies checked but didn't match)

**Example: Emotional Escalation**
```json
{
  "request_id": "req-201",
  "response_type": "escalation",
  "message": "I appreciate your patience, and I understand how frustrating this is, especially as a long-time customer. Your situation deserves more attention than I can provide. I'm escalating your case to our support specialist, who will be able to help with a resolution. You'll hear back within 2 hours.",
  "escalation_reason": {
    "reason": "emotional_escalation",
    "description": "Customer expressed frustration ('ridiculous') and mentioned 5-year loyalty; tone suggests anger, not just question",
    "context_summary": "Customer has been subscribed for 5 years, recently charged an unexpected fee, feels service quality has declined. Requested escalation implicitly via frustrated tone. Handbook covers standard billing but not loyalty/exception cases.",
    "recommended_action": "Consider goodwill gesture (discount, free month). Review customer's satisfaction history."
  }
}
```

**Example: Handbook Gap**
```json
{
  "request_id": "req-202",
  "response_type": "escalation",
  "message": "Your question about custom contract terms is outside my standard support scope. I'm connecting you with a specialist who can review your specific agreement and provide an accurate answer.",
  "escalation_reason": {
    "reason": "handbook_gap",
    "description": "Customer mentioned 'custom contract' which is not covered in standard handbook",
    "context_summary": "Customer claims to have negotiated custom terms for plan X. Standard handbook only covers default plans (Basic, Pro, Enterprise). Cannot verify custom terms or pricing.",
    "recommended_action": "Contact sales/account management team to verify custom terms"
  }
}
```

---

## Error Cases

### Timeout / LLM API Error

If agent cannot generate response due to timeout or API error:

```json
{
  "request_id": "req-xyz",
  "response_type": "escalation",
  "message": "I'm having trouble processing your request right now. I'm escalating to our support team, who will get back to you shortly.",
  "escalation_reason": {
    "reason": "complexity",
    "description": "Agent processing timed out",
    "context_summary": "LLM API timeout after 30s. Unable to classify intent or generate response.",
    "recommended_action": "Retry or escalate to human"
  }
}
```

### Malformed Request

If `SupportRequest.message` is empty or invalid:

**Agent should raise validation error; console should catch and prompt customer to retry.**

```
Agent.HandleSupportRequest(SupportRequest(message=""))
  → Raises: DataValidationError("Message cannot be empty")
  → Console catches, displays: "Please provide a support request message."
```

---

## Contract Validation Rules

### Agent Responsibility (Must Verify)

1. ✅ Response message is non-empty and <2KB
2. ✅ Response type is one of: DIRECT_ANSWER, CLARIFICATION_NEEDED, ESCALATION
3. ✅ If DIRECT_ANSWER and intent is REFUND/CANCELLATION, at least one handbook policy is cited
4. ✅ If CLARIFICATION_NEEDED, clarification object is present with non-empty questions
5. ✅ If ESCALATION, escalation_reason is present with description and context_summary
6. ✅ handbook_policies_cited (if present) has relevance_score >= 0.5
7. ✅ Clarification questions are specific, not generic (e.g., "What is your order ID?" not "Tell me more")

### Console Responsibility (Must Verify Before Display)

1. ✅ Response.message is not empty (should not display blank response)
2. ✅ Response.request_id matches the request that was sent
3. ✅ If type is CLARIFICATION_NEEDED, display questions and wait for input
4. ✅ If type is ESCALATION, log escalation_reason for human support review
5. ✅ If type is DIRECT_ANSWER, cite handbook policies (e.g., footnotes or bracketed references)

---

## Example Flow Walkthrough

### Scenario: Customer Requests Refund (Incomplete Information)

**Step 1: Console Reads Input**
```
Customer: "I want my money back."
```

**Step 2: Console Creates Request**
```json
{
  "request_id": "req-2026-04-15-001",
  "message": "I want my money back.",
  "timestamp": "2026-04-15T14:22:00Z"
}
```

**Step 3: Agent Processes Request**
- Detect intent: REFUND
- Detect missing info: order_id, purchase_date
- Return: CLARIFICATION_NEEDED

**Step 4: Console Displays Response + Questions**
```
Agent: "I'd like to help with your refund request. To check your eligibility, I need a bit more information:
  1. What is your order ID or invoice number?
  2. What is the date of your original purchase?"
```

**Step 5: Customer Provides Clarification**
```
Customer: "Order #789, purchased on April 5, 2026"
```

**Step 6: Console Merges Context & Resends**
```json
{
  "request_id": "req-2026-04-15-001-clarified",
  "message": "I want my money back. Order #789, purchased on April 5, 2026",
  "timestamp": "2026-04-15T14:23:00Z",
  "metadata": {
    "clarification_context": {
      "original_request_id": "req-2026-04-15-001",
      "customer_clarifications": [
        {"field": "order_id", "value": "789"},
        {"field": "purchase_date", "value": "2026-04-05"}
      ]
    }
  }
}
```

**Step 7: Agent Processes Again**
- Intent: REFUND (confident)
- Entities: order_id = "789", purchase_date = 2026-04-05 (10 days ago, within 30-day window) ✓
- Lookup handbook: Refund Policy (30-day money-back) ✓
- Decision: Approve refund
- Return: DIRECT_ANSWER

**Step 8: Console Displays Final Response**
```
Agent: "Good news! Your order #789 qualifies for a full refund. You purchased on April 5, 2026, which is within our 30-day money-back guarantee. 

To process your refund:
1. Reply with your preferred refund method (original card or bank account)
2. Your refund will be processed within 5-7 business days

Is there anything else I can help with?"

[Footnote: Response based on our 30-Day Money-Back Guarantee policy]
```

---

**Request/Response Contract**: Complete  
**Status**: Ready for implementation
