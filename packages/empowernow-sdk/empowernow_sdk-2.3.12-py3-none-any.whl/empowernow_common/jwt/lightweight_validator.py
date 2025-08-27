"""
Lightweight JWT Validator shared across services per BFF Authentication Architecture P1-5.

Features:
- Validate JWT signature using JWKS
- Check token expiration
- Validate audience
- Minimal deps and fast
- Optional FIPS/HardenedOAuth JWKS fetch when empowernow_common.oauth is available

Public API:
- ValidationError (exception)
- class LightweightValidator
- create_validator(jwks_url: str | None = None, expected_audience: str | list[str] | None = None)
"""
from __future__ import annotations

from typing import Dict, Any, Optional, List
from datetime import datetime, UTC
import os
import time
import logging

import jwt
from cachetools import TTLCache

logger = logging.getLogger("empowernow_common.jwt.lightweight_validator")


class ValidationError(Exception):
    pass


class LightweightValidator:
    def __init__(
        self,
        jwks_url: str,
        expected_audience: str | List[str],
        cache_ttl: int = 1800,
        timeout: float = 5.0,
        use_hardened_oauth: bool = False,
    ):
        self.jwks_url = jwks_url
        self.expected_audience = expected_audience
        self.timeout = timeout
        self.use_hardened_oauth = use_hardened_oauth
        self._jwks_cache: TTLCache[str, Dict[str, Any]] = TTLCache(maxsize=1, ttl=cache_ttl)
        self._validation_count = 0
        self._validation_errors = 0
        self._cache_hits = 0

        logger.info(
            "Initialized LightweightValidator: jwks_url=%s, audience=%s, cache_ttl=%ds, hardened_oauth=%s",
            jwks_url,
            expected_audience,
            cache_ttl,
            use_hardened_oauth,
        )

    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        start = time.time()
        self._validation_count += 1
        try:
            if not token or not isinstance(token, str):
                return None

            try:
                unverified_header = jwt.get_unverified_header(token)
                key_id = unverified_header.get("kid")
            except jwt.DecodeError:
                self._validation_errors += 1
                logger.debug("Invalid JWT format")
                return None

            try:
                public_key = await self._get_public_key(key_id)
                if not public_key:
                    self._validation_errors += 1
                    logger.debug("Public key not found for kid: %s", key_id)
                    return None
            except Exception as e:
                self._validation_errors += 1
                logger.error("Failed to get public key: %s", e)
                raise ValidationError(f"Public key retrieval failed: {e}")

            try:
                claims = jwt.decode(
                    token,
                    key=public_key,
                    algorithms=["RS256", "PS256"],
                    audience=self.expected_audience,
                    options={
                        "verify_signature": True,
                        "verify_exp": True,
                        "verify_aud": True,
                        "verify_iss": True,
                    },
                )

                if not self._validate_claims(claims):
                    self._validation_errors += 1
                    return None

                logger.debug(
                    "Token validation successful: sub=%s, time_ms=%.2f",
                    claims.get("sub", "unknown"),
                    (time.time() - start) * 1000,
                )
                return claims
            except jwt.ExpiredSignatureError:
                self._validation_errors += 1
                logger.debug("Token expired")
                return None
            except jwt.InvalidAudienceError:
                self._validation_errors += 1
                logger.debug("Invalid audience")
                return None
            except jwt.InvalidTokenError as e:
                self._validation_errors += 1
                logger.debug("Invalid token: %s", e)
                return None
        except Exception as e:
            self._validation_errors += 1
            logger.error("Unexpected validation error: %s", e)
            raise ValidationError(f"Token validation failed: {e}")

    async def _get_public_key(self, key_id: str | None) -> Optional[str]:
        try:
            if "jwks" in self._jwks_cache:
                jwks_data = self._jwks_cache["jwks"]
                self._cache_hits += 1
            else:
                jwks_data = await self._fetch_jwks()
                if jwks_data:
                    self._jwks_cache["jwks"] = jwks_data

            if not jwks_data or not key_id:
                return None

            for key in jwks_data.get("keys", []):
                if key.get("kid") == key_id:
                    return self._jwk_to_pem(key)
            logger.debug("kid not found in JWKS: %s", key_id)
            return None
        except Exception as e:
            logger.error("Failed to get public key for kid %s: %s", key_id, e)
            return None

    async def _fetch_jwks(self) -> Optional[Dict[str, Any]]:
        try:
            if self.use_hardened_oauth:
                try:
                    from empowernow_common.oauth import HardenedOAuth  # type: ignore

                    issuer_url = self.jwks_url
                    if "/jwks" in issuer_url:
                        issuer_url = issuer_url.rsplit("/jwks", 1)[0]
                    elif "/.well-known" in issuer_url:
                        issuer_url = issuer_url.split("/.well-known")[0]
                    else:
                        issuer_url = issuer_url.rsplit("/", 1)[0]

                    oauth_client = HardenedOAuth(
                        issuer_url,
                        client_id="jwks-fetcher",
                        client_secret="dummy",
                        fips_mode=True,
                        timeout_seconds=self.timeout,
                    )
                    try:
                        discovery = await oauth_client._discover_endpoints()
                        jwks_uri = discovery.get("jwks_uri")
                        if jwks_uri:
                            client = await oauth_client._ensure_http_client()
                            resp = await client.get(jwks_uri)
                            resp.raise_for_status()
                            return resp.json()
                        logger.error("JWKS URI not found in discovery document")
                        return None
                    finally:
                        await oauth_client.close()
                except Exception as e:
                    logger.warning("HardenedOAuth JWKS fetch failed, falling back: %s", e)

            # Fallback: simple HTTP client
            import httpx

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(self.jwks_url)
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            logger.error("Failed to fetch JWKS from %s: %s", self.jwks_url, e)
            return None

    def _jwk_to_pem(self, jwk: Dict[str, Any]) -> str:
        try:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            import base64

            n = base64.urlsafe_b64decode(self._add_padding(jwk["n"]))
            e = base64.urlsafe_b64decode(self._add_padding(jwk["e"]))
            n_int = int.from_bytes(n, byteorder="big")
            e_int = int.from_bytes(e, byteorder="big")
            public_key = rsa.RSAPublicNumbers(e_int, n_int).public_key()
            pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            return pem.decode("utf-8")
        except Exception as e:
            logger.error("Failed to convert JWK to PEM: %s", e)
            raise ValidationError(f"Key conversion failed: {e}")

    def _add_padding(self, b64: str) -> str:
        missing = len(b64) % 4
        if missing:
            b64 += "=" * (4 - missing)
        return b64

    def _validate_claims(self, claims: Dict[str, Any]) -> bool:
        if not claims.get("sub"):
            logger.debug("Missing subject claim")
            return False
        iat = claims.get("iat")
        if not iat:
            logger.debug("Missing issued at claim")
            return False
        try:
            if isinstance(iat, (int, float)):
                now = datetime.now(UTC).timestamp()
                if iat > now + 300:
                    logger.debug("Token issued in the future beyond skew")
                    return False
        except Exception:
            logger.debug("Invalid iat claim type")
            return False
        return True

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "validation_count": self._validation_count,
            "validation_errors": self._validation_errors,
            "cache_hits": self._cache_hits,
            "error_rate": (self._validation_errors / self._validation_count) if self._validation_count else 0.0,
            "cache_hit_rate": (self._cache_hits / self._validation_count) if self._validation_count else 0.0,
        }


def create_validator(
    jwks_url: str | None = None,
    expected_audience: str | List[str] | None = None,
    *,
    use_hardened_oauth: bool | None = None,
) -> LightweightValidator:
    """Factory with sensible defaults and env overrides.

    Env support:
      - OIDC_JWKS_URL
      - OIDC_EXPECTED_AUD (comma-separated to allow multiple)
      - EMPOWERNOW_FIPS_ENABLE (when set to true, enable HardenedOAuth)
    """
    resolved_jwks = os.getenv("OIDC_JWKS_URL") or jwks_url or "http://idp-app:8002/api/oidc/jwks"

    aud_env = os.getenv("OIDC_EXPECTED_AUD")
    if aud_env:
        aud_values = [a.strip() for a in aud_env.split(",") if a.strip()]
        resolved_aud: str | List[str] = aud_values if len(aud_values) > 1 else aud_values[0]
    else:
        resolved_aud = expected_audience or "empowernow"

    if use_hardened_oauth is None:
        # Default: FIPS OFF. Opt-in when EMPOWERNOW_FIPS_ENABLE=true
        use_hardened_oauth = os.getenv("EMPOWERNOW_FIPS_ENABLE", "").lower() in ("1", "true", "yes")

    return LightweightValidator(
        jwks_url=resolved_jwks,
        expected_audience=resolved_aud,
        use_hardened_oauth=use_hardened_oauth,
    )


