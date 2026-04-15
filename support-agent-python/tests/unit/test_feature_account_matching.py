import pytest

from app.models import Intent
from app.processor import SupportRequestProcessor


def test_question_intent_detected_for_plan_feature_prompt():
    processor = SupportRequestProcessor()
    assert processor._classify_intent("Does Basic include API access?") == Intent.Question


@pytest.mark.asyncio
async def test_feature_question_returns_policy_reference():
    processor = SupportRequestProcessor()
    result = await processor.process("How do I upgrade my plan and get API access?")
    assert result.intent == Intent.Question
    assert "Policy reference" in result.customer_facing_response
