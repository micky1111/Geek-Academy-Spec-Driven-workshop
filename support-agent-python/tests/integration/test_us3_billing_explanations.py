import pytest

from app.models import ResponseType


@pytest.mark.asyncio
async def test_us3_known_billing_case(processor):
    result = await processor.process("Why was I charged again for my subscription order #99 on March 15 for $50")
    assert result.response_type == ResponseType.DirectAnswer
    assert "subscription" in result.customer_facing_response.lower() or "renewal" in result.customer_facing_response.lower()


@pytest.mark.asyncio
async def test_us3_duplicate_charge_case(processor):
    result = await processor.process("I think I was charged twice order #22 on March 10 for $49")
    assert result.response_type == ResponseType.DirectAnswer
    assert "duplicate" in result.customer_facing_response.lower() or "pending" in result.customer_facing_response.lower()
