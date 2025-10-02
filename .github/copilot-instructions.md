# GitHub Copilot Instructions for Solana Automation

## Project Overview

This is a multi-agent Solana automation platform combining Python and TypeScript for AI-driven blockchain operations, browser automation, and autonomous trading. The platform uses a Multi-Agent Consensus Protocol (MCP) where specialized AI agents collaborate to analyze data and execute trades.

## Architecture

### Technology Stack
- **Backend**: Python 3.8+ (FastAPI, Solana SDK, web automation)
- **MCP Server**: TypeScript/Node.js (Solana integration, MCP protocol)
- **Frontend**: React (Trading Desktop UI)
- **Blockchain**: Solana (Web3.js, SPL tokens, Metaplex)
- **AI/ML**: Multiple LLM providers (OpenAI, Anthropic, etc.)

### Key Components
- **Terminagent**: Main orchestrator coordinating AI agent council
- **Agent Council**: Warren Buffett, Cathie Wood, Charlie Munger, Ben Graham, Risk Manager personas
- **Browser Service**: Automated web scraping and data extraction
- **Blockchain Service**: On-chain operations (transactions, token deployment, NFTs)
- **Payment Service**: X402 protocol for autonomous micropayments
- **API Layer**: FastAPI endpoints for agent, browser, blockchain, and payment operations

## Code Style Guidelines

### Python
- **Style**: Follow PEP 8 with 88 character line length (Black formatter)
- **Type hints**: Use type annotations for function parameters and return values
- **Imports**: Sort with isort (Black profile)
- **Linting**: Use ruff for linting checks
- **Docstrings**: Use Google-style docstrings for functions and classes
- **Async**: Prefer async/await for I/O operations, especially blockchain interactions

Example:
```python
from typing import Optional
from solana.rpc.api import Client

async def get_token_balance(
    wallet_address: str,
    token_mint: str,
    rpc_client: Client
) -> Optional[float]:
    """Get SPL token balance for a wallet.
    
    Args:
        wallet_address: Base58-encoded wallet public key
        token_mint: Base58-encoded token mint address
        rpc_client: Solana RPC client instance
        
    Returns:
        Token balance as float, or None if not found
    """
    # Implementation
```

### TypeScript
- **Style**: ESLint recommended rules, Prettier formatting
- **Config**: 100 char print width, single quotes, trailing commas (ES5)
- **Types**: Prefer explicit types over `any`
- **Async**: Use async/await consistently
- **Modules**: Use ES6 import/export syntax

Example:
```typescript
import { Connection, PublicKey } from '@solana/web3.js';

interface TokenBalance {
  address: string;
  amount: number;
  decimals: number;
}

async function getTokenBalance(
  connection: Connection,
  walletAddress: string,
  tokenMint: string
): Promise<TokenBalance | null> {
  // Implementation
}
```

## Security Best Practices

### Critical Security Rules
1. **Never hardcode secrets**: Use environment variables exclusively
2. **API Keys**: Always use `.env` files (never commit them)
3. **Private Keys**: Store securely, never in code or logs
4. **Validation**: Always validate and sanitize user inputs
5. **Rate Limiting**: Implement rate limits on all API endpoints
6. **Transaction Safety**: Require confirmation before blockchain transactions

### Environment Variables
All sensitive data must be in `.env` files:
```python
# Good
api_key = os.getenv("OPENAI_API_KEY")

# Bad - Never do this
api_key = "sk-1234567890abcdef"
```

### Solana Private Keys
```python
# Good
from solders.keypair import Keypair
import base58

private_key_bytes = base58.b58decode(os.getenv("SOLANA_PRIVATE_KEY"))
keypair = Keypair.from_bytes(private_key_bytes)

# Bad - Never log or print private keys
print(f"Private key: {private_key}")  # NEVER DO THIS
```

## Development Workflow

### Before Committing
1. **Python checks**:
   ```bash
   ruff check . && black --check . && isort --check-only . && mypy .
   ```

2. **TypeScript checks**:
   ```bash
   cd mcp-server && npm run lint && npm run build
   ```

3. **Run tests**:
   ```bash
   pytest  # Python tests
   cd mcp-server && npm test  # TypeScript tests
   ```

### Git Workflow
- Use descriptive commit messages
- Keep commits focused and atomic
- Never commit `.env` files, logs, or build artifacts
- Review `.gitignore` before committing new file types

## Common Patterns

### Blockchain Interactions
```python
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction

async def send_transaction(
    client: AsyncClient,
    transaction: Transaction,
    signers: list,
    max_retries: int = 3
) -> str:
    """Send transaction with retry logic."""
    for attempt in range(max_retries):
        try:
            result = await client.send_transaction(
                transaction,
                *signers,
                opts={"skip_preflight": False}
            )
            await client.confirm_transaction(result.value)
            return str(result.value)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)
```

### AI Agent Tool Pattern
```python
from langchain.tools import BaseTool

class SolanaTransferTool(BaseTool):
    name: str = "solana_transfer"
    description: str = """Transfer SOL to another wallet.
    
    Input: JSON string with:
    {
        "to_address": "recipient wallet address",
        "amount": "amount in SOL"
    }
    """
    
    async def _arun(self, input: str):
        # Implementation
        
    def _run(self, input: str):
        raise NotImplementedError("Use async _arun instead")
```

### Error Handling
```python
# Always use specific exceptions
try:
    result = await blockchain_operation()
except ValueError as e:
    logger.error(f"Invalid input: {e}")
    raise
except ConnectionError as e:
    logger.error(f"RPC connection failed: {e}")
    # Implement retry logic
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    raise
```

## Testing Guidelines

### Python Tests
- Use pytest for testing
- Mock external services (RPC calls, AI APIs)
- Test edge cases and error conditions
- Use fixtures for common setup

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_transfer_sol():
    with patch('solana.rpc.async_api.AsyncClient') as mock_client:
        mock_client.send_transaction = AsyncMock(return_value=...)
        result = await transfer_sol("address", 1.0)
        assert result is not None
```

### TypeScript Tests
- Test public interfaces
- Mock blockchain connections
- Validate input/output types

## API Development

### FastAPI Endpoints
```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

router = APIRouter(prefix="/api/blockchain", tags=["blockchain"])

class TransferRequest(BaseModel):
    to_address: str
    amount: float

@router.post("/transfer")
async def transfer_sol(
    request: TransferRequest,
    current_user: User = Depends(get_current_user)
):
    """Transfer SOL to another wallet."""
    try:
        result = await blockchain_service.transfer(
            request.to_address,
            request.amount
        )
        return {"transaction": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## Documentation

### Code Comments
- Add comments for complex logic, not obvious code
- Explain "why" not "what"
- Keep comments up to date with code changes

### Function Documentation
Always document:
- Purpose of the function
- Parameters and types
- Return value and type
- Exceptions that may be raised
- Example usage for complex functions

## Performance Considerations

1. **Async Operations**: Use async/await for I/O-bound operations
2. **Connection Pooling**: Reuse RPC connections
3. **Caching**: Cache frequently accessed blockchain data
4. **Rate Limits**: Respect API rate limits (especially RPC endpoints)
5. **Batch Operations**: Batch blockchain reads when possible

## Common Pitfalls to Avoid

1. **Don't** mix sync and async code without proper handling
2. **Don't** ignore transaction confirmations
3. **Don't** use float arithmetic for token amounts (use integers with decimals)
4. **Don't** trust user input without validation
5. **Don't** deploy to production without thorough testing
6. **Don't** commit secrets or credentials
7. **Don't** use global state for request-specific data

## Project-Specific Patterns

### Agent Tool Creation
When creating new tools for AI agents:
1. Inherit from `BaseTool`
2. Provide clear `name` and `description`
3. Implement async `_arun` method
4. Return structured data (dict/JSON)
5. Handle errors gracefully

### Browser Automation
Use the browser service for web scraping:
```python
from browser.solana_web_browser import SolanaWebBrowser

browser = SolanaWebBrowser(headless=True)
await browser.navigate("https://birdeye.so/token/...")
data = await browser.extract_token_data()
await browser.close()
```

### X402 Payment Integration
For autonomous payments:
```python
from payment.x402_handler import X402PaymentHandler

handler = X402PaymentHandler(
    wallet=wallet,
    auto_approve_threshold=0.1  # SOL
)
response = await handler.request_with_payment(url, method="GET")
```

## Resources

- **Solana Docs**: https://docs.solana.com/
- **Web3.js Docs**: https://solana-labs.github.io/solana-web3.js/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Project README**: /README.md
- **Security Guidelines**: /SECURITY_CHECKLIST.md

## Questions to Ask

When unsure about implementation:
1. Does this require blockchain interaction? (Consider gas/transaction fees)
2. Is this data sensitive? (Use environment variables)
3. Should this be async? (I/O operations should be async)
4. Have I validated inputs? (Always validate)
5. Is error handling comprehensive? (Log and handle appropriately)
6. Does this need testing? (Yes, especially for critical paths)
7. Am I following the project's existing patterns? (Check similar code)

## File Organization

```
/api/              - FastAPI routes and services
/agent/            - AI agent implementations
/browser/          - Web automation modules
/tools/            - Blockchain utilities (deploy, swap, etc.)
/payment/          - X402 payment protocol
/characters/       - AI agent personality configs
/mcp-server/       - TypeScript MCP server
/metaplex-integration/ - NFT operations
/utils/            - Shared utilities
/config/           - Configuration management
/docs/             - Project documentation
```

When creating new files, follow the existing directory structure and naming conventions.
