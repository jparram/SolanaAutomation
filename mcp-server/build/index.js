"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
const solana_agent_kit_1 = require("solana-agent-kit");
const dotenv = __importStar(require("dotenv"));
const http_1 = require("http");
const solana_agent_kit_2 = require("solana-agent-kit");
const web3_js_1 = require("@solana/web3.js");
dotenv.config();
// Get RPC URL
const rpcUrl = process.env.RPC_URL || "https://api.mainnet-beta.solana.com";
// Load private key from environment
const privateKeyStr = process.env.SOLANA_PRIVATE_KEY;
let wallet;
if (privateKeyStr) {
    try {
        // Parse private key from string format
        const privateKeyData = JSON.parse(privateKeyStr);
        const keypair = web3_js_1.Keypair.fromSecretKey(Uint8Array.from(privateKeyData), { skipValidation: true });
        wallet = new solana_agent_kit_2.KeypairWallet(keypair, rpcUrl);
        console.log(`Wallet loaded with public key: ${wallet.publicKey.toBase58()}`);
    }
    catch (error) {
        console.error(`Error initializing wallet: ${error}`);
        process.exit(1);
    }
}
else {
    console.warn("No private key provided, generating random keypair");
    wallet = new solana_agent_kit_2.KeypairWallet(web3_js_1.Keypair.generate(), rpcUrl);
    console.log(`Generated wallet with public key: ${wallet.publicKey.toBase58()}`);
}
// Create Solana connection
const connection = new web3_js_1.Connection(rpcUrl);
// Initialize Solana Agent Kit
const agent = new solana_agent_kit_1.SolanaAgentKit(wallet, rpcUrl, {
    OPENAI_API_KEY: process.env.OPENAI_API_KEY || ""
});
// Available actions
const ACTIONS = {
    GET_ASSET: async ({ tokenAddress }) => {
        try {
            // Use the Solana connection to get token/mint info instead of the non-existent getMintInfo
            const mintInfo = await connection.getAccountInfo(new web3_js_1.PublicKey(tokenAddress));
            return {
                success: true,
                data: mintInfo
            };
        }
        catch (error) {
            return {
                success: false,
                error: `Failed to get asset info: ${error}`
            };
        }
    },
    DEPLOY_TOKEN: async ({ name, symbol, initialSupply, decimals = 9 }) => {
        try {
            // This is a placeholder - actual token deployment would require specific implementation
            return {
                success: false,
                error: "Token deployment not implemented yet"
            };
        }
        catch (error) {
            return {
                success: false,
                error: `Token deployment failed: ${error}`
            };
        }
    },
    TRADE: async ({ tokenAddress, amount, isBuy }) => {
        try {
            // Placeholder for trading implementation
            return {
                success: false,
                error: "Trading not implemented yet"
            };
        }
        catch (error) {
            return {
                success: false,
                error: `Trade failed: ${error}`
            };
        }
    },
    BALANCE: async () => {
        try {
            // Get SOL balance
            const balanceResult = await agent.connection.getBalance(wallet.publicKey);
            return {
                success: true,
                data: {
                    sol: balanceResult / 1e9, // Convert lamports to SOL
                    address: wallet.publicKey.toBase58()
                }
            };
        }
        catch (error) {
            return {
                success: false,
                error: `Failed to get balance: ${error}`
            };
        }
    },
    WALLET_ADDRESS: () => {
        return {
            success: true,
            data: {
                address: wallet.publicKey.toBase58()
            }
        };
    },
    TOKEN_BALANCES: async ({ tokenAddresses }) => {
        try {
            // Placeholder for token balances implementation
            return {
                success: false,
                error: "Token balance retrieval not implemented yet"
            };
        }
        catch (error) {
            return {
                success: false,
                error: `Failed to get token balances: ${error}`
            };
        }
    }
};
// Create a basic HTTP server to handle MCP requests
const server = (0, http_1.createServer)((req, res) => {
    // Set CORS headers to allow requests from any origin
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    // Handle preflight requests
    if (req.method === 'OPTIONS') {
        res.writeHead(204);
        res.end();
        return;
    }
    if (req.method === 'POST') {
        let body = '';
        req.on('data', chunk => {
            body += chunk.toString();
        });
        req.on('end', async () => {
            try {
                const request = JSON.parse(body);
                const { action, params } = request;
                console.log(`Received action: ${action}`, params);
                if (action && ACTIONS[action]) {
                    try {
                        const result = await ACTIONS[action](params || {});
                        res.writeHead(200, { 'Content-Type': 'application/json' });
                        res.end(JSON.stringify(result));
                    }
                    catch (actionError) {
                        console.error(`Error executing action ${action}:`, actionError);
                        res.writeHead(400, { 'Content-Type': 'application/json' });
                        res.end(JSON.stringify({
                            success: false,
                            error: `Error executing action ${action}: ${actionError}`
                        }));
                    }
                }
                else {
                    res.writeHead(400, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({
                        success: false,
                        error: `Unknown action: ${action}`
                    }));
                }
            }
            catch (error) {
                console.error(`Error processing request: ${error}`);
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({
                    success: false,
                    error: `Server error: ${error}`
                }));
            }
        });
    }
    else {
        // Return available actions for GET requests
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            success: true,
            availableActions: Object.keys(ACTIONS),
            serverInfo: {
                name: "Solana Trading MCP Server",
                version: "0.0.1",
                wallet: wallet.publicKey.toBase58(),
                rpcUrl: rpcUrl
            }
        }));
    }
});
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`MCP server running at http://localhost:${PORT}`);
    console.log(`Available actions: ${Object.keys(ACTIONS).join(', ')}`);
});
