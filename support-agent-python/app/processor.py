from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from app.agent import SupportAgent
from app.models import (
    ActionTaken,
    EscalationReason,
    EscalationReasonType,
    Intent,
    Sentiment,
    SupportRequest,
    SupportRequestResult,
    Urgency,
    ResponseType,
)
from app import renderer


def parse_handbook_sections(handbook_content: str) -> list[dict[str, Any]]:
    sections: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for line in handbook_content.splitlines():
        if line.startswith("## "):
            title = line[3:].strip()
            current = {
                "policy_id": hashlib.md5(title.encode("utf-8")).hexdigest()[:10],
                "section": title,
                "title": title,
                "content": "",
                "tags": _extract_tags(title),
            }
            sections.append(current)
            continue

        if current is not None:
            current["content"] += f"{line}\n"

    return sections


class SupportRequestProcessor:
    def __init__(self, handbook_path: Path | None = None) -> None:
        self._agent = SupportAgent()
        self._handbook_path = handbook_path or Path(__file__).resolve().parent.parent / "data" / "support_handbook.md"
        self._handbook_sections = parse_handbook_sections(self._handbook_path.read_text(encoding="utf-8"))

    async def process(
        self,
        customer_message: str,
        clarification_context: dict[str, Any] | None = None,
    ) -> SupportRequestResult:
        request = SupportRequest(message=customer_message, metadata=clarification_context or {})
        entities = self._extract_entities(request.message)
        intent = self._classify_intent(request.message)
        sentiment_score = await self._agent.score_sentiment(request.message)
        sentiment = self._sentiment_from_score(sentiment_score)
        urgency = self._classify_urgency(request.message, sentiment_score)

        reasoning = [
            f"Classified intent as {intent.value}.",
            f"Detected sentiment {sentiment.value} (score {sentiment_score:.2f}).",
            f"Extracted entities: {', '.join(sorted(entities.keys())) or 'none' }.",
        ]

        escalation = self._explicit_escalation_reason(request.message)
        if escalation is not None:
            response = renderer.render_empathetic_escalation(
                "I understand this is frustrating, and I want to get this resolved quickly.",
                "I am escalating this to a senior support specialist now.",
            )
            return SupportRequestResult(
                intent=Intent.Complaint,
                sentiment=Sentiment.Angry,
                urgency=Urgency.High,
                reasoning=reasoning + ["Escalation triggered by explicit escalation signal."],
                action_taken=ActionTaken.EscalatedToHuman,
                customer_facing_response=response,
                recommended_next_action="Senior support SLA is approximately 4 business hours.",
                response_type=ResponseType.Escalation,
                escalation_reason=escalation,
            )

        missing_fields = self._missing_fields(intent, entities)
        clarification_round_used = bool((clarification_context or {}).get("clarification_round_used"))
        if missing_fields and not clarification_round_used:
            clarification = self._agent.build_clarification_request(missing_fields, intent)
            prompt = renderer.render_clarification_prompt(clarification, clarification.reason)
            return SupportRequestResult(
                intent=intent,
                sentiment=sentiment,
                urgency=urgency,
                reasoning=reasoning + [f"Missing fields require clarification: {', '.join(missing_fields)}."],
                action_taken=ActionTaken.ClarificationRequested,
                customer_facing_response=prompt,
                recommended_next_action="Collect clarification once, then reprocess with merged context.",
                response_type=ResponseType.ClarificationNeeded,
                clarification_request=clarification,
            )

        if missing_fields and clarification_round_used:
            escalation_reason = EscalationReason(
                reason=EscalationReasonType.Complexity,
                description="Required details still missing after clarification round.",
                context_summary="Unable to safely apply support policy without critical billing details.",
                recommended_action="Human support should follow up for verification.",
            )
            response = renderer.render_empathetic_escalation(
                "I still do not have enough verified details to make a policy-safe decision.",
                "I am escalating your case so a specialist can resolve it directly.",
            )
            return SupportRequestResult(
                intent=intent,
                sentiment=sentiment,
                urgency=Urgency.High,
                reasoning=reasoning + ["Escalated because clarification limit reached."],
                action_taken=ActionTaken.EscalatedToHuman,
                customer_facing_response=response,
                recommended_next_action="Specialist follow-up required.",
                response_type=ResponseType.Escalation,
                escalation_reason=escalation_reason,
            )

        response, action, policies = self._route_intent(intent, request.message, entities)
        envelope = renderer.compose_response_envelope(
            renderer.compose_conversation_summary(request.message, intent, entities),
            response,
            "Let me know if you want me to apply cancellation or escalate this case.",
        )

        return SupportRequestResult(
            intent=intent,
            sentiment=sentiment,
            urgency=urgency,
            reasoning=reasoning,
            action_taken=action,
            customer_facing_response=envelope,
            recommended_next_action="Conversation can continue in the same thread.",
            response_type=ResponseType.DirectAnswer,
            cited_policies=policies,
        )

    def _route_intent(
        self, intent: Intent, message: str, entities: dict[str, str]
    ) -> tuple[str, ActionTaken, list[Any]]:
        if intent == Intent.Refund:
            policies = self._agent.lookup_handbook_policy("refund money back goodwill", self._handbook_sections, intent=intent)
            body = "Based on our support policy, refunds are generally flexible within about 30 days, with exceptions for outages and billing errors."
            if "days_ago" in entities and int(entities["days_ago"]) > 30:
                body = "This appears outside the first-month refund window, so I can escalate for a goodwill review."
            return renderer.inject_policy_citations(body, policies), ActionTaken.RefundTicketCreated, policies

        if intent == Intent.Cancellation:
            policies = self._agent.lookup_handbook_policy("cancel cancellation billing period data retention", self._handbook_sections, intent=intent)
            body = "Cancellation is effective now, access continues through your paid billing period, and data is retained about 90 days."
            return renderer.inject_policy_citations(body, policies), ActionTaken.CancellationTicketCreated, policies

        if intent == Intent.BillingExplanation:
            policies = self._agent.lookup_handbook_policy("billing renewal charged again duplicate charge", self._handbook_sections, intent=intent)
            body = renderer.compose_billing_explanation(message, entities)
            return renderer.inject_policy_citations(body, policies), ActionTaken.ReplySent, policies

        if intent == Intent.Question:
            policies = self._agent.lookup_handbook_policy("plan features account api access", self._handbook_sections, intent=intent)
            if len(policies) > 1 and self._is_ambiguous_question(message):
                clarification = self._agent.build_clarification_request(["plan_name"], intent)
                text = renderer.render_clarification_prompt(
                    clarification,
                    "I found multiple handbook sections and want to answer the right one.",
                )
                return text, ActionTaken.ClarificationRequested, policies
            body = "Based on the handbook, API access is Premium-only and plan transitions apply next billing cycle."
            return renderer.inject_policy_citations(body, policies), ActionTaken.ReplySent, policies

        policies = self._agent.lookup_handbook_policy("escalation support lead", self._handbook_sections, intent=Intent.Complaint)
        body = "I am escalating this request so a specialist can review full context and follow up."
        return renderer.inject_policy_citations(body, policies), ActionTaken.EscalatedToHuman, policies

    def _classify_intent(self, text: str) -> Intent:
        lower = text.lower()
        if any(token in lower for token in ["refund", "money back"]):
            return Intent.Refund
        if any(token in lower for token in ["cancel", "cancellation", "unsubscribe"]):
            return Intent.Cancellation
        if any(token in lower for token in ["charged", "billing", "charge", "renewal"]):
            return Intent.BillingExplanation
        if any(token in lower for token in ["manager", "supervisor", "lawyer", "gdpr", "regulator"]):
            return Intent.Complaint
        if any(token in lower for token in ["how", "what", "does", "api", "plan", "feature"]):
            return Intent.Question
        return Intent.Unclear

    def _extract_entities(self, text: str) -> dict[str, str]:
        entities: dict[str, str] = {}
        order_match = re.search(r"(?:order|invoice)\s*#?\s*([a-z0-9-]+)", text, flags=re.I)
        if order_match:
            entities["order_id"] = order_match.group(1)

        amount_match = re.search(r"\$\s*([0-9]+(?:\.[0-9]{1,2})?)", text)
        if amount_match:
            entities["amount"] = amount_match.group(1)

        if "basic" in text.lower():
            entities["plan_name"] = "Basic"
        if "premium" in text.lower():
            entities["plan_name"] = "Premium"

        days_match = re.search(r"(\d+)\s+days?", text, flags=re.I)
        if days_match:
            entities["days_ago"] = days_match.group(1)

        if re.search(r"(?:march|april|may|june|july|august|september|october|november|december|january|february)\s+\d{1,2}", text, flags=re.I):
            entities["charge_date"] = "provided"

        return entities

    def _missing_fields(self, intent: Intent, entities: dict[str, str]) -> list[str]:
        if intent in (Intent.Refund, Intent.Cancellation):
            needed = ["order_id", "charge_date"]
        elif intent == Intent.BillingExplanation:
            needed = ["charge_date", "amount"]
        else:
            needed = []
        return [field for field in needed if field not in entities]

    def _classify_urgency(self, text: str, sentiment_score: float) -> Urgency:
        lower = text.lower()
        if sentiment_score >= 0.75 or any(token in lower for token in ["today", "immediately", "third time", "disputing"]):
            return Urgency.High
        if sentiment_score >= 0.45 or "soon" in lower:
            return Urgency.Medium
        return Urgency.Low

    def _sentiment_from_score(self, score: float) -> Sentiment:
        if score >= 0.75:
            return Sentiment.Angry
        if score >= 0.45:
            return Sentiment.Frustrated
        if score >= 0.3:
            return Sentiment.Confused
        return Sentiment.Neutral

    def _explicit_escalation_reason(self, text: str) -> EscalationReason | None:
        lower = text.lower()
        if "manager" in lower or "supervisor" in lower:
            return EscalationReason(
                reason=EscalationReasonType.EmotionalEscalation,
                description="Customer explicitly requested managerial escalation.",
                context_summary="Request includes direct ask for manager/supervisor review.",
                recommended_action="Route to senior support immediately.",
            )
        if any(token in lower for token in ["lawyer", "gdpr", "regulator", "chargeback"]):
            return EscalationReason(
                reason=EscalationReasonType.Complexity,
                description="Potential legal or regulatory mention.",
                context_summary="Message contains legal/regulatory keywords.",
                recommended_action="Escalate to senior support and legal workflow.",
            )
        if "third time" in lower or "three" in lower and "same issue" in lower:
            return EscalationReason(
                reason=EscalationReasonType.RepeatedIssue,
                description="Repeated unresolved issue pattern detected.",
                context_summary="Customer indicates multiple unresolved contacts in short period.",
                recommended_action="Escalate for senior case ownership.",
            )
        return None

    def _is_ambiguous_question(self, text: str) -> bool:
        lower = text.lower()
        return "what" in lower and "or" in lower


def _extract_tags(title: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", title.lower())
    expanded = set(words)
    if "refund" in expanded:
        expanded.update({"money", "back", "goodwill"})
    if "cancel" in expanded or "cancellation" in expanded:
        expanded.update({"unsubscribe", "billing", "period"})
    if "billing" in expanded:
        expanded.update({"charge", "renewal", "duplicate"})
    if "plan" in expanded:
        expanded.update({"feature", "api", "basic", "premium"})
    return sorted(expanded)
