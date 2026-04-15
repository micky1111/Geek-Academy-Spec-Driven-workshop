from app.models import Intent
from app.renderer import compose_conversation_summary, compose_response_envelope


def test_response_envelope_contains_required_sections():
    summary = compose_conversation_summary("Please refund order #12", Intent.Refund, {"order_id": "12"})
    response = compose_response_envelope(summary, "I can process this request.", "Confirm your purchase date.")
    assert "Action:" in response
    assert "Next step:" in response


def test_summary_mentions_intent_and_entities():
    summary = compose_conversation_summary("Cancel my plan", Intent.Cancellation, {"plan_name": "Premium"})
    assert "cancellation" in summary.lower()
    assert "plan_name" in summary
