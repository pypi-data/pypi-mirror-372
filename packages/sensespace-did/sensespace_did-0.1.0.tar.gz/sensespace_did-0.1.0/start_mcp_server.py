from fastmcp import FastMCP
from sensespace_did.fastmcp import SenseSpaceTokenVerifier
from fastmcp.server.auth import RemoteAuthProvider
from sensespace_did import generate_token
import httpx


def start_mcp_server():
    """Run FastMCP server with SenseSpace token verification."""
    # Configure JWT verification
    verifier = SenseSpaceTokenVerifier()

    # auth = RemoteAuthProvider(
    #     token_verifier=verifier,
    #     # 告诉客户端：信任哪些授权服务器（issuer）
    #     authorization_servers=[],  # 换成你们的 AS/issuer
    #     # 告诉客户端：受保护资源的实际 URL（注意带 /mcp）
    #     resource_server_url="http://127.0.0.1:15925/mcp",
    # )

    # mcp = FastMCP(name="Protected API", auth=auth)
    # # Create FastMCP server with authentication
    mcp = FastMCP(name="Protected API", auth=verifier)

    @mcp.tool()
    def get_protected_data(message: str = "Hello from protected endpoint!") -> str:
        """A protected tool that requires authentication."""
        print(f"🔒 Protected tool called with message: {message}")
        return f"Protected response: {message}"

    @mcp.tool()
    def get_public_data() -> str:
        """A public tool for testing."""
        print("🌍 Public tool called")
        return "This is public data"

    print("🚀 Starting FastMCP server on port 8080...")
    mcp.run(
        port=8080,
        host="0.0.0.0",
        transport="streamable-http",
    )


if __name__ == "__main__":
    start_mcp_server()
