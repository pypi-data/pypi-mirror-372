import pytest
import httpx
from empowernow_common.oauth import HardenedOAuth, SecureOAuthConfig


@pytest.mark.asyncio
async def test_token_introspection_and_revocation(monkeypatch):
    introspect_called = False
    revoke_called = False

    async def handler(request: httpx.Request):
        nonlocal introspect_called, revoke_called
        if "introspect" in str(request.url):
            introspect_called = True
            return httpx.Response(200, json={"active": True, "scope": "read"})
        if "revoke" in str(request.url):
            revoke_called = True
            return httpx.Response(200, text="")
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)

    async def _mock_client(self, base_url):  # type: ignore
        return httpx.AsyncClient(transport=transport, base_url=base_url)

    monkeypatch.setattr(
        HardenedOAuth, "_get_secure_http_client", _mock_client, raising=True
    )

    cfg = SecureOAuthConfig(
        client_id="c",
        client_secret="s",
        token_url="https://auth/token",
        authorization_url="https://auth/authorize",
        introspection_url="https://auth/introspect",
        revocation_url="https://auth/revoke",
    )

    oauth = HardenedOAuth(cfg)

    introspect_data = await oauth.introspect_token("access123")
    assert introspect_called
    assert introspect_data["active"] is True

    await oauth.revoke_token("access123")
    assert revoke_called
