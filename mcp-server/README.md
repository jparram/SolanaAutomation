# Solana Trading MCP Server

This is a Model Context Protocol (MCP) server for Solana trading and analytics. It provides a standardized interface for AI agents like Claude Desktop to interact with the Solana blockchain.

## Features

- Wallet address and balance retrieval
- Token information retrieval
- Solana asset data access
- Standardized JSON API for AI agent interaction

## Available Actions

- `GET_ASSET`: Retrieve information about a Solana token by address
- `DEPLOY_TOKEN`: (Placeholder) Deploy a new token on Solana
- `TRADE`: (Placeholder) Execute token trades
- `BALANCE`: Get the SOL balance of the connected wallet
- `WALLET_ADDRESS`: Get the public key of the connected wallet
- `TOKEN_BALANCES`: (Placeholder) Get token balances for the connected wallet

## Setup

1. Install dependencies:
```bash
pnpm install
```

2. Create a `.env` file in the project root with:
```
RPC_URL="https://api.mainnet-beta.solana.com" 
OPENAI_API_KEY="[OPTIONAL_OPENAI_KEY]"
PORT=3000
```
It's recommended to leave `SOLANA_PRIVATE_KEY` empty in your `.env` file. If it's empty, a new keypair will be generated automatically at runtime. If you choose to use an existing wallet, ensure you store your private key securely and do not commit it to version control.

3. Build the project:
```bash
pnpm run build
```

4. Start the server:
```bash
pnpm start
```

The MCP server will be available at http://localhost:3000 (or the PORT specified in your .env file).

## Using with Claude Desktop

1. In Claude Desktop, configure a new MCP server with the URL http://localhost:3000
2. Add a name like "Solana Trading"
3. Claude will automatically discover the available actions
4. You can now use natural language to interact with your Solana wallet

Example prompts:
- "Check my wallet balance"
- "Get information about this token: [TOKEN_ADDRESS]"

## Development

For development with auto-reload:
```bash
pnpm run dev
```

## License

ISC
