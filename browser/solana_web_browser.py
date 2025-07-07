import logging
import os
import time
from typing import Optional, Dict, List, Any, Union
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException

# Configure logging
logger = logging.getLogger(__name__)

# Constants
DEFAULT_WAIT_TIME = 10  # seconds
SCREENSHOT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "screenshots"
)


class SolanaWebBrowser:
    """
    A browser automation class for Solana-specific tasks.
    
    Provides browser automation capabilities for interacting with Solana-related 
    websites, including DEXs, portfolio trackers, and explorers.
    """
    def __init__(self, headless: Optional[bool] = None, model_id: Optional[str] = None):
        """
        Initialize the Solana web browser.
        
        Args:
            headless: Whether to run the browser in headless mode
            model_id: ID of the model/profile to use
        """
        self.headless = headless if headless is not None else False
        self.model_id = model_id or "default"
        self.driver = None
        self.wait = None
        self.current_url = None
        self.task_results = []
        
        # Create screenshots directory if it doesn't exist
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        
        # Initialize the browser
        self._initialize_browser()
        logger.info(f"Initialized SolanaWebBrowser with model_id: {self.model_id}, headless: {self.headless}")
    
    def _initialize_browser(self) -> None:
        """Initialize the Selenium WebDriver with appropriate options."""
        try:
            options = ChromeOptions()
            
            # Configure Chrome options
            if self.headless:
                options.add_argument("--headless=new")
            
            # Add additional options for stability and performance
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-notifications")
            
            # Initialize the driver
            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, DEFAULT_WAIT_TIME)
            
            # Set window size
            self.driver.set_window_size(1920, 1080)
            
            logger.info("Browser initialized successfully")
        except WebDriverException as e:
            logger.error(f"Failed to initialize browser: {str(e)}")
            raise
    
    def __del__(self):
        """Clean up resources when the object is destroyed."""
        self.close()
    
    def close(self) -> None:
        """Close the browser and clean up resources."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser closed")
            except Exception as e:
                logger.error(f"Error closing browser: {str(e)}")
            finally:
                self.driver = None
                self.wait = None

    def navigate_to(self, url: str) -> bool:
        """Navigate to the specified URL."""
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        try:
            self.driver.get(url)
            self.current_url = self.driver.current_url
            logger.info(f"Navigated to: {url}")
            return True
        except WebDriverException as e:
            logger.error(f"Failed to navigate to {url}: {str(e)}")
            return False
    
    def screenshot(self, name: Optional[str] = None) -> str:
        """Take a screenshot of the current page."""
        if not name:
            name = f"screenshot_{time.strftime('%Y%m%d_%H%M%S')}.png"
        elif not name.endswith(".png"):
            name += ".png"
        
        filepath = os.path.join(SCREENSHOT_DIR, name)
        try:
            self.driver.save_screenshot(filepath)
            logger.info(f"Screenshot saved to: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to take screenshot: {str(e)}")
            return ""
    
    def find_element(self, by: By, value: str, timeout: int = DEFAULT_WAIT_TIME) -> Any:
        """Find an element on the page with wait support."""
        try:
            element = self.wait.until(EC.presence_of_element_located((by, value)))
            return element
        except TimeoutException:
            logger.warning(f"Element not found: {by}={value}")
            return None
    
    def find_elements(self, by: By, value: str, timeout: int = DEFAULT_WAIT_TIME) -> List[Any]:
        """Find elements on the page with wait support."""
        try:
            elements = self.wait.until(EC.presence_of_all_elements_located((by, value)))
            return elements
        except TimeoutException:
            logger.warning(f"Elements not found: {by}={value}")
            return []
    
    def click_element(self, by: By, value: str) -> bool:
        """Click on an element."""
        element = self.find_element(by, value)
        if element:
            try:
                element.click()
                logger.info(f"Clicked element: {by}={value}")
                return True
            except Exception as e:
                logger.error(f"Failed to click element {by}={value}: {str(e)}")
        return False
    
    def input_text(self, by: By, value: str, text: str) -> bool:
        """Input text into an element."""
        element = self.find_element(by, value)
        if element:
            try:
                element.clear()
                element.send_keys(text)
                logger.info(f"Input text '{text}' to element: {by}={value}")
                return True
            except Exception as e:
                logger.error(f"Failed to input text to element {by}={value}: {str(e)}")
        return False
    
    def wait_for_element(self, by: By, value: str, timeout: int = DEFAULT_WAIT_TIME) -> bool:
        """Wait for an element to be present."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return True
        except TimeoutException:
            logger.warning(f"Timed out waiting for element: {by}={value}")
            return False
    
    def extract_text(self, by: By, value: str) -> str:
        """Extract text from an element."""
        element = self.find_element(by, value)
        if element:
            return element.text
        return ""
    
    def get_current_url(self) -> str:
        """Get the current URL."""
        return self.driver.current_url
    
    def check_solana_explorer(self, address: str) -> Dict[str, Any]:
        """Check Solana Explorer for an address."""
        explorer_url = f"https://explorer.solana.com/address/{address}"
        self.navigate_to(explorer_url)
        
        # Wait for page to load
        time.sleep(3)  # Simple wait for content to load
        
        # Take screenshot for verification
        screenshot_path = self.screenshot(f"explorer_{address[:8]}")
        
        # Extract basic information
        try:
            # This is a simplified implementation - selectors may need adjustment
            balance_elem = self.find_element(By.CSS_SELECTOR, ".account-header-details-content")
            balance_text = balance_elem.text if balance_elem else "Balance not found"
            
            # Get transaction count if available
            txn_count_elem = self.find_element(By.CSS_SELECTOR, ".filter-dropdown-header h2")
            txn_count = txn_count_elem.text if txn_count_elem else "Unknown"
            
            return {
                "address": address,
                "explorer_url": explorer_url,
                "balance_text": balance_text,
                "transaction_count": txn_count,
                "screenshot": screenshot_path
            }
        except Exception as e:
            logger.error(f"Error extracting data from Solana Explorer: {str(e)}")
            return {
                "address": address,
                "explorer_url": explorer_url,
                "error": str(e),
                "screenshot": screenshot_path
            }
    
    def check_token_price(self, token_symbol: str) -> Dict[str, Any]:
        """Check token price on a price tracking website."""
        # Using Birdeye as an example
        url = f"https://birdeye.so/token/{token_symbol}?chain=solana"
        self.navigate_to(url)
        
        # Wait for price data to load
        time.sleep(5)  # Simple wait for content to load
        
        screenshot_path = self.screenshot(f"price_{token_symbol}")
        
        try:
            # This is a simplified implementation - selectors may need adjustment
            price_elem = self.find_element(By.CSS_SELECTOR, ".token-info-price")
            price_text = price_elem.text if price_elem else "Price not found"
            
            volume_elem = self.find_element(By.CSS_SELECTOR, ".token-info-volume")
            volume_text = volume_elem.text if volume_elem else "Volume not found"
            
            return {
                "token": token_symbol,
                "price": price_text,
                "volume": volume_text,
                "source_url": url,
                "screenshot": screenshot_path
            }
        except Exception as e:
            logger.error(f"Error extracting price data for {token_symbol}: {str(e)}")
            return {
                "token": token_symbol,
                "source_url": url,
                "error": str(e),
                "screenshot": screenshot_path
            }
    
    def run(self, instructions: str) -> Union[str, Dict[str, Any]]:
        """
        Run browser automation based on instructions.
        
        Args:
            instructions: String containing instructions for browser tasks
            
        Returns:
            Results of the browser automation tasks
        """
        logger.info(f"Running browser automation with instructions: {instructions}")
        
        # Parse instructions to determine task
        instructions_lower = instructions.lower()
        result = {}
        
        try:
            # Handle different types of instructions
            if "check address" in instructions_lower and any(addr in instructions for addr in ["address", "wallet"]):
                # Extract address - this is a simple implementation
                parts = instructions.split()
                for i, part in enumerate(parts):
                    if len(part) >= 32 and part.startswith(("1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "A", "B", "C", "D", "E", "F")):
                        result = self.check_solana_explorer(part)
                        break
            
            elif "token price" in instructions_lower or "price of" in instructions_lower:
                # Extract token symbol - this is a simple implementation
                words = instructions.split()
                for i, word in enumerate(words):
                    if word.lower() in ["token", "price", "of"] and i + 1 < len(words):
                        token_symbol = words[i + 1].strip(",.;:()\"'")
                        result = self.check_token_price(token_symbol)
                        break
            
            elif "go to" in instructions_lower or "navigate to" in instructions_lower or "visit" in instructions_lower:
                # Extract URL - this is a simple implementation
                words = instructions.split()
                for word in words:
                    if word.startswith("http") or ".com" in word or ".io" in word or ".org" in word:
                        url = word.strip(",.;:()\"'")
                        success = self.navigate_to(url)
                        screenshot_path = self.screenshot("navigation_result")
                        result = {
                            "success": success,
                            "url": url,
                            "current_url": self.get_current_url(),
                            "screenshot": screenshot_path
                        }
                        break
            
            else:
                # Generic browsing - take screenshot and return info
                result = {
                    "message": f"Completed browser task for: {instructions}",
                    "current_url": self.get_current_url() if self.driver else None,
                    "screenshot": self.screenshot("generic_result") if self.driver else None
                }
        
        except Exception as e:
            logger.error(f"Error during browser automation: {str(e)}")
            result = {
                "error": str(e),
                "instructions": instructions,
                "screenshot": self.screenshot("error_state") if self.driver else None
            }
        
        # Save results and return them
        self.task_results.append(result)
        return result