#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FastMCP TokenVerifier for SenseSpace DID authentication.

Validates JWT (alg=EdDSA, sub=SS58) issued by SenseSpace and returns an
AccessToken consumable by FastMCP tools.
"""

from __future__ import annotations

import logging
from typing import Any, Optional
from pydantic import AnyHttpUrl

from fastmcp.server.auth import TokenVerifier, AccessToken
from .core import verify_token as core_verify_token

logger = logging.getLogger(__name__)


def _normalize_scopes(claims: dict) -> list[str]:
    """Normalize scopes from JWT claims.

    Supports both 'scope' (space-separated string) and 'scopes' (list) formats.

    Args:
        claims: JWT claims dictionary

    Returns:
        List of scope strings
    """
    if "scopes" in claims and isinstance(claims["scopes"], list):
        return [str(s) for s in claims["scopes"]]
    if "scope" in claims and isinstance(claims["scope"], str):
        return [s for s in claims["scope"].split() if s]
    return []


def _extract_expiration(claims: dict) -> Optional[int]:
    """Extract and normalize expiration time from JWT claims.

    Args:
        claims: JWT claims dictionary

    Returns:
        Expiration time as epoch seconds (int), or None if not present
    """
    exp = claims.get("exp")
    if isinstance(exp, (int, float)):
        return int(exp)
    return None


class SenseSpaceTokenVerifier(TokenVerifier):
    """
    Specialized TokenVerifier for the SenseSpace ecosystem.

    This verifier validates JWT tokens with EdDSA signatures and SS58-encoded
    subject identifiers, typically issued by SenseSpace authorization servers.
    """

    def __init__(
        self,
        did_base_url: AnyHttpUrl | str | None = "https://api.sensespace.xyz/api/did/",
    ):
        """Initialize the SenseSpace token verifier.

        Args:
            did_base_url: Base URL for DID document resolution. If None,
                         DID resolution will be skipped during verification.
        """
        super().__init__()
        self.did_base_url = str(did_base_url) if did_base_url else None
        logger.info(
            "Initializing SenseSpaceTokenVerifier with DID base URL: %s",
            self.did_base_url,
        )

    async def verify_token(self, token: str) -> AccessToken | None:
        """
        Verify a bearer token and return AccessToken if valid.

        Args:
            token: The JWT token string to verify

        Returns:
            AccessToken instance if verification succeeds, None otherwise
        """
        try:
            result = await core_verify_token(token, self.did_base_url)
        except Exception as e:
            logger.exception("SenseSpace token verification error: %s", e)
            return None

        if not getattr(result, "success", False):
            logger.debug(
                "Token verification failed: %s",
                getattr(result, "error", "Unknown error"),
            )
            return None

        claims: dict[str, Any] = getattr(result, "claims", {}) or {}
        client_id = str(claims.get("sub") or "")
        if not client_id:
            logger.warning("Missing 'sub' claim in token; rejecting")
            return None

        scopes = _normalize_scopes(claims)
        expires_at = _extract_expiration(claims)
        resource_url = getattr(self, "resource_server_url", None)

        logger.debug(
            "Token verified successfully for client_id=%s, scopes=%s, expires_at=%s",
            client_id,
            scopes,
            expires_at,
        )

        return AccessToken(
            token=token,
            client_id=client_id,
            scopes=scopes,
            expires_at=expires_at,
            resource=resource_url,
            claims=claims,
        )
