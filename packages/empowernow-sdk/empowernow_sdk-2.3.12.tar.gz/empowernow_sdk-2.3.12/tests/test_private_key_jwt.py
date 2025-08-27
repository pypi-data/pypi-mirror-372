import pytest
import time
from empowernow_common.oauth import (
    HardenedOAuth,
    SecureOAuthConfig,
    generate_jar_signing_key,
)
from jose import jwt as jose_jwt


def test_private_key_jwt_assertion_creation():
    key = generate_jar_signing_key()
    token_url = "https://auth.example.com/token"
    cfg = SecureOAuthConfig(
        client_id="pkjwt-client",
        client_secret="ignored",
        token_url=token_url,
        authorization_url="https://auth.example.com/authorize",
    )
    oauth = HardenedOAuth(cfg)
    oauth.configure_private_key_jwt(
        signing_key=key, signing_alg="RS256", assertion_ttl=120
    )

    assertion = oauth._pkjwt_config.to_jwt(cfg.client_id, token_url)
    claims = jose_jwt.get_unverified_claims(assertion)
    assert claims["iss"] == cfg.client_id
    assert claims["aud"] == token_url
    assert claims["exp"] - claims["iat"] == 120
