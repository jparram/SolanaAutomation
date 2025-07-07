import { createUmi } from '@metaplex-foundation/umi-bundle-defaults';
import { publicKey, Signer, TransactionBuilder } from '@metaplex-foundation/umi';
import { request } from '@metaplex-foundation/umi';

/**
 * X402 Payment Protocol client for UMI framework
 * Implements the x402 protocol for HTTP payments using UMI's HTTP interface
 */
export class X402UmiClient {
  private umi: any;
  private wallet: Signer;
  private paymentHistory: X402Payment[] = [];
  private autoApproveThreshold: number;
  private approvalCallback?: (url: string, amount: number, token: string) => Promise<boolean>;
  private facilitatorUrl: string;

  /**
   * Create a new X402UmiClient
   * 
   * @param umi - UMI instance
   * @param wallet - Wallet signer to use for payments
   * @param options - Configuration options
   */
  constructor(umi: any, wallet: Signer, options?: {
    autoApproveThreshold?: number;
    approvalCallback?: (url: string, amount: number, token: string) => Promise<boolean>;
    facilitatorUrl?: string;
  }) {
    this.umi = umi;
    this.wallet = wallet;
    this.autoApproveThreshold = options?.autoApproveThreshold ?? 0.1;
    this.approvalCallback = options?.approvalCallback;
    this.facilitatorUrl = options?.facilitatorUrl ?? 'https://s402.w3hf.fun';
    
    // Install the HTTP interceptor
    this.installHttpInterceptor();
  }

  /**
   * Install an HTTP interceptor to handle 402 responses
   */
  private installHttpInterceptor(): void {
    const originalSend = this.umi.http.send;
    
    this.umi.http.send = async (httpRequest: any) => {
      const response = await originalSend(httpRequest);
      
      // Check if it's a 402 Payment Required response
      if (response.status === 402) {
        console.log(`Received 402 Payment Required response from ${httpRequest.url}`);
        
        // Extract payment information from headers
        const paymentInfo = this.extractPaymentInfo(response, httpRequest.url);
        
        // Check if payment should be approved
        const shouldPay = await this.shouldApprovePay(
          paymentInfo.amount,
          paymentInfo.token,
          httpRequest.url
        );
        
        if (shouldPay) {
          // Execute payment
          const paymentResult = await this.executePayment(paymentInfo);
          
          if (paymentResult.success) {
            // Retry the request with payment headers
            const newRequest = { 
              ...httpRequest, 
              headers: {
                ...httpRequest.headers,
                'X-402-Payment-Token': paymentInfo.token,
                'X-402-Payment-Amount': paymentInfo.amount.toString(),
                'X-402-Payment-Recipient': paymentInfo.recipient,
                'X-402-Payment-Transaction': paymentResult.txid,
                'X-402-Payment-Nonce': Date.now().toString(),
                'X-402-Payment-Signature': paymentResult.signature,
              }
            };
            
            // Send the new request
            return await originalSend(newRequest);
          } else {
            console.error(`Payment failed: ${paymentResult.error}`);
            return response;
          }
        } else {
          console.log('Payment not approved by user');
          return response;
        }
      }
      
      return response;
    };
  }

  /**
   * Extract payment information from a 402 response
   * 
   * @param response - HTTP response
   * @param serviceUrl - Service URL that requested payment
   * @returns Payment information
   */
  private extractPaymentInfo(response: any, serviceUrl: string): X402PaymentInfo {
    const headers = response.headers;
    
    return {
      token: headers['x-402-payment-token'] || 'USDC',
      amount: parseFloat(headers['x-402-payment-amount'] || '0'),
      recipient: headers['x-402-payment-recipient'] || '',
      serviceUrl,
    };
  }

  /**
   * Determine if a payment should be approved
   * 
   * @param amount - Payment amount
   * @param token - Token symbol
   * @param serviceUrl - Service URL requesting payment
   * @returns Whether the payment should be approved
   */
  private async shouldApprovePay(amount: number, token: string, serviceUrl: string): Promise<boolean> {
    // Auto-approve if under threshold
    if (amount <= this.autoApproveThreshold) {
      return true;
    }
    
    // Use callback if provided
    if (this.approvalCallback) {
      return await this.approvalCallback(serviceUrl, amount, token);
    }
    
    // Default to manual approval via console - not ideal for production
    // In a real implementation, this would show a UI prompt or use a different mechanism
    console.log(`Payment required: ${amount} ${token} to ${serviceUrl}`);
    console.log('Auto-approval threshold exceeded. Payment will not be processed automatically.');
    return false;
  }

  /**
   * Execute a payment transaction
   * 
   * @param paymentInfo - Payment information
   * @returns Payment result
   */
  private async executePayment(paymentInfo: X402PaymentInfo): Promise<X402PaymentResult> {
    try {
      console.log(`Executing payment: ${paymentInfo.amount} ${paymentInfo.token} to ${paymentInfo.recipient}`);
      
      // For token transfers, we would need to create and submit the appropriate transaction
      // This is a simplified implementation
      
      // Create a transaction to transfer tokens
      const tx = await this.createPaymentTransaction(paymentInfo);
      
      // Sign and send the transaction
      const result = await tx.sendAndConfirm(this.umi);
      
      // Record the payment
      const payment: X402Payment = {
        timestamp: new Date(),
        amount: paymentInfo.amount,
        token: paymentInfo.token,
        recipient: paymentInfo.recipient,
        serviceUrl: paymentInfo.serviceUrl,
        txid: result.signature,
      };
      
      this.paymentHistory.push(payment);
      
      // Return the payment result
      return {
        success: true,
        txid: result.signature,
        amount: paymentInfo.amount,
        token: paymentInfo.token,
        signature: await this.generatePaymentSignature(paymentInfo, result.signature),
      };
    } catch (error) {
      console.error('Payment execution failed:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : String(error),
      };
    }
  }

  /**
   * Create a payment transaction
   * 
   * @param paymentInfo - Payment information
   * @returns Transaction builder
   */
  private async createPaymentTransaction(paymentInfo: X402PaymentInfo): Promise<TransactionBuilder> {
    // This is a simplified implementation
    // In a real implementation, this would create the appropriate token transfer transaction
    
    // We would need to verify that we have sufficient balance of the token
    // and create the appropriate SPL token transfer instructions
    
    // For demonstration purposes, we're just creating a placeholder transaction
    return TransactionBuilder.make()
      .add({
        instruction: {
          programId: publicKey('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'),
          keys: [
            { pubkey: this.wallet.publicKey, isSigner: true, isWritable: true },
            { pubkey: publicKey(paymentInfo.recipient), isSigner: false, isWritable: true },
          ],
          data: new Uint8Array([]),
        },
      });
  }

  /**
   * Generate a payment signature for verification
   * 
   * @param paymentInfo - Payment information
   * @param txid - Transaction ID
   * @returns Payment signature
   */
  private async generatePaymentSignature(paymentInfo: X402PaymentInfo, txid: string): Promise<string> {
    // Create a message to sign
    const message = `${paymentInfo.recipient}:${paymentInfo.token}:${paymentInfo.amount}:${txid}`;
    
    // Sign the message
    const signature = await this.umi.signMessage(this.wallet, new TextEncoder().encode(message));
    
    // Return base64 encoded signature
    return Buffer.from(signature).toString('base64');
  }

  /**
   * Get payment history
   * 
   * @returns Array of payments made
   */
  public getPaymentHistory(): X402Payment[] {
    return [...this.paymentHistory];
  }

  /**
   * Make a HTTP request with x402 payment support
   * 
   * @param url - URL to request
   * @param method - HTTP method
   * @param options - Request options
   * @returns HTTP response
   */
  public async request(url: string, method: 'get' | 'post' | 'put' | 'delete' = 'get', options?: {
    headers?: Record<string, string>;
    data?: any;
    asJson?: boolean;
  }): Promise<any> {
    // Create the HTTP request
    let req = request().url(url).method(method);
    
    // Add headers if provided
    if (options?.headers) {
      for (const [key, value] of Object.entries(options.headers)) {
        req = req.header(key, value);
      }
    }
    
    // Add data if provided
    if (options?.data) {
      req = req.withData(options.data);
    }
    
    // Set response type
    if (options?.asJson !== false) {
      req = req.asJson();
    }
    
    // Send the request (this will automatically handle 402 responses)
    return await this.umi.http.send(req);
  }
}

/**
 * Payment information extracted from a 402 response
 */
export interface X402PaymentInfo {
  token: string;
  amount: number;
  recipient: string;
  serviceUrl: string;
}

/**
 * Result of a payment operation
 */
export interface X402PaymentResult {
  success: boolean;
  txid?: string;
  amount?: number;
  token?: string;
  signature?: string;
  error?: string;
}

/**
 * Record of a completed payment
 */
export interface X402Payment {
  timestamp: Date;
  amount: number;
  token: string;
  recipient: string;
  serviceUrl: string;
  txid: string;
}

/**
 * Create a new X402UmiClient instance
 * 
 * @param umi - UMI instance
 * @param wallet - Wallet signer
 * @param options - Configuration options
 * @returns X402UmiClient instance
 */
export function createX402Client(umi: any, wallet: Signer, options?: {
  autoApproveThreshold?: number;
  approvalCallback?: (url: string, amount: number, token: string) => Promise<boolean>;
  facilitatorUrl?: string;
}): X402UmiClient {
  return new X402UmiClient(umi, wallet, options);
}

/**
 * X402 UMI plugin for installation
 * 
 * @param options - Configuration options
 * @returns UMI plugin
 */
export function x402Plugin(options?: {
  autoApproveThreshold?: number;
  facilitatorUrl?: string;
}) {
  return {
    install(umi: any) {
      const x402Client = new X402UmiClient(umi, umi.identity, {
        autoApproveThreshold: options?.autoApproveThreshold,
        facilitatorUrl: options?.facilitatorUrl,
      });
      
      // Add x402 methods to UMI instance
      umi.x402 = {
        request: x402Client.request.bind(x402Client),
        getPaymentHistory: x402Client.getPaymentHistory.bind(x402Client),
      };
    },
  };
}

// Example usage:
/*
import { createUmi } from '@metaplex-foundation/umi-bundle-defaults';
import { createSignerFromKeypair, generateSigner } from '@metaplex-foundation/umi';
import { x402Plugin } from './x402-umi-plugin';

// Create UMI instance
const umi = createUmi('https://api.mainnet-beta.solana.com');

// Add x402 plugin
umi.use(x402Plugin({
  autoApproveThreshold: 0.1, // Auto-approve payments under 0.1 USDC
}));

// Make a request that might require payment
async function fetchPaidContent() {
  try {
    const response = await umi.x402.request('https://api.example.com/premium-content', 'get');
    console.log('Response:', response.body);
    
    // Check payment history
    const paymentHistory = umi.x402.getPaymentHistory();
    console.log('Payment history:', paymentHistory);
  } catch (error) {
    console.error('Request failed:', error);
  }
}

fetchPaidContent();
*/
