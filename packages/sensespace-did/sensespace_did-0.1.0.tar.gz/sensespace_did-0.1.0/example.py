#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Example usage of sensespace_did package"""

from sensespace_did import generate_token, verify_token
import asyncio


async def main():
    import os

    print("=" * 60)
    print("Example 1: Basic token verification")
    print("=" * 60)

    # Generate a random 32-byte private key
    random_private_key = os.urandom(32)
    print(f"Generated random private key (hex): {random_private_key.hex()}")

    TOKEN = generate_token(random_private_key)
    print(f"Generated token: {TOKEN}")
    # Basic verification
    result = await verify_token(TOKEN)

    if result.success:
        print("✅ Token verified successfully!")
    else:
        print(f"❌ Verification failed: {result.get('error')}")
    print(result.claims)


if __name__ == "__main__":
    asyncio.run(main())
