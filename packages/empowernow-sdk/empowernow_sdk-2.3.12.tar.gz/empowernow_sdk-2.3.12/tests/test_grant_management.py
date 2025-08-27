from empowernow_common.oauth import (
    HardenedOAuth,
    SecureOAuthConfig,
    GrantManagementAction,
    PARResponse,
)


def test_grant_management_url():
    cfg = SecureOAuthConfig(
        client_id="c",
        client_secret="s",
        authorization_url="https://auth/authorize",
        token_url="https://auth/token",
    )
    oauth = HardenedOAuth(cfg)
    par_resp = PARResponse(request_uri="urn:par:1", expires_in=90)
    url = oauth.create_authorization_url_with_grant(
        par_resp, action=GrantManagementAction.CREATE
    )
    assert "grant_management_action=create" in url
