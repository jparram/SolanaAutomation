#!/usr/bin/env python
"""
Test Script for Solana Web Browser
This script demonstrates how to use the SolanaWebBrowser class for Solana-related web automation.
"""

import os
import sys
import time
import logging
import argparse
from solana_web_browser import SolanaWebBrowser
from selenium.webdriver.common.by import By

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_argparse():
    """Configure command line arguments"""
    parser = argparse.ArgumentParser(description='Test the Solana Web Browser')
    parser.add_argument(
        '--headless', 
        action='store_true', 
        help='Run browser in headless mode'
    )
    parser.add_argument(
        '--task', 
        choices=['explorer', 'token', 'navigate', 'all'],
        default='all',
        help='Specific task to run'
    )
    parser.add_argument(
        '--address',
        type=str,
        default='4Zw5RukqrwJMV3FVaHJgPXz7HEyGbhJq4L9L9YpmMhRW',
        help='Solana address to check (for explorer task)'
    )
    parser.add_argument(
        '--token',
        type=str,
        default='SOL',
        help='Token symbol to check (for token task)'
    )
    return parser.parse_args()

def test_explorer(browser, address):
    """Test checking a Solana address on the explorer"""
    logger.info(f"Testing explorer functionality with address: {address}")
    result = browser.check_solana_explorer(address)
    
    logger.info("Explorer test results:")
    for key, value in result.items():
        if key != 'screenshot':  # Don't print the screenshot path
            logger.info(f"  {key}: {value}")
    logger.info(f"  screenshot: {os.path.basename(result.get('screenshot', ''))}")
    
    return result

def test_token_price(browser, token):
    """Test checking a token price"""
    logger.info(f"Testing token price lookup for: {token}")
    result = browser.check_token_price(token)
    
    logger.info("Token price test results:")
    for key, value in result.items():
        if key != 'screenshot':  # Don't print the screenshot path
            logger.info(f"  {key}: {value}")
    logger.info(f"  screenshot: {os.path.basename(result.get('screenshot', ''))}")
    
    return result

def test_navigation(browser):
    """Test basic navigation"""
    logger.info("Testing navigation to Solana.com")
    result = browser.run("navigate to solana.com")
    
    logger.info("Navigation test results:")
    if isinstance(result, dict):
        for key, value in result.items():
            if key != 'screenshot':  # Don't print the screenshot path
                logger.info(f"  {key}: {value}")
        logger.info(f"  screenshot: {os.path.basename(result.get('screenshot', ''))}")
    else:
        logger.info(f"  result: {result}")
    
    return result

def main():
    """Main test function"""
    args = setup_argparse()
    
    logger.info(f"Initializing browser (headless: {args.headless})")
    browser = None
    
    try:
        # Initialize the browser
        browser = SolanaWebBrowser(headless=args.headless)
        logger.info("Browser initialized successfully")
        
        # Run requested tests
        if args.task in ('explorer', 'all'):
            test_explorer(browser, args.address)
            time.sleep(2)  # Short pause between tasks
            
        if args.task in ('token', 'all'):
            test_token_price(browser, args.token)
            time.sleep(2)  # Short pause between tasks
            
        if args.task in ('navigate', 'all'):
            test_navigation(browser)
        
        logger.info("Tests completed successfully")
        
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}")
        sys.exit(1)
        
    finally:
        # Clean up
        if browser:
            logger.info("Closing browser")
            browser.close()

if __name__ == "__main__":
    main()
