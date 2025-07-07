# X402 Payment Protocol Integration

This module extends the SolanaAI Agent with support for the x402 payment protocol, enabling automated stablecoin payments directly through HTTP requests.

## Overview

The x402 protocol (and its Solana implementation, s402) allows for instant stablecoin payments through standard HTTP, making it possible for applications, APIs, and AI agents to transact seamlessly without complex wallet interactions.

This integration enables the SolanaAI Agent to:

1. **Automatically handle 402 Payment Required responses** from HTTP requests
2. **Make micropayments using stablecoins** on the Solana blockchain
3. **Access paywalled content and services** with minimal user intervention
4. **Track payment history** for all transactions made through the protocol

## How It Works

The x402 protocol flow is as follows:

1. You make a request to a service through HTTP
2. The server replies with a "402 Payment Required" status and payment details
3. Your client sends a payment using stablecoins through a standard HTTP header
4. A payment facilitator verifies and settles the payment
5. The server provides the requested service

Our implementation handles this entire flow automatically, allowing the agent to seamlessly access paywalled content.

## Components

This integration provides two main implementations:

### 1. Python Implementation (`x402_module.py`)

- **`X402PaymentHandler`**: Handles payments for 402 responses
- **`X402HttpClient`**: HTTP client with automatic x402 payment support
- **`UmiX402Extension`**: Extends the Umi framework with x402 capabilities
- **Integration functions** for SolanaAI Agent

### 2. TypeScript Implementation (`x402-umi-integration.ts`)

- **`X402UmiClient`**: Client for the Umi framework to handle x402 payments
- **`x402Plugin`**: Plugin for easy integration with Umi applications
- **Helper types and utilities** for TypeScript/JavaScript applications

## Installation

The Python implementation is included directly in the SolanaAI Agent project.

For the TypeScript/Umi implementation, you'll need to:

1. Place `x402-umi-integration.ts` in your project
2. Import and use it in your Umi applications

## Usage

### Python Usage

```python
from solana_ai_agent import SolanaAIAgent, SolanaWallet
from x402_module import integrate_x402_with_solana_agent

# Initialize your wallet and agent
wallet = SolanaWallet()
agent = SolanaAIAgent(wallet=wallet)

# Integrate x402 with the agent
payment_handler, http_client = integrate_x402_with_solana_agent(
    agent,
    wallet,
    auto_approve_threshold=0.1  # Auto-approve payments under 0.1 USDC
)

# Now the agent can access paywalled content automatically
result = agent.agent.python_executor("""
x402_request("https://api.example.com/premium-content")
""", agent.agent.state)

print(result)

# Check payment history
for payment in payment_handler.payment_history:
    print(f"{payment['timestamp']}: {payment['amount']} {payment['token']} to {payment['recipient']}")
```

### TypeScript/Umi Usage

```typescript
import { createUmi } from '@metaplex-foundation/umi-bundle-defaults';
import { mplTokenMetadata } from '@metaplex-foundation/mpl-token-metadata';
import { x402Plugin } from './x402-umi-integration';

// Create UMI instance with x402 plugin
const umi = createUmi('https://api.mainnet-beta.solana.com')
  .use(mplTokenMetadata())
  .use(x402Plugin({
    autoApproveThreshold: 0.1,  // Auto-approve payments under 0.1 USDC
  }));

// Make a request with x402 payment support
async function fetchPremiumContent() {
  try {
    const response = await umi.x402.request('https://api.example.com/premium-content');
    console.log('Response:', response.body);
    
    // Check payment history
    const paymentHistory = umi.x402.getPaymentHistory();
    console.log('Payment history:', paymentHistory);
  } catch (error) {
    console.error('Request failed:', error);
  }
}

fetchPremiumContent();
```

## Configuration

Both implementations support the following configuration options:

- **`auto_approve_threshold`**: Maximum amount to auto-approve without confirmation (in USDC)
- **`approval_callback`**: Function to call for payment approval above the threshold
- **`facilitator_url`**: URL of the payment facilitator service

## Security Considerations

- Always set a reasonable `auto_approve_threshold` to prevent excessive spending
- Consider implementing an `approval_callback` for higher value transactions
- Review the payment history regularly to monitor spending
- Be cautious about which services you allow automatic payments to

## Example Applications

### 1. AI Research Assistant

An AI agent can access premium research databases, paying micropayments for each query without requiring subscriptions.

### 2. Content Marketplace Integration

Access premium content across various platforms with pay-as-you-go pricing instead of multiple subscriptions.

### 3. Real-Time Data Analysis

Monitor and analyze financial data from premium APIs, paying only for the specific data points needed.

## Real-World Use Cases

### Pay-Per-Call API Billing

Instead of managing API keys and monthly subscriptions, services can charge precise amounts per request based on actual usage.

### Autonomous Agent Systems

AI agents can independently access paid resources as needed to complete tasks, with budget constraints enforced through the payment threshold.

### Micropayment-Based Content

Content creators can monetize their work through micropayments without relying on advertising or subscription models.

## Resources

- [X402 Protocol Documentation](https://github.com/coinbase/x402)
- [S402 Solana Fork Repository](https://github.com/8bitsats/s402)
- [Solana SPL Token Documentation](https://spl.solana.com/token)
