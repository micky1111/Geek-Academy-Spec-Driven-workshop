import pytest

from app.models import ActionTaken, ResponseType


@pytest.mark.asyncio
async def test_us1_single_round_clarification_flow(processor):
    first = await processor.process("I was charged twice this month.")
    assert first.response_type == ResponseType.ClarificationNeeded
    assert first.action_taken == ActionTaken.ClarificationRequested
    assert first.clarification_request is not None

    second = await processor.process(
        "I was charged twice this month. Order #123, March 15, $50",
        clarification_context={
            "clarification_round_used": True,
            "required_fields": first.clarification_request.required_fields,
            "clarification_response": "Order #123, March 15, $50",
        },
    )
    assert second.response_type != ResponseType.ClarificationNeeded
