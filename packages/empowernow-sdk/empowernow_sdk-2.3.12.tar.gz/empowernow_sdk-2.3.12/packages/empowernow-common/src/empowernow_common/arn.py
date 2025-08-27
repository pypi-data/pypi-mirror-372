"""Empower ARN helper functions (canonical grammar).

Canonical grammar (v0):
    auth:<type>:<provider>:<subject>

Where:
    - type     – account | service | agent | identity
    - provider – logical source/provider (e.g., empowernow, okta)
    - subject  – stable identifier within the provider (email, upn, oid, etc.)

Public helpers:
    - ``parse(arn_str)``   → ``{"type": str, "provider": str, "id": str}``
    - ``validate(arn)``    → bool (fast validation)
    - ``is_user(arn)``     → bool (alias for ``type == 'account'``)
    - ``to_user_id(arn)``  → Returns subject when ``type == 'account'`` else ``None``

Note: This replaces the previous experimental "arn:emp:" grammar. All
services should use the canonical ``auth:<type>:<provider>:<subject>`` format.
"""
from __future__ import annotations

from typing import Optional, Dict

__all__ = ["parse", "validate", "is_user", "to_user_id"]

PREFIX = "auth:"


def _split_fragment(arn: str):  # retained for backward compatibility; no-op
    return arn, None


def parse(arn: str) -> Dict[str, str]:
    """Return components of a canonical ARN.

    Returns a dict with keys: type, provider, id.
    Raises ``ValueError`` if string is not a valid canonical ARN.
    """
    typ, provider, subject = _parse_components(arn)
    return {"type": typ, "provider": provider, "id": subject}


def validate(arn: str) -> bool:  # fast path for middleware
    try:
        _parse_components(arn)
        return True
    except ValueError:
        return False


def is_user(arn: str) -> bool:
    """Alias for checking account-type identities (historical naming)."""
    try:
        typ, *_ = _parse_components(arn)
        return typ == "account"
    except ValueError:
        return False


def to_user_id(arn: str) -> Optional[str]:
    """Return the subject when type == 'account', else None."""
    try:
        typ, _provider, subject = _parse_components(arn)
        return subject if typ == "account" else None
    except ValueError:
        return None


# ---------------- internal helpers ---------------- #

def _parse_components(arn: str) -> tuple[str, str, str]:
    if not isinstance(arn, str) or not arn.startswith(PREFIX):
        raise ValueError("ARN must start with 'auth:'")

    parts = arn[len(PREFIX) :].split(":", 2)
    if len(parts) != 3 or not parts[0] or not parts[1] or not parts[2]:
        raise ValueError("ARN must be 'auth:<type>:<provider>:<subject>'")

    typ, provider, subject = parts

    # basic sanity: enforce lowercase for type; provider non-empty
    if not typ or not typ.islower() or not typ.replace("-", "").replace("_", "").isalnum():
        raise ValueError("Invalid ARN type")
    if not provider or ":" in provider:
        raise ValueError("Invalid ARN provider")

    if len(subject) > 512:
        raise ValueError("ARN subject too long")

    return typ, provider, subject