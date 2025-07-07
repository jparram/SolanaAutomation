import os
import json
import base64
import time
from typing import Dict, Any, Optional, Union, List, Callable
import logging
import requests
from urllib.parse import urlparse

# Solana imports
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.system_program import SYS_PROGRAM_ID
from solana.rpc.types import TxOpts

# Local imports
from solana_ai_agent import SolanaWallet

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("x402_module")

class X402PaymentHandler:
    """
    Handler for x402 protocol payments using the Solana blockchain.
    Allows for automated payments when receiving a 402 Payment Required response.
    """
    
    def __init__(self, 
                 wallet: SolanaWallet,
                 facilitator_url: str = "https://s402.w3hf.fun",
                 auto_approve_threshold: Optional[float] = 0.1,  # Auto-approve payments under 0.1 USDC
                 approval_callback: Optional[Callable[[str, float, str], bool]] = None):
        """
        Initialize the X402 payment handler.
        
        Args:
            wallet: SolanaWallet instance for making payments.
            facilitator_url: URL of the payment facilitator service.
            auto_approve_threshold: Maximum amount to auto-approve without confirmation (in USDC).
            approval_callback: Function to call for payment approval above the threshold.
        """
        self.wallet = wallet
        self.facilitator_url = facilitator_url
        self.auto_approve_threshold = auto_approve_threshold
        self.approval_callback = approval_callback
        self.payment_history = []
        
        # Load token info for supported tokens (primarily stablecoins)
        self.supported_tokens = {
            "USDC": {
                "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                "decimals": 6
            },
            "USDT": {
                "mint": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
                "decimals": 6
            },
        }
    
    def _get_payment_headers(self, payment_info: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate HTTP headers for x402 payment.
        
        Args:
            payment_info: Payment information including token, amount, and recipient.
            
        Returns:
            Dict[str, str]: HTTP headers for the payment.
        """
        return {
            "X-402-Payment-Token": payment_info.get("token", "USDC"),
            "X-402-Payment-Amount": str(payment_info.get("amount")),
            "X-402-Payment-Recipient": payment_info.get("recipient"),
            "X-402-Payment-Nonce": str(int(time.time())),
            "X-402-Payment-Signature": self._generate_payment_signature(payment_info),
        }
    
    def _generate_payment_signature(self, payment_info: Dict[str, Any]) -> str:
        """
        Generate a signature for the payment using the wallet's keypair.
        
        Args:
            payment_info: Payment information.
            
        Returns:
            str: Base64-encoded signature.
        """
        # Create a message to sign containing payment details
        message = f"{payment_info.get('recipient')}:{payment_info.get('token')}:{payment_info.get('amount')}:{int(time.time())}"
        message_bytes = message.encode('utf-8')
        
        # Sign the message with the wallet's keypair
        signature = self.wallet.keypair.sign(message_bytes)
        
        # Return base64 encoded signature
        return base64.b64encode(signature).decode('utf-8')
    
    def _should_approve_payment(self, amount: float, token: str, service_url: str) -> bool:
        """
        Determine if a payment should be automatically approved.
        
        Args:
            amount: Payment amount.
            token: Token symbol.
            service_url: URL of the service requiring payment.
            
        Returns:
            bool: Whether the payment should be approved.
        """
        # Auto-approve if under threshold
        if amount <= self.auto_approve_threshold:
            return True
        
        # Use callback if provided
        if self.approval_callback:
            return self.approval_callback(service_url, amount, token)
        
        # Default to manual approval via console input
        approval = input(f"Approve payment of {amount} {token} to {service_url}? (y/n): ")
        return approval.lower() in ['y', 'yes']
    
    def _execute_payment(self, payment_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a payment on the Solana blockchain.
        
        Args:
            payment_info: Payment details including token, amount, and recipient.
            
        Returns:
            Dict[str, Any]: Transaction result.
        """
        # For now, we'll simulate the payment and return a mock transaction result
        # In a real implementation, this would create and send an SPL token transfer transaction
        
        logger.info(f"Executing payment: {payment_info['amount']} {payment_info['token']} to {payment_info['recipient']}")
        
        # Record the payment
        self.payment_history.append({
            "timestamp": time.time(),
            "amount": payment_info["amount"],
            "token": payment_info["token"],
            "recipient": payment_info["recipient"],
            "service": payment_info.get("service_url", "unknown"),
        })
        
        # Mock transaction result
        return {
            "success": True,
            "txid": f"simulated_tx_{int(time.time())}",
            "amount": payment_info["amount"],
            "token": payment_info["token"],
        }
    
    def handle_402_response(self, 
                           response: requests.Response, 
                           original_request: requests.Request) -> Dict[str, Any]:
        """
        Handle a 402 Payment Required response.
        
        Args:
            response: The 402 response from the server.
            original_request: The original request that triggered the 402.
            
        Returns:
            Dict[str, Any]: Payment result and new response after payment.
        """
        # Extract payment information from the response headers
        payment_info = {
            "token": response.headers.get("X-402-Payment-Token", "USDC"),
            "amount": float(response.headers.get("X-402-Payment-Amount", "0")),
            "recipient": response.headers.get("X-402-Payment-Recipient", ""),
            "service_url": original_request.url,
        }
        
        # Validate payment information
        if not payment_info["recipient"] or payment_info["amount"] <= 0:
            logger.error("Invalid payment information in 402 response")
            return {
                "success": False,
                "error": "Invalid payment information",
                "response": response
            }
        
        # Check if payment should be approved
        if not self._should_approve_payment(
            payment_info["amount"], 
            payment_info["token"],
            payment_info["service_url"]
        ):
            logger.info("Payment not approved by user")
            return {
                "success": False,
                "error": "Payment not approved",
                "response": response
            }
        
        # Execute the payment
        payment_result = self._execute_payment(payment_info)
        
        if not payment_result["success"]:
            logger.error(f"Payment failed: {payment_result.get('error', 'Unknown error')}")
            return {
                "success": False,
                "error": f"Payment failed: {payment_result.get('error', 'Unknown error')}",
                "response": response
            }
        
        # Retry the original request with payment headers
        payment_headers = self._get_payment_headers(payment_info)
        payment_headers["X-402-Payment-Transaction"] = payment_result["txid"]
        
        # Create a new request with payment headers
        new_request = original_request.copy()
        for key, value in payment_headers.items():
            new_request.headers[key] = value
        
        # Send the new request
        try:
            new_response = requests.Session().send(new_request.prepare())
            return {
                "success": True,
                "payment": payment_result,
                "response": new_response
            }
        except Exception as e:
            logger.error(f"Failed to retry request after payment: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to retry request: {str(e)}",
                "payment": payment_result,
                "response": response
            }


class X402HttpClient:
    """
    HTTP client with x402 payment protocol support.
    """
    
    def __init__(self, payment_handler: X402PaymentHandler):
        """
        Initialize the x402-enabled HTTP client.
        
        Args:
            payment_handler: Handler for x402 payments.
        """
        self.payment_handler = payment_handler
        self.session = requests.Session()
    
    def request(self, 
               method: str, 
               url: str, 
               headers: Optional[Dict[str, str]] = None, 
               data: Optional[Any] = None,
               json: Optional[Dict[str, Any]] = None,
               params: Optional[Dict[str, Any]] = None,
               auto_handle_402: bool = True,
               **kwargs) -> requests.Response:
        """
        Send an HTTP request with support for x402 payment protocol.
        
        Args:
            method: HTTP method to use.
            url: URL to send the request to.
            headers: Request headers.
            data: Request body data.
            json: JSON data to send.
            params: URL parameters.
            auto_handle_402: Whether to automatically handle 402 responses.
            **kwargs: Additional arguments to pass to requests.
            
        Returns:
            requests.Response: Response from the server.
        """
        # Prepare the request
        req = requests.Request(
            method=method,
            url=url,
            headers=headers or {},
            data=data,
            json=json,
            params=params,
            **kwargs
        )
        prepped = req.prepare()
        
        # Send the request
        response = self.session.send(prepped)
        
        # Handle 402 Payment Required response
        if response.status_code == 402 and auto_handle_402:
            logger.info(f"Received 402 Payment Required response from {url}")
            payment_result = self.payment_handler.handle_402_response(response, req)
            
            if payment_result["success"]:
                logger.info(f"Payment successful, received new response with status {payment_result['response'].status_code}")
                return payment_result["response"]
            else:
                logger.warning(f"Payment failed: {payment_result.get('error', 'Unknown error')}")
        
        return response
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """Shorthand for GET request."""
        return self.request("GET", url, **kwargs)
    
    def post(self, url: str, **kwargs) -> requests.Response:
        """Shorthand for POST request."""
        return self.request("POST", url, **kwargs)
    
    def put(self, url: str, **kwargs) -> requests.Response:
        """Shorthand for PUT request."""
        return self.request("PUT", url, **kwargs)
    
    def delete(self, url: str, **kwargs) -> requests.Response:
        """Shorthand for DELETE request."""
        return self.request("DELETE", url, **kwargs)


class UmiX402Extension:
    """
    Extension for Umi to support x402 payments protocol.
    This extends Umi's HTTP interface to handle 402 payment required responses.
    """
    
    def __init__(self, payment_handler: X402PaymentHandler):
        """
        Initialize the Umi x402 extension.
        
        Args:
            payment_handler: Handler for x402 payments.
        """
        self.payment_handler = payment_handler
    
    def install(self, umi: Any) -> None:
        """
        Install the x402 extension into a Umi instance.
        
        Args:
            umi: The Umi instance to extend.
        """
        # Store the original HTTP send method
        original_send = umi.http.send
        
        # Override the HTTP send method with x402 handling
        async def send_with_x402(request):
            # Convert Umi request to requests-compatible format
            method = request.method
            url = request.url
            headers = request.headers or {}
            
            # Get body data if present
            data = None
            if request.body:
                data = request.body
            
            # Create a requests.Request object
            req = requests.Request(
                method=method,
                url=url,
                headers=headers,
                data=data,
            )
            prepped = req.prepare()
            
            # Send the request
            session = requests.Session()
            response = session.send(prepped)
            
            # Handle 402 Payment Required response
            if response.status_code == 402:
                logger.info(f"Received 402 Payment Required response from {url}")
                payment_result = self.payment_handler.handle_402_response(response, req)
                
                if payment_result["success"]:
                    # Convert the response back to Umi format
                    return {
                        "status": payment_result["response"].status_code,
                        "headers": dict(payment_result["response"].headers),
                        "body": payment_result["response"].content,
                    }
            
            # Continue with original response
            return original_send(request)
        
        # Replace the HTTP send method
        umi.http.send = send_with_x402
        
        # Add x402 utilities to the Umi instance
        umi.x402 = {
            "payment_handler": self.payment_handler,
            "payment_history": self.payment_handler.payment_history,
        }


# Example usage with the SolanaAI agent system
def integrate_x402_with_solana_agent(agent, wallet, auto_approve_threshold=0.1):
    """
    Integrate x402 payment protocol with the SolanaAI agent.
    
    Args:
        agent: SolanaAI agent instance.
        wallet: SolanaWallet instance.
        auto_approve_threshold: Maximum amount to auto-approve without confirmation.
        
    Returns:
        tuple: (X402PaymentHandler, X402HttpClient) - The configured handler and client.
    """
    # Create the payment handler
    payment_handler = X402PaymentHandler(
        wallet=wallet,
        auto_approve_threshold=auto_approve_threshold,
        approval_callback=None  # Could add a callback for agent to decide on payments
    )
    
    # Create the HTTP client
    http_client = X402HttpClient(payment_handler)
    
    # Add x402 capability to the agent
    agent.x402_handler = payment_handler
    agent.x402_client = http_client
    
    # Add x402 HTTP request tool to the agent
    @agent.agent.tool.register("x402_request")
    def x402_request(url: str, method: str = "GET", data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make an HTTP request with x402 payment protocol support.
        
        Args:
            url: URL to send the request to.
            method: HTTP method to use (GET, POST, PUT, DELETE).
            data: Data to send with the request.
            
        Returns:
            Dict[str, Any]: Response information.
        """
        try:
            response = http_client.request(method, url, json=data)
            
            # Return a simplified response
            return {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "content": response.text,
                "payment_made": response.status_code == 200 and response.request.headers.get("X-402-Payment-Transaction") is not None,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    return payment_handler, http_client


# Extension for Umi framework to support x402
def extend_umi_with_x402(umi, wallet):
    """
    Extend a Umi instance with x402 payment protocol support.
    
    Args:
        umi: The Umi instance to extend.
        wallet: SolanaWallet instance for making payments.
        
    Returns:
        Any: The extended Umi instance.
    """
    # Create the payment handler
    payment_handler = X402PaymentHandler(wallet=wallet)
    
    # Create and install the extension
    extension = UmiX402Extension(payment_handler)
    extension.install(umi)
    
    return umi
