import os
from sensespace_did import generate_token

import asyncio


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

    # base_url = "http://localhost:15925/mcp"
    base_url = "https://sensespace-did-mcp-974618882715.us-central1.run.app/mcp"
    from fastmcp import Client
    from fastmcp.client.transports import StreamableHttpTransport

    transport = StreamableHttpTransport(
        base_url,
        auth=token,
    )

    async with Client(transport) as client:
        # await client.ping()
        tools = await client.list_tools()
        print(tools)


if __name__ == "__main__":
    asyncio.run(run_client())
