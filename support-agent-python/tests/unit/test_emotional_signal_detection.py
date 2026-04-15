import pytest

from app.models import ResponseType
from app.processor import SupportRequestProcessor


def test_manager_request_triggers_escalation_reason():
    processor = SupportRequestProcessor()
    escalation = processor._explicit_escalation_reason("I need a manager now.")
    assert escalation is not None


@pytest.mark.asyncio
async def test_angry_message_escalates():
    processor = SupportRequestProcessor()
    result = await processor.process("This is ridiculous and I want a supervisor.")
    assert result.response_type == ResponseType.Escalation
