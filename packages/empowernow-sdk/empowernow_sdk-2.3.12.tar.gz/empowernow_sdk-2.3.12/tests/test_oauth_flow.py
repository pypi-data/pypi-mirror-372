import asyncio
from datetime import datetime, timezone
import httpx
import jwt
import pytest
import base64
import json
import time

from empowernow_common.oauth import HardenedOAuth, SecureOAuthConfig, RARBuilder


@pytest.mark.asyncio
async def test_par_auth_token_flow_happy(monkeypatch):
    """Happy-path: PAR → authorization URL construction returns expected values."""

    # --- Arrange -----------------------------------------------------------
    par_endpoint = "https://auth.example.com/par"

    # Fake PAR server response
    async def par_handler(request: httpx.Request):
        assert request.method == "POST"
        # basic auth header present
        assert request.headers.get("Authorization", "").startswith("Basic ")
        return httpx.Response(
            200, json={"request_uri": "urn:example:par:123", "expires_in": 90}
        )

    transport = httpx.MockTransport(par_handler)

    async def _mock_client(self, base_url):  # type: ignore
        return httpx.AsyncClient(transport=transport, base_url=base_url)

    monkeypatch.setattr(
        HardenedOAuth, "_get_secure_http_client", _mock_client, raising=True
    )

    config = SecureOAuthConfig(
        client_id="client1",
        client_secret="secret",
        authorization_url="https://auth.example.com/authorize",
        token_url="https://auth.example.com/token",
        par_endpoint=par_endpoint,
    )

    oauth = HardenedOAuth(config)

    # --- Act --------------------------------------------------------------
    par_response = await oauth.create_par_request(
        redirect_uri="https://app.example.com/cb",
        scope="openid",
    )

    auth_url = oauth.build_authorization_url(par_response)

    # --- Assert -----------------------------------------------------------
    assert par_response.request_uri == "urn:example:par:123"
    assert "request_uri=urn%3Aexample%3Apar%3A123" in auth_url
    assert auth_url.startswith("https://auth.example.com/authorize")


@pytest.mark.asyncio
async def test_jar_jarm_flow_builds_jwt(monkeypatch):
    """Ensure JAR + JARM flow constructs JWT request object without network."""

    # Stub out network for PAR as above but we won't call it here
    async def _dummy_client(self, base_url):  # type: ignore
        return httpx.AsyncClient(
            transport=httpx.MockTransport(lambda r: httpx.Response(500))
        )

    monkeypatch.setattr(
        HardenedOAuth, "_get_secure_http_client", _dummy_client, raising=True
    )

    config = SecureOAuthConfig(
        client_id="client2",
        client_secret="secret",
        authorization_url="https://auth.example.com/authorize",
        token_url="https://auth.example.com/token",
    )

    oauth = HardenedOAuth(config)
    oauth.configure_jar()
    oauth.enable_jarm()

    jwt_request_object = oauth.create_jar_request_object(
        authorization_params={
            "response_type": "code",
            "client_id": config.client_id,
            "redirect_uri": "https://app/cb",
        },
        audience=config.authorization_url,
    )

    # quick sanity: it should decode (not validate signature) as JWT structure
    header = jwt.get_unverified_header(jwt_request_object)
    assert header["alg"] in {"RS256", "ES256"}


@pytest.mark.asyncio
async def test_jarm_response_processing(monkeypatch):
    """JARMManager should parse and validate minimal signed auth response (signature not verified)."""

    client_id = "client3"
    jarm = HardenedOAuth(
        SecureOAuthConfig(
            client_id=client_id,
            client_secret="secret",
            authorization_url="https://auth.example.com/authorize",
            token_url="https://auth.example.com/token",
        )
    )._jarm_manager

    # Enable JARM with RS256 (default)
    jarm.enable_jarm()

    # Craft minimal JWT (header + payload base64url, dummy signature)
    header_b64 = (
        base64.urlsafe_b64encode(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
        .rstrip(b"=")
        .decode()
    )
    payload = {
        "iss": "https://auth.example.com",
        "aud": client_id,
        "exp": int(time.time()) + 300,
    }
    payload_b64 = (
        base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()
    )
    jwt_compact = f"{header_b64}.{payload_b64}.signature"

    claims = jarm.process_response(jwt_compact)
    assert claims["aud"] == client_id
    assert claims["iss"] == "https://auth.example.com"
