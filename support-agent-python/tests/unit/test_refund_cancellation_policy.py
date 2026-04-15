import pytest

from app.models import Intent
from app.processor import SupportRequestProcessor


@pytest.mark.asyncio
async def test_refund_policy_path_returns_policy_reference():
    processor = SupportRequestProcessor()
    result = await processor.process("Refund request for order #456 on April 5, charged $49")
    assert result.intent == Intent.Refund
    assert "Policy reference" in result.customer_facing_response


@pytest.mark.asyncio
async def test_cancellation_policy_path_returns_access_data_info():
    processor = SupportRequestProcessor()
    result = await processor.process("Please cancel my Premium plan for order #456 on April 5")
    assert result.intent == Intent.Cancellation
    assert "billing period" in result.customer_facing_response.lower()
