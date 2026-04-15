import pytest


@pytest.mark.asyncio
async def test_us6_direct_answer_has_coherent_envelope(processor):
    result = await processor.process("Cancel order #42 charged on March 12")
    assert "Action:" in result.customer_facing_response
    assert "Next step:" in result.customer_facing_response


@pytest.mark.asyncio
async def test_us6_clarification_branch_has_contextual_prompt(processor):
    result = await processor.process("Can I get a refund?")
    assert result.customer_facing_response
    assert "Please share" in result.customer_facing_response or "Action:" in result.customer_facing_response
