# Connecting Claude Desktop to Solana Trading MCP Server

This guide explains how to connect Claude Desktop to our Solana Trading MCP Server to enable AI-powered Solana trading interactions.

## Prerequisites

1. Claude Desktop application installed
2. Solana Trading MCP Server running (on http://localhost:3000 by default)

## Setup Steps

1. Open Claude Desktop
2. Click on "Settings" (gear icon) in the bottom left corner
3. Select "Model Context Protocol" from the settings menu
4. Click "+ Add new MCP server"
5. Enter the following information:
   - **Name**: Solana Trading
   - **URL**: http://localhost:3000
   - **Authentication**: None (leave blank)
6. Click "Save" to add the MCP server
7. Claude should automatically discover the available actions from the server

## Using MCP Actions in Claude

Once connected, you can use natural language to interact with the Solana blockchain through Claude. Here are some example prompts:

- "Check my Solana wallet balance"
- "What's my wallet address?"
- "Get information about this token: [TOKEN_ADDRESS]"

## Available Actions

The following actions are available through the MCP server:

- **GET_ASSET**: Get information about a Solana token
- **BALANCE**: Check your SOL balance
- **WALLET_ADDRESS**: Get your wallet's public key
- **TOKEN_BALANCES**: View your token holdings (placeholder)
- **DEPLOY_TOKEN**: Create a new token (placeholder)
- **TRADE**: Execute token trades (placeholder)

## Example Conversation

```
You: What's my Solana wallet balance?

Claude: Let me check your wallet balance for you.
[MCP Action: BALANCE]
Your current SOL balance is 0.5 SOL in wallet DWg1t9wVBy8NwD1oqP5XBgYVkRWcKPuFjFZMeHx99Ris.
```

## Troubleshooting

If Claude cannot connect to the MCP server:

1. Ensure the server is running (run `node build/index.js` in the mcp-server directory)
2. Check that the URL is correct (http://localhost:3000)
3. Make sure there are no network issues or firewalls blocking the connection
4. Try restarting Claude Desktop
5. Check the server console for any error messages

For more detailed information about the MCP server implementation, please see the README.md file in the mcp-server directory.
