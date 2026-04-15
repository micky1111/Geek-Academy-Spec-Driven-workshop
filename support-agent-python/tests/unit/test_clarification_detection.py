from app.models import Intent
from app.processor import SupportRequestProcessor


def test_missing_fields_for_billing_requests():
    processor = SupportRequestProcessor()
    missing = processor._missing_fields(Intent.BillingExplanation, {})
    assert "charge_date" in missing
    assert "amount" in missing


def test_missing_fields_for_refund_request_with_partial_entities():
    processor = SupportRequestProcessor()
    missing = processor._missing_fields(Intent.Refund, {"order_id": "123"})
    assert missing == ["charge_date"]
