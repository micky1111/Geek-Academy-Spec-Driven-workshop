from pathlib import Path

import pytest


@pytest.mark.asyncio
async def test_regression_sample_requests(processor):
    path = Path(__file__).resolve().parents[2] / "data" / "sample_requests.md"
    content = path.read_text(encoding="utf-8")
    requests = [chunk.strip() for chunk in content.split("---") if "From:" in chunk]

    assert len(requests) >= 6

    for request in requests:
        result = await processor.process(request)
        assert result.customer_facing_response
        assert len(result.customer_facing_response) > 20
