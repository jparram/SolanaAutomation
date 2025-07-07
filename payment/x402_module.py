import logging
import json
import time
from typing import Optional, Dict, Any, List, Union, Tuple
import aiohttp
import requests
from urllib.parse import urlparse, urljoin
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class X402PaymentInfo:
    """Data structure to hold x402 payment details"""
    amount: int
    token_mint: str
    recipient: str
    reference: str
    memo: Optional[str] = None
    expiration: Optional[int] = None
    facilitator: Optional[str] = None

@dataclass
class X402PaymentHistory:
    """Track payment history for a given endpoint"""
    url: str
    amount_paid: int
    token_mint: str
    transaction_signature: str
    timestamp: int
    expiration: Optional[int] = None
    

class X402PaymentHandler:
    """
    Handler for x402 protocol payments using the Solana blockchain.
    """
    def __init__(self, wallet: Any, facilitator_url: Optional[str] = None):
        self.wallet = wallet
        self.facilitator_url = facilitator_url or "https://x402-facilitator.solana.com"
        self.payment_history: List[X402PaymentHistory] = []
        self.supported_tokens = {
            "So11111111111111111111111111111111111111112": "SOL",  # Native SOL
            "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v": "USDC",  # USDC
            "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB": "USDT",  # USDT
        }
        
    def _parse_payment_headers(self, headers: Dict[str, str]) -> Optional[X402PaymentInfo]:
        """Parse x402 payment headers from response"""
        try:
            if 'x-402-payment-required' not in headers:
                return None
                
            payment_data = json.loads(headers['x-402-payment-required'])
            return X402PaymentInfo(
                amount=int(payment_data.get('amount', 0)),
                token_mint=payment_data.get('tokenMint', ''),
                recipient=payment_data.get('recipient', ''),
                reference=payment_data.get('reference', ''),
                memo=payment_data.get('memo'),
                expiration=payment_data.get('expiration'),
                facilitator=payment_data.get('facilitator', self.facilitator_url)
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Error parsing x402 payment headers: {e}")
            return None
    
    def _check_payment_history(self, url: str, payment_info: X402PaymentInfo) -> bool:
        """Check if we have already paid for this resource recently"""
        current_time = int(time.time())
        
        # Find matching payments that haven't expired
        for payment in self.payment_history:
            if payment.url == url and payment.token_mint == payment_info.token_mint:
                # If no expiration or not expired yet
                if not payment.expiration or payment.expiration > current_time:
                    logger.info(f"Found valid payment in history for {url}")
                    return True
                    
        return False
        
    async def process_payment(self, payment_info: X402PaymentInfo) -> Optional[str]:
        """Process the actual payment transaction"""
        try:
            logger.info(f"Processing payment of {payment_info.amount} tokens to {payment_info.recipient}")
            
            # For simulation mode, return a fake signature
            if not hasattr(self.wallet, 'send_transaction') or not callable(getattr(self.wallet, 'send_transaction', None)):
                logger.warning("Wallet does not support send_transaction, returning simulated signature")
                return f"SIMULATED_TX_SIG_{int(time.time())}"
            
            # Convert to lamports if SOL
            amount = payment_info.amount
            if payment_info.token_mint == "So11111111111111111111111111111111111111112":
                # Process native SOL payment
                tx_sig = await self.wallet.send_transaction(
                    to_pubkey=payment_info.recipient,
                    amount_lamports=amount,
                    memo=payment_info.memo,
                    reference=payment_info.reference
                )
            else:
                # Process SPL token payment
                tx_sig = await self.wallet.send_token_transaction(
                    token_mint=payment_info.token_mint,
                    to_pubkey=payment_info.recipient,
                    amount=amount,
                    memo=payment_info.memo,
                    reference=payment_info.reference
                )
                
            return tx_sig
            
        except Exception as e:
            logger.error(f"Payment processing error: {e}")
            return None
            
    async def verify_payment(self, payment_info: X402PaymentInfo, tx_sig: str) -> bool:
        """Verify payment was successful using facilitator"""
        if not payment_info.facilitator:
            logger.warning("No facilitator URL provided for payment verification")
            return True  # Assume success if no facilitator
            
        try:
            facilitator_url = urljoin(payment_info.facilitator, f"/verify/{tx_sig}")
            async with aiohttp.ClientSession() as session:
                async with session.get(facilitator_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('verified', False)
                    else:
                        logger.error(f"Facilitator verification failed: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Error verifying payment: {e}")
            return False

    async def handle_402_response(self, response: Union[requests.Response, aiohttp.ClientResponse], 
                              original_request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a 402 Payment Required response"""
        logger.info("Handling 402 Payment Required response")
        
        # Extract headers based on response type
        if isinstance(response, requests.Response):
            headers = dict(response.headers)
        else:  # aiohttp.ClientResponse
            headers = dict(response.headers)
            
        payment_info = self._parse_payment_headers(headers)
        if not payment_info:
            logger.error("Invalid or missing x402 payment headers")
            return {"success": False, "message": "Invalid payment headers"}
            
        # Check payment history to avoid paying again
        url = str(original_request.get('url', ''))
        if self._check_payment_history(url, payment_info):
            return {"success": True, "message": "Already paid", "cached": True}
        
        # Process the payment
        tx_sig = await self.process_payment(payment_info)
        if not tx_sig:
            return {"success": False, "message": "Payment failed"}    
        
        # Verify payment if facilitator available
        verified = await self.verify_payment(payment_info, tx_sig)
        if not verified:
            return {"success": False, "message": "Payment verification failed"}
        
        # Store payment in history
        self.payment_history.append(X402PaymentHistory(
            url=url,
            amount_paid=payment_info.amount,
            token_mint=payment_info.token_mint,
            transaction_signature=tx_sig,
            timestamp=int(time.time()),
            expiration=payment_info.expiration
        ))
        
        return {
            "success": True, 
            "message": "Payment successful",
            "transaction": tx_sig,
            "amount": payment_info.amount,
            "token": self.supported_tokens.get(payment_info.token_mint, payment_info.token_mint)
        }

class X402HttpClient:
    """
    HTTP client with x402 payment protocol support.
    """
    def __init__(self, payment_handler: X402PaymentHandler):
        self.payment_handler = payment_handler
        self.session = requests.Session()
        self.max_payment_attempts = 3
        
    def _prepare_request_args(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Prepare request arguments for both sync and async requests"""
        request_args = {
            'method': method,
            'url': url,
            **kwargs
        }
        
        # Add x402 protocol headers
        headers = kwargs.get('headers', {})
        headers['Accept'] = 'application/json, */*'
        headers['X-402-Protocol-Version'] = '1.0'
        request_args['headers'] = headers
        
        return request_args
    
    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make a request with x402 payment support"""
        logger.info(f"Making {method} request to {url} with x402 support")
        
        request_args = self._prepare_request_args(method, url, **kwargs)
        attempts = 0
        
        while attempts < self.max_payment_attempts:
            response = self.session.request(**request_args)
            
            if response.status_code != 402:
                return response
                
            logger.info(f"Received 402 Payment Required from {url}")
            
            # Handle payment synchronously (using asyncio.run for the async handler)
            import asyncio
            payment_result = asyncio.run(self.payment_handler.handle_402_response(
                response, request_args
            ))
            
            if not payment_result['success']:
                logger.error(f"Payment failed: {payment_result['message']}")
                return response
            
            # Retry the request after successful payment
            attempts += 1
            logger.info(f"Payment successful, retrying request (attempt {attempts})")
        
        logger.error(f"Max payment attempts ({self.max_payment_attempts}) reached")
        return response
        
    async def async_request(self, method: str, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make an async request with x402 payment support"""
        logger.info(f"Making async {method} request to {url} with x402 support")
        
        request_args = self._prepare_request_args(method, url, **kwargs)
        attempts = 0
        
        async with aiohttp.ClientSession() as session:
            while attempts < self.max_payment_attempts:
                async with session.request(request_args['method'], request_args['url'], 
                                          headers=request_args.get('headers', {}),
                                          params=request_args.get('params', {}),
                                          json=request_args.get('json'),
                                          data=request_args.get('data')) as response:
                    
                    if response.status != 402:
                        return response
                        
                    logger.info(f"Received 402 Payment Required from {url}")
                    
                    # Handle payment
                    payment_result = await self.payment_handler.handle_402_response(
                        response, request_args
                    )
                    
                    if not payment_result['success']:
                        logger.error(f"Payment failed: {payment_result['message']}")
                        return response
                
                # Retry the request after successful payment
                attempts += 1
                logger.info(f"Payment successful, retrying request (attempt {attempts})")
            
            logger.error(f"Max payment attempts ({self.max_payment_attempts}) reached")
            return response