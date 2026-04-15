import pytest

from app.models import ActionTaken


@pytest.mark.asyncio
async def test_us4_general_plan_question(processor):
    result = await processor.process("How do I upgrade from Basic to Premium?")
    assert result.action_taken in {ActionTaken.ReplySent, ActionTaken.ClarificationRequested}


@pytest.mark.asyncio
async def test_us4_ambiguous_question_can_request_narrowing(processor):
    result = await processor.process("What happens with plan or account changes?")
    assert result.customer_facing_response
