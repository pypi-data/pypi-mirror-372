"""
SenseSpace DID Token Verification Library

A Python library for verifying JWT tokens with Ed25519 signatures using SS58 addresses.
"""

from .core import verify_token, generate_token, VerifyTokenResult
from .fastmcp import (
    SenseSpaceTokenVerifier,
)

__version__ = "0.1.0"
__all__ = [
    "verify_token",
    "generate_token",
    "SenseSpaceTokenVerifier",
    "VerifyTokenResult",
]
