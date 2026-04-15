import pytest

from app.models import Intent
from app.processor import SupportRequestProcessor


def test_billing_intent_detected_for_charge_questions():
    processor = SupportRequestProcessor()
    assert processor._classify_intent("Why was I charged again?") == Intent.BillingExplanation


@pytest.mark.asyncio
async def test_billing_response_mentions_charge_patterns():
    processor = SupportRequestProcessor()
    result = await processor.process("Why was I charged $50 on March 15 for order #123?")
    assert result.intent == Intent.BillingExplanation
    assert "charge" in result.customer_facing_response.lower()
