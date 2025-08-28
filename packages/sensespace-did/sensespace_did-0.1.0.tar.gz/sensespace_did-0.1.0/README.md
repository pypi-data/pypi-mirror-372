# SenseSpace DID Token Verification

[![PyPI version](https://badge.fury.io/py/sensespace-did.svg)](https://badge.fury.io/py/sensespace-did)
[![Python versions](https://img.shields.io/pypi/pyversions/sensespace-did.svg)](https://pypi.org/project/sensespace-did/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Python library for verifying JWT tokens with Ed25519 signatures using SS58 addresses in the SenseSpace ecosystem. This library provides both standalone token verification and FastMCP integration for building secure, decentralized applications.

## Features

- 🔐 **Ed25519 JWT Verification**: Verify JWT tokens with EdDSA algorithm
- 🌐 **SS58 Address Support**: Native support for Substrate-style SS58 addresses
- 📄 **DID Document Resolution**: Optional DID document fetching and validation
- ⚡ **FastMCP Integration**: Built-in FastMCP TokenVerifier for server applications
- 🔧 **Flexible Configuration**: Customizable DID service endpoints
- 🛡️ **Security Focused**: Comprehensive error handling and validation
- 📦 **Easy Installation**: Simple pip installation with minimal dependencies

## Installation

```bash
pip install sensespace-did
```

## Quick Start

### Basic Token Verification

```python
from sensespace_did import verify_token

# Your JWT token
token = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9..."

# Verify the token
result = await verify_token(token)

if result.success:
    print("✅ Token verified successfully!")
    print(f"Subject: {result.claims['sub']}")
    print(f"Claims: {result.claims}")
else:
    print(f"❌ Verification failed: {result.error}")
```

### With DID Document Fetching

```python
from sensespace_did import verify_token

# Verify token and fetch DID document
result = await verify_token(
    token=token,
    did_base_url="https://api.sensespace.xyz/api/did/"  # Optional, this is the default
)

if result.success:
    print(f"✅ Token verified: {result.claims}")
    
    if result.did_document:
        print(f"📄 DID Document: {result.did_document}")
```

### FastMCP Integration

```python
from fastmcp.server import FastMCPServer
from sensespace_did import SenseSpaceTokenVerifier

# Create FastMCP server with SenseSpace authentication
server = FastMCPServer(
    token_verifier=SenseSpaceTokenVerifier(
        did_base_url="https://api.sensespace.xyz/api/did/"
    )
)

# Your server implementation...
```

## API Reference

### Core Functions

#### `verify_token(token, did_base_url=None)`

Verifies a JWT token with Ed25519 signature using SS58 address.

**Parameters:**
- `token` (str): The JWT token to verify
- `did_base_url` (str, optional): Base URL for DID API. Default: `"https://api.sensespace.xyz/api/did/"`

**Returns:**
`VerifyTokenResult` object containing:
- `success` (bool): Whether verification succeeded
- `claims` (dict): JWT claims (if successful)
- `error` (str): Error message (if verification failed)
- `did_document` (dict): DID document (if fetched successfully)

#### `generate_token(private_key)`

Generates a JWT token for a given private key.

**Parameters:**
- `private_key` (bytes|str): Ed25519 private key in bytes or hex/base58 string

**Returns:**
- `str`: JWT token string

### FastMCP Integration

#### `SenseSpaceTokenVerifier`

A specialized TokenVerifier for the SenseSpace ecosystem that can be used with FastMCP servers.

```python
from sensespace_did import SenseSpaceTokenVerifier

verifier = SenseSpaceTokenVerifier(
    did_base_url="https://api.sensespace.xyz/api/did/"
)

# Use with FastMCP server
server = FastMCPServer(token_verifier=verifier)
```

## Advanced Usage

### Custom DID Service

```python
# Use a custom DID service URL
result = await verify_token(
    token=token,
    did_base_url="https://your-custom-did-service.com/api/did/"
)
```

### Error Handling

```python
from sensespace_did import verify_token

try:
    result = await verify_token(token)
    
    if result.success:
        print("Token is valid")
        print(f"Subject: {result.claims['sub']}")
        print(f"Issued at: {result.claims['iat']}")
        print(f"Expires at: {result.claims['exp']}")
    else:
        print(f"Token verification failed: {result.error}")
        
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Token Generation

```python
from sensespace_did import generate_token
import secrets

# Generate a random Ed25519 private key
private_key = secrets.token_bytes(32)

# Generate a JWT token
token = generate_token(private_key)
print(f"Generated token: {token}")
```

## Requirements

- **Python**: >= 3.10
- **PyJWT**: >= 2.8.0
- **cryptography**: >= 41.0.0
- **base58**: >= 2.1.1
- **httpx**: >= 0.25.0
- **fastmcp**: >= 2.11.0 (for FastMCP integration)

## Development

### Installation from Source

```bash
git clone https://github.com/verisense-network/sensespace-did.git
cd sensespace-did
pip install -e .
```

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Building and Publishing

```bash
# Build the package
python -m build

# Publish to PyPI
twine upload dist/*
```

## Security Considerations

- **Private Key Handling**: Never expose private keys in client-side code
- **Token Storage**: Store tokens securely and use HTTPS for transmission
- **DID Resolution**: Verify DID documents from trusted sources
- **Token Expiration**: Always check token expiration times
- **Algorithm Validation**: This library only accepts EdDSA algorithm tokens

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
