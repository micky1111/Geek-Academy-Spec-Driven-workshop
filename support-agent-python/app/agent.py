import os
import re
from typing import Any

try:
    from agent_framework import Agent
    from agent_framework.openai import OpenAIChatCompletionClient
except ImportError:
    Agent = None
    OpenAIChatCompletionClient = None

from app.models import ClarificationRequest, HandbookLookupError, HandbookPolicy, Intent


class SupportAgent:
    def __init__(self) -> None:
        self._agent = self._try_build_llm_agent()

    def lookup_handbook_policy(
        self,
        query: str,
        handbook_sections: list[dict[str, Any]],
        *,
        intent: Intent | None = None,
    ) -> list[HandbookPolicy]:
        query_terms = set(re.findall(r"[a-z0-9]+", query.lower()))
        if not query_terms:
            raise HandbookLookupError("Handbook lookup query is empty")

        scored: list[tuple[float, dict[str, Any]]] = []
        for section in handbook_sections:
            haystack_terms = set(re.findall(r"[a-z0-9]+", section["content"].lower()))
            title_terms = set(re.findall(r"[a-z0-9]+", section["title"].lower()))
            tags = set(section.get("tags", []))
            overlap = len(query_terms & haystack_terms) / max(len(query_terms), 1)
            title_overlap = len(query_terms & title_terms) / max(len(query_terms), 1)
            tag_overlap = len(query_terms & tags) / max(len(query_terms), 1)
            score = (overlap * 0.5) + (title_overlap * 0.3) + (tag_overlap * 0.2)

            if intent and intent.value.lower() in section["title"].lower():
                score = min(1.0, score + 0.15)

            if score > 0:
                scored.append((score, section))

        scored.sort(key=lambda item: item[0], reverse=True)
        matches = scored[:3]
        return [
            HandbookPolicy(
                policy_id=entry["policy_id"],
                section=entry["section"],
                title=entry["title"],
                content=entry["content"],
                tags=entry.get("tags", []),
                relevance_score=round(score, 3),
            )
            for score, entry in matches
        ]

    def build_clarification_request(
        self, missing_fields: list[str], intent: Intent
    ) -> ClarificationRequest:
        field_to_question = {
            "order_id": "What is your order ID or invoice number?",
            "purchase_date": "What is the date of your original purchase?",
            "charge_date": "What date did the charge happen?",
            "amount": "What amount were you charged?",
            "plan_name": "Which plan are you currently on (Basic or Premium)?",
        }
        questions = [field_to_question[field] for field in missing_fields if field in field_to_question]
        if not questions:
            questions = ["Could you share the key details so I can help accurately?"]

        return ClarificationRequest(
            questions=questions,
            reason=f"Need additional details to process {intent.value.lower()} request",
            required_fields=missing_fields,
        )

    async def score_sentiment(self, customer_message: str) -> float:
        if self._agent is None:
            return self._heuristic_sentiment(customer_message)

        # Conservative fallback: if MAF call path changes, keep behavior deterministic.
        return self._heuristic_sentiment(customer_message)

    def _try_build_llm_agent(self):
        if Agent is None or OpenAIChatCompletionClient is None:
            return None

        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        if not endpoint or not api_key or not deployment_name:
            return None

        client = OpenAIChatCompletionClient(
            model=deployment_name,
            azure_endpoint=endpoint,
            api_key=api_key,
        )

        return Agent(
            client=client,
            name="SupportSentimentAgent",
            instructions="Score emotional negativity from 0.0 to 1.0.",
        )

    def _heuristic_sentiment(self, customer_message: str) -> float:
        text = customer_message.lower()
        angry_terms = [
            "ridiculous",
            "furious",
            "angry",
            "third time",
            "disputing",
            "lawyer",
            "regulator",
            "manager",
            "supervisor",
        ]
        frustrated_terms = ["disappointed", "frustrated", "upset", "doesn't help", "not resolved"]
        score = 0.15
        score += 0.15 * sum(term in text for term in frustrated_terms)
        score += 0.2 * sum(term in text for term in angry_terms)
        return min(score, 1.0)


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value or not value.strip():
        raise RuntimeError(f"Missing environment variable {name}. Add it to .env.")
    return value
