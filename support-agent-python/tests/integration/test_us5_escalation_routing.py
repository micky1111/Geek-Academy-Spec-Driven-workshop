import pytest

from app.models import ResponseType


@pytest.mark.asyncio
async def test_us5_explicit_manager_escalation(processor):
    result = await processor.process("Need to speak with a manager about my billing dispute.")
    assert result.response_type == ResponseType.Escalation
    assert result.escalation_reason is not None


@pytest.mark.asyncio
async def test_us5_legal_signal_escalation(processor):
    result = await processor.process("If this is not fixed I will contact a regulator.")
    assert result.response_type == ResponseType.Escalation
