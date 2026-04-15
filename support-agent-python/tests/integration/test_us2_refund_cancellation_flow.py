import pytest

from app.models import Intent, ResponseType


@pytest.mark.asyncio
async def test_us2_refund_in_policy_like_case(processor):
    result = await processor.process("I need a refund for order #789 charged on April 5 for $49")
    assert result.intent == Intent.Refund
    assert result.response_type == ResponseType.DirectAnswer


@pytest.mark.asyncio
async def test_us2_cancellation_case(processor):
    result = await processor.process("Cancel my account order #555 charged on March 10")
    assert result.intent == Intent.Cancellation
    assert result.response_type == ResponseType.DirectAnswer
