#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
from dataclasses import Field
import hashlib
import json
import time
from typing import Tuple, Dict, Any, Optional

import base58
import jwt
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from pydantic import AnyHttpUrl, BaseModel


def b64url_decode(data: str) -> bytes:
    """Base64URL decode with padding fix."""
    pad = (-len(data)) % 4
    return base64.urlsafe_b64decode(data + ("=" * pad))


def split_jwt(token: str) -> Tuple[dict, dict, bytes]:
    """Return (header, payload, signature_bytes). Does not perform signature verification."""
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid JWT format")
    h, p, s = parts
    header = json.loads(b64url_decode(h))
    payload = json.loads(b64url_decode(p))
    signature = b64url_decode(s)
    return header, payload, signature


def ss58_decode_public_key(ss58_addr: str) -> bytes:
    """
    Decode common SS58 addresses (e.g., 5DA9...) to extract 32-byte Ed25519 public key.
    Convention:
      - Only handles 32-byte AccountId format
      - 1~2 byte prefix (depending on address type), 2-byte checksum at the end
    For more complex address types/lengths, replace with official implementation.
    """
    raw = base58.b58decode(ss58_addr)

    if len(raw) < 1 + 32 + 2:
        raise ValueError(f"SS58 raw too short: {len(raw)} bytes")

    # Try 1-byte prefix
    if len(raw) == 1 + 32 + 2:
        prefix_len = 1
    # Try 2-byte prefix (some networks/types use 2 bytes)
    elif len(raw) == 2 + 32 + 2:
        prefix_len = 2
    else:
        # For 5DA9... type common addresses, usually 1+32+2=35 bytes
        # Here we provide info and try to extract 32 bytes from the end (conservative fallback)
        # You can also directly raise, letting the caller handle it
        # raise ValueError(f"Unexpected SS58 length: {len(raw)}")
        prefix_len = len(raw) - 32 - 2  # Try to be compatible

    pubkey = raw[prefix_len : prefix_len + 32]
    if len(pubkey) != 32:
        raise ValueError("Decoded public key is not 32 bytes")

    return pubkey


def ed25519_public_key_pem_from_raw(raw32: bytes) -> bytes:
    """Convert 32-byte Ed25519 public key to standard PEM (SubjectPublicKeyInfo)."""
    pub = ed25519.Ed25519PublicKey.from_public_bytes(raw32)
    pem = pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return pem


def generate_token(
    sk: bytes,
) -> str:
    """Generate a JWT token for a given DID and payload."""
    # Handle private key input
    if isinstance(sk, str):
        # If sk is a string, decode it from hex or base58
        try:
            # Try hex decoding first
            sk_raw = bytes.fromhex(sk)
        except ValueError:
            try:
                # Try base58 decoding
                sk_raw = base58.b58decode(sk)
            except Exception:
                raise ValueError("Private key string must be valid hex or base58")
    else:
        # Assume sk is already bytes
        sk_raw = sk

    # Validate private key length (Ed25519 private keys are 32 bytes)
    if len(sk_raw) != 32:
        raise ValueError(f"Ed25519 private key must be 32 bytes, got {len(sk_raw)}")

    # Create Ed25519 private key object
    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(sk_raw)

    # Get public key from private key
    public_key = private_key.public_key()
    pubkey_raw = public_key.public_bytes(
        encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
    )

    # Generate SS58 address from public key
    # Using prefix 42 (generic Substrate), you can adjust based on your network
    prefix = 42
    checksum_input = bytes([prefix]) + pubkey_raw
    checksum = hashlib.blake2b(checksum_input, digest_size=2).digest()
    ss58_address = base58.b58encode(bytes([prefix]) + pubkey_raw + checksum).decode()

    # Set subject in payload
    payload = {
        "iat": time.time(),
        "exp": time.time() + 60 * 60 * 24 * 30,
        "nbf": time.time(),
        "iss": "sensespace",
        "sub": ss58_address,
    }
    pubkey_pem = ed25519_public_key_pem_from_raw(pubkey_raw)

    # 2. Generate JWT token
    token = jwt.encode(payload, private_key, algorithm="EdDSA")
    return token


class VerifyTokenResult(BaseModel):
    success: bool
    error: Optional[str] = None
    claims: Optional[dict] = None


async def verify_token(
    token: str,
    did_base_url: AnyHttpUrl | str | None = "https://api.sensespace.xyz/api/did/",
) -> VerifyTokenResult:
    """
    Verify JWT token and return verification information.

    Args:
        token: JWT token string
        did_base_url: DID API base URL (optional, defaults to sensespace API)

    Returns:
        Dictionary containing verification results:
        {
            "success": bool,
            "error": str  # Only present when success=False
            "
        }
    """
    try:
        # 1. Parse JWT
        header, payload, _ = split_jwt(token)

        # 2. Extract subject (SS58 address)
        sub = payload.get("sub")
        if not sub:
            raise ValueError("JWT payload has no 'sub'")

        # 3. SS58 decode to get public key
        pubkey_raw = ss58_decode_public_key(sub)
        pubkey_pem = ed25519_public_key_pem_from_raw(pubkey_raw)

        # 4. Verify algorithm
        if header.get("alg") != "EdDSA":
            raise ValueError(
                f"JWT alg is {header.get('alg')}, expected 'EdDSA' for Ed25519"
            )

        # 5. Verify JWT signature
        _ = jwt.decode(token, pubkey_pem, algorithms=["EdDSA"])
        # 6. Optional: Get DID document
        if did_base_url:
            did_url = f"{did_base_url.rstrip('/')}/{sub}"

            try:
                import httpx

                async with httpx.AsyncClient(timeout=10) as client:
                    response = await client.get(did_url)
                    response.raise_for_status()
                    did_data = response.json()

                    if not (did_data.get("success") and did_data.get("data")):
                        return VerifyTokenResult(
                            success=False,
                            error="DID document not found or invalid response",
                        )
            except Exception as e:
                return VerifyTokenResult(
                    success=False,
                    error=f"Failed to fetch DID document: {str(e)}",
                )

        return VerifyTokenResult(success=True, claims=payload)

    except jwt.InvalidTokenError as e:
        return VerifyTokenResult(
            success=False, error=f"JWT validation failed: {str(e)}"
        )
    except httpx.HTTPStatusError as e:
        return VerifyTokenResult(success=False, error=f"HTTP error: {str(e)}")
    except httpx.TimeoutException as e:
        return VerifyTokenResult(success=False, error=f"Timeout: {str(e)}")
    except Exception as e:
        return VerifyTokenResult(success=False, error=str(e))
