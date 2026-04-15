from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class DataValidationError(ValueError):
    pass


class HandbookLookupError(RuntimeError):
    pass


class IntentClassificationError(RuntimeError):
    pass


class Intent(Enum):
    Unclear = "Unclear"
    Refund = "Refund"
    Cancellation = "Cancellation"
    BillingExplanation = "BillingExplanation"
    Question = "Question"
    Complaint = "Complaint"


class Sentiment(Enum):
    Neutral = "Neutral"
    Frustrated = "Frustrated"
    Angry = "Angry"
    Confused = "Confused"


class Urgency(Enum):
    Low = "Low"
    Medium = "Medium"
    High = "High"


class ActionTaken(Enum):
    None_ = "None"
    ReplySent = "ReplySent"
    ClarificationRequested = "ClarificationRequested"
    EscalatedToHuman = "EscalatedToHuman"
    RefundTicketCreated = "RefundTicketCreated"
    CancellationTicketCreated = "CancellationTicketCreated"


class ResponseType(Enum):
    DirectAnswer = "DirectAnswer"
    ClarificationNeeded = "ClarificationNeeded"
    Escalation = "Escalation"


class EscalationReasonType(Enum):
    PolicyException = "PolicyException"
    EmotionalEscalation = "EmotionalEscalation"
    Complexity = "Complexity"
    HandbookGap = "HandbookGap"
    RepeatedIssue = "RepeatedIssue"


@dataclass(frozen=True)
class SupportRequest:
    message: str
    request_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if not self.message or len(self.message.strip()) == 0:
            raise DataValidationError("Support request message cannot be empty")
        if len(self.message) > 10_000:
            raise DataValidationError("Support request message exceeds maximum size")


@dataclass(frozen=True)
class ClarificationRequest:
    questions: list[str]
    reason: str
    required_fields: list[str]
    clarification_id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        if not self.questions:
            raise DataValidationError("Clarification questions cannot be empty")
        if len(self.questions) > 5:
            raise DataValidationError("Clarification questions exceed single-round limits")


@dataclass(frozen=True)
class HandbookPolicy:
    policy_id: str
    section: str
    title: str
    content: str
    tags: list[str]
    relevance_score: float = 1.0


@dataclass(frozen=True)
class EscalationReason:
    reason: EscalationReasonType
    description: str
    context_summary: str
    recommended_action: str = ""


@dataclass(frozen=True)
class SupportResponse:
    request_id: str
    response_type: ResponseType
    message: str
    clarification: ClarificationRequest | None = None
    escalation_reason: EscalationReason | None = None
    handbook_policies_cited: list[HandbookPolicy] | None = None
    agent_reasoning: str = ""

    def __post_init__(self) -> None:
        if not self.message or len(self.message.strip()) == 0:
            raise DataValidationError("Support response message cannot be empty")
        if self.response_type == ResponseType.ClarificationNeeded and not self.clarification:
            raise DataValidationError("Clarification response missing clarification payload")
        if self.response_type == ResponseType.Escalation and not self.escalation_reason:
            raise DataValidationError("Escalation response missing escalation reason")


@dataclass(frozen=True)
class SupportRequestResult:
    intent: Intent
    sentiment: Sentiment
    urgency: Urgency
    reasoning: list[str]
    action_taken: ActionTaken
    customer_facing_response: str
    recommended_next_action: str | None
    response_type: ResponseType = ResponseType.DirectAnswer
    clarification_request: ClarificationRequest | None = None
    escalation_reason: EscalationReason | None = None
    cited_policies: list[HandbookPolicy] | None = None
