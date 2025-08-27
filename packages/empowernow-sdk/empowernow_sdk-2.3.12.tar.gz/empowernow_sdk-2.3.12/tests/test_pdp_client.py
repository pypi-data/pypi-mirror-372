import asyncio
import pytest

from empowernow_common.authzen.client import (
    EnhancedPDP,
    EnhancedAuthResult,
    Constraint,
    Obligation,
)


@pytest.fixture
def epdp():
    return EnhancedPDP(
        base_url="https://pdp.example.com",
        client_id="client",
        client_secret="secret",
        token_url="https://pdp.example.com/token",
    )


@pytest.mark.asyncio
async def test_pdp_permit(epdp, monkeypatch):
    """PDP permit decision should return True decision flag."""

    async def fake_call(self, req):
        return {"decision": True, "context": {"constraints": [], "obligations": []}}

    monkeypatch.setattr(EnhancedPDP, "_call_pdp_api", fake_call, raising=True)

    result = await epdp.evaluate({})
    assert isinstance(result, EnhancedAuthResult)
    assert result.decision is True
    assert not result.has_constraints


@pytest.mark.asyncio
async def test_pdp_deny(epdp, monkeypatch):
    """PDP deny decision should return False decision flag."""

    async def fake_call(self, req):
        return {
            "decision": False,
            "context": {
                "reason_admin": {"en": "denied"},
                "constraints": [],
                "obligations": [],
            },
        }

    monkeypatch.setattr(EnhancedPDP, "_call_pdp_api", fake_call, raising=True)

    result = await epdp.evaluate({})
    assert result.decision is False


@pytest.mark.asyncio
async def test_pdp_obligation_retry(epdp, monkeypatch):
    """Critical obligation should retry and raise after retries exhausted."""

    # Prepare PDP response with one critical obligation
    obligation_dict = {
        "id": "audit1",
        "type": "audit_log",
        "parameters": {"event": "login"},
        "timing": "after",
        "critical": True,
    }

    async def fake_call(self, req):
        return {
            "decision": True,
            "context": {"constraints": [], "obligations": [obligation_dict]},
        }

    monkeypatch.setattr(EnhancedPDP, "_call_pdp_api", fake_call, raising=True)

    # Obligation handler that always fails
    async def failing_handler(obligation: Obligation):  # type: ignore
        raise RuntimeError("db down")

    epdp.register_obligation_handler("audit_log", failing_handler)

    with pytest.raises(Exception):
        await epdp.evaluate_and_enforce({})
