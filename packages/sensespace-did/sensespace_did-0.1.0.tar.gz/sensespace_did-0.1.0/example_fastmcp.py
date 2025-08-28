#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Example FastMCP integration with SenseSpace DID TokenVerifier.

This example demonstrates how to use the TokenVerifier with FastMCP
for authentication and authorization.
"""

import os
import asyncio
import threading
import time
from typing import Optional

from fastmcp import FastMCP, Context
from sensespace_did.fastmcp import SenseSpaceTokenVerifier
from fastmcp.server.auth import RemoteAuthProvider
from sensespace_did import generate_token
import httpx


def run_server():
    """Run FastMCP server with SenseSpace token verification."""
    # Configure JWT verification

    # auth = RemoteAuthProvider(
    #     token_verifier=verifier,
    #     # 告诉客户端：信任哪些授权服务器（issuer）
    #     authorization_servers=[],  # 换成你们的 AS/issuer
    #     # 告诉客户端：受保护资源的实际 URL（注意带 /mcp）
    #     resource_server_url="http://127.0.0.1:15925/mcp",
    # )

    # mcp = FastMCP(name="Protected API", auth=auth)
    # # Create FastMCP server with authentication
    verifier = SenseSpaceTokenVerifier()
    mcp = FastMCP(name="Protected API", auth=verifier)

    @mcp.tool()
    def get_protected_data(message: str = "Hello from protected endpoint!") -> str:
        """A protected tool that requires authentication."""
        print(f"🔒 Protected tool called with message: {message}")
        return f"Protected response: {message}"

    @mcp.tool()
    def get_public_data(context: Context = None) -> str:
        """A public tool for testing."""

        if context and hasattr(context, "transport"):
            headers = getattr(context.transport, "headers", {}) or {}
        print("🌍 Public tool called")
        return "This is public data"

    print("🚀 Starting FastMCP server on port 15925...")
    mcp.run(
        port=15925,
        transport="streamable-http",
    )


async def run_client():
    """Run client to test the server."""
    # Wait a moment for server to start
    await asyncio.sleep(2)

    print("\n" + "=" * 50)
    print("Testing FastMCP Client")
    print("=" * 50)

    # Generate a token for testing
    random_private_key = os.urandom(32)
    token = generate_token(random_private_key)
    print(f"Generated test token: {token[:50]}...")

    base_url = "http://localhost:15925/mcp"
    from fastmcp import Client
    from fastmcp.client.transports import StreamableHttpTransport

    transport = StreamableHttpTransport(
        base_url,
        auth=token,
    )

    async with Client(transport) as client:
        tools = await client.list_tools()
        print(tools)


def main():
    """Main function to run server and client in separate threads."""
    print("Starting FastMCP Server and Client Test")

    # Start server in a separate thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Run client in main thread
    try:
        asyncio.run(run_client())
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")

    # Give some time to see the results
    time.sleep(2)


if __name__ == "__main__":
    main()
    # run_server()
