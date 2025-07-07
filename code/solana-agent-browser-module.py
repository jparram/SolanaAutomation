import os
from io import BytesIO
from time import sleep
from typing import Optional, List, Dict, Any, Union

# Browser automation imports
import helium
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# SmolAgents imports
from smolagents import CodeAgent, tool
from smolagents.agents import ActionStep
from smolagents import InferenceClientModel, LiteLLMModel

class SolanaWebBrowser:
    """
    A browser automation class built on SmolAgents for Solana and crypto-specific tasks.
    """
    
    def __init__(self, 
                headless: bool = False, 
                model_id: str = "meta-llama/Llama-3.3-70B-Instruct",
                api_key: Optional[str] = None):
        """
        Initialize the Solana Web Browser.
        
        Args:
            headless: Whether to run the browser in headless mode.
            model_id: ID of the model to use for the agent.
            api_key: API key for the model provider (if needed).
        """
        self.headless = headless
        self.model_id = model_id
        self.api_key = api_key
        
        # Initialize browser
        self.driver = self._init_browser()
        
        # Set up agent
        self.agent = self._init_agent()
    
    def _init_browser(self) -> webdriver.Chrome:
        """
        Initialize the Chrome browser with appropriate settings.
        
        Returns:
            webdriver.Chrome: Initialized Chrome driver.
        """
        # Configure Chrome options
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--force-device-scale-factor=1")
        chrome_options.add_argument("--window-size=1200,800")
        chrome_options.add_argument("--disable-pdf-viewer")
        chrome_options.add_argument("--window-position=0,0")
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        # Initialize the browser
        driver = helium.start_chrome(headless=self.headless, options=chrome_options)
        return driver
    
    def _save_screenshot(self, memory_step: ActionStep, agent: CodeAgent) -> None:
        """
        Capture and save a screenshot from the browser.
        
        Args:
            memory_step: Current memory step to attach the screenshot to.
            agent: The CodeAgent instance.
        """
        sleep(1.0)  # Let JavaScript animations happen before taking screenshot
        driver = helium.get_driver()
        current_step = memory_step.step_number
        
        if driver is not None:
            # Remove previous screenshots for lean processing
            for previous_memory_step in agent.memory.steps:
                if isinstance(previous_memory_step, ActionStep) and previous_memory_step.step_number <= current_step - 2:
                    previous_memory_step.observations_images = None
            
            # Capture screenshot
            png_bytes = driver.get_screenshot_as_png()
            image = Image.open(BytesIO(png_bytes))
            print(f"Captured a browser screenshot: {image.size} pixels")
            memory_step.observations_images = [image.copy()]
            
            # Update observations with current URL
            url_info = f"Current URL: {driver.current_url}"
            memory_step.observations = (
                url_info if memory_step.observations is None 
                else memory_step.observations + "\n" + url_info
            )
    
    def _init_agent(self) -> CodeAgent:
        """
        Initialize the CodeAgent with browser tools.
        
        Returns:
            CodeAgent: Configured agent with tools.
        """
        # Set up model
        if "anthropic" in self.model_id.lower() or "claude" in self.model_id.lower():
            model = LiteLLMModel(
                model_id=self.model_id,
                api_key=self.api_key or os.environ.get("ANTHROPIC_API_KEY")
            )
        elif "gpt" in self.model_id.lower() or "openai" in self.model_id.lower():
            model = LiteLLMModel(
                model_id=self.model_id,
                api_key=self.api_key or os.environ.get("OPENAI_API_KEY")
            )
        else:
            model = InferenceClientModel(model_id=self.model_id)
        
        # Define browser tools
        @tool
        def search_for_text(text: str, nth_result: int = 1) -> str:
            """
            Searches for text on the current page and jumps to the nth occurrence.
            
            Args:
                text: The text to search for.
                nth_result: Which occurrence to jump to (default: 1).
                
            Returns:
                str: Result of the search operation.
            """
            elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
            if nth_result > len(elements):
                raise Exception(f"Match #{nth_result} not found (only {len(elements)} matches found)")
            
            result = f"Found {len(elements)} matches for '{text}'."
            elem = elements[nth_result - 1]
            self.driver.execute_script("arguments[0].scrollIntoView(true);", elem)
            result += f" Focused on element {nth_result} of {len(elements)}"
            return result
        
        @tool
        def go_back() -> None:
            """Goes back to the previous page."""
            self.driver.back()
            return "Navigated back to previous page."
        
        @tool
        def close_popups() -> str:
            """
            Closes any visible modal or pop-up on the page.
            """
            webdriver.ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            return "Attempted to close any popups by pressing ESC key."
        
        @tool
        def extract_token_info() -> Dict[str, Any]:
            """
            Extract token information from popular Solana token explorers like Solscan or Birdeye.
            
            Returns:
                Dict[str, Any]: Extracted token information.
            """
            current_url = self.driver.current_url
            token_info = {"success": False, "data": {}}
            
            try:
                if "solscan.io" in current_url:
                    # Extract from Solscan
                    token_info["source"] = "Solscan"
                    
                    # Token name and symbol
                    try:
                        name_element = self.driver.find_element(By.CSS_SELECTOR, "div.token-name")
                        if name_element:
                            token_info["data"]["name"] = name_element.text
                    except:
                        pass
                    
                    # Token price
                    try:
                        price_element = self.driver.find_element(By.CSS_SELECTOR, "div.token-price-usd")
                        if price_element:
                            token_info["data"]["price"] = price_element.text
                    except:
                        pass
                    
                    # Market cap
                    try:
                        market_cap_element = self.driver.find_element(By.XPATH, "//div[contains(text(), 'Market Cap')]/following-sibling::div")
                        if market_cap_element:
                            token_info["data"]["market_cap"] = market_cap_element.text
                    except:
                        pass
                    
                elif "birdeye.so" in current_url:
                    # Extract from Birdeye
                    token_info["source"] = "Birdeye"
                    
                    # Token name and symbol
                    try:
                        name_element = self.driver.find_element(By.CSS_SELECTOR, "div.token-name-container")
                        if name_element:
                            token_info["data"]["name"] = name_element.text
                    except:
                        pass
                    
                    # Token price
                    try:
                        price_element = self.driver.find_element(By.CSS_SELECTOR, "div.token-price")
                        if price_element:
                            token_info["data"]["price"] = price_element.text
                    except:
                        pass
                    
                    # Market cap
                    try:
                        market_cap_element = self.driver.find_element(By.XPATH, "//div[contains(text(), 'Market Cap')]/following-sibling::div")
                        if market_cap_element:
                            token_info["data"]["market_cap"] = market_cap_element.text
                    except:
                        pass
                    
                elif "magiceden.io" in current_url:
                    # Extract from Magic Eden
                    token_info["source"] = "Magic Eden"
                    
                    # Collection name
                    try:
                        name_element = self.driver.find_element(By.CSS_SELECTOR, "h1.collection-name")
                        if name_element:
                            token_info["data"]["collection_name"] = name_element.text
                    except:
                        pass
                    
                    # Floor price
                    try:
                        price_element = self.driver.find_element(By.XPATH, "//div[contains(text(), 'Floor')]/following-sibling::div")
                        if price_element:
                            token_info["data"]["floor_price"] = price_element.text
                    except:
                        pass
                    
                    # Total volume
                    try:
                        volume_element = self.driver.find_element(By.XPATH, "//div[contains(text(), 'Total Volume')]/following-sibling::div")
                        if volume_element:
                            token_info["data"]["total_volume"] = volume_element.text
                    except:
                        pass
                    
                token_info["success"] = len(token_info["data"]) > 0
                
                # If no data was found, try a generic approach
                if not token_info["success"]:
                    # Extract any price-like information
                    price_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '$') or contains(text(), 'USD')]")
                    if price_elements:
                        token_info["data"]["possible_prices"] = [elem.text for elem in price_elements[:5]]
                        token_info["success"] = True
                
                return token_info
            
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "url": current_url
                }
        
        @tool
        def extract_nft_info() -> Dict[str, Any]:
            """
            Extract NFT information from popular marketplaces like Magic Eden, Tensor, etc.
            
            Returns:
                Dict[str, Any]: Extracted NFT information.
            """
            current_url = self.driver.current_url
            nft_info = {"success": False, "data": {}}
            
            try:
                if "magiceden.io" in current_url:
                    # Extract from Magic Eden
                    nft_info["source"] = "Magic Eden"
                    
                    # NFT name
                    try:
                        name_element = self.driver.find_element(By.CSS_SELECTOR, "h1.nft-title")
                        if name_element:
                            nft_info["data"]["name"] = name_element.text
                    except:
                        pass
                    
                    # NFT price
                    try:
                        price_element = self.driver.find_element(By.CSS_SELECTOR, "div.price-container")
                        if price_element:
                            nft_info["data"]["price"] = price_element.text
                    except:
                        pass
                    
                    # NFT collection
                    try:
                        collection_element = self.driver.find_element(By.CSS_SELECTOR, "a.collection-link")
                        if collection_element:
                            nft_info["data"]["collection"] = collection_element.text
                    except:
                        pass
                    
                elif "tensor.trade" in current_url:
                    # Extract from Tensor
                    nft_info["source"] = "Tensor"
                    
                    # NFT name
                    try:
                        name_element = self.driver.find_element(By.CSS_SELECTOR, "h1.nft-name")
                        if name_element:
                            nft_info["data"]["name"] = name_element.text
                    except:
                        pass
                    
                    # NFT price
                    try:
                        price_element = self.driver.find_element(By.CSS_SELECTOR, "div.nft-price")
                        if price_element:
                            nft_info["data"]["price"] = price_element.text
                    except:
                        pass
                    
                    # NFT collection
                    try:
                        collection_element = self.driver.find_element(By.CSS_SELECTOR, "a.collection-name")
                        if collection_element:
                            nft_info["data"]["collection"] = collection_element.text
                    except:
                        pass
                
                nft_info["success"] = len(nft_info["data"]) > 0
                
                # If no data was found, try a generic approach
                if not nft_info["success"]:
                    # Extract any image that might be the NFT
                    img_elements = self.driver.find_elements(By.TAG_NAME, "img")
                    if img_elements:
                        nft_info["data"]["possible_nft_images"] = [img.get_attribute("src") for img in img_elements[:3]]
                        nft_info["success"] = True
                
                return nft_info
            
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "url": current_url
                }
        
        @tool
        def inspect_metaplex_docs() -> Dict[str, Any]:
            """
            Extract information from Metaplex documentation when browsing the docs.
            
            Returns:
                Dict[str, Any]: Extracted documentation information.
            """
            current_url = self.driver.current_url
            docs_info = {"success": False, "data": {}}
            
            try:
                if "docs.metaplex.com" in current_url or "metaplex.com/docs" in current_url:
                    docs_info["source"] = "Metaplex Docs"
                    
                    # Extract title
                    try:
                        title_element = self.driver.find_element(By.CSS_SELECTOR, "h1")
                        if title_element:
                            docs_info["data"]["title"] = title_element.text
                    except:
                        pass
                    
                    # Extract code samples
                    try:
                        code_elements = self.driver.find_elements(By.CSS_SELECTOR, "pre code")
                        if code_elements:
                            docs_info["data"]["code_samples"] = [elem.text for elem in code_elements]
                    except:
                        pass
                    
                    # Extract main content
                    try:
                        content_elements = self.driver.find_elements(By.CSS_SELECTOR, "article p, article li")
                        if content_elements:
                            docs_info["data"]["content"] = "\n".join([elem.text for elem in content_elements[:10]])
                    except:
                        pass
                    
                    docs_info["success"] = len(docs_info["data"]) > 0
                
                return docs_info
            
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "url": current_url
                }
        
        # Create the agent with tools
        agent = CodeAgent(
            tools=[
                search_for_text,
                go_back,
                close_popups,
                extract_token_info,
                extract_nft_info,
                inspect_metaplex_docs
            ],
            model=model,
            additional_authorized_imports=["helium"],
            step_callbacks=[self._save_screenshot],
            max_steps=20,
            verbosity_level=1,
        )
        
        # Import helium for the agent to use
        agent.python_executor("from helium import *", agent.state)
        
        return agent
    
    def run(self, instructions: str) -> str:
        """
        Run browser automation with the given instructions.
        
        Args:
            instructions: Instructions for the browser automation.
            
        Returns:
            str: Result of the browser automation.
        """
        # Add Helium usage instructions
        helium_instructions = """
        You can use helium to access websites. The helium driver is already managed.
        We've already run "from helium import *".
        
        Here are some examples of how to use helium:
        
        To navigate to a website:
        ```py
        go_to('https://solscan.io')
        ```
        
        To click on elements with specific text:
        ```py
        click("Tokens")
        ```
        
        To click on a link:
        ```py
        click(Link("Solana"))
        ```
        
        To search within a page:
        ```py
        search_for_text("SOL", 1)  # Find first occurrence of "SOL"
        ```
        
        To scroll:
        ```py
        scroll_down(num_pixels=800)  # Scroll down 800 pixels
        scroll_up(num_pixels=400)    # Scroll up 400 pixels
        ```
        
        To close popups:
        ```py
        close_popups()  # Presses ESC key to close popups
        ```
        
        If you're on a token explorer page, you can extract token information:
        ```py
        token_info = extract_token_info()
        print(f"Token price: {token_info['data'].get('price', 'Unknown')}")
        ```
        
        If you're on an NFT marketplace, you can extract NFT information:
        ```py
        nft_info = extract_nft_info()
        print(f"NFT name: {nft_info['data'].get('name', 'Unknown')}")
        ```
        
        If you're on Metaplex documentation, you can extract documentation info:
        ```py
        docs_info = inspect_metaplex_docs()
        print(f"Documentation title: {docs_info['data'].get('title', 'Unknown')}")
        ```
        
        Remember to check if an element exists before clicking on it:
        ```py
        if Text('Accept cookies').exists():
            click('Accept')
        ```
        """
        
        full_instructions = f"{instructions}\n\n{helium_instructions}"
        return self.agent.run(full_instructions)
    
    def close(self):
        """Close the browser."""
        helium.kill_browser()


class SolanaDeveloperBrowser(SolanaWebBrowser):
    """
    Extended browser automation for Solana developers, with tools for code extraction,
    documentation parsing, and developer resources.
    """
    
    def __init__(self, 
                headless: bool = False,
                model_id: str = "meta-llama/Llama-3.3-70B-Instruct",
                api_key: Optional[str] = None):
        """Initialize the Solana Developer Browser."""
        super().__init__(headless, model_id, api_key)
        
        # Add additional developer tools
        self._add_developer_tools()
    
    def _add_developer_tools(self):
        """Add developer-specific tools to the agent."""
        
        @tool
        def extract_code_sample() -> Dict[str, Any]:
            """
            Extract code samples from the current page.
            
            Returns:
                Dict[str, Any]: Extracted code samples.
            """
            result = {"success": False, "samples": []}
            
            try:
                # Try different code block selectors used by various documentation sites
                selectors = [
                    "pre code",
                    ".code-block",
                    ".code-sample",
                    ".highlight",
                    ".syntax-highlighter",
                    ".language-javascript",
                    ".language-typescript",
                    ".language-rust",
                    ".language-python"
                ]
                
                for selector in selectors:
                    code_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if code_elements:
                        for i, elem in enumerate(code_elements):
                            code_text = elem.text.strip()
                            if code_text:
                                # Try to determine the language
                                language = "unknown"
                                classes = elem.get_attribute("class") or ""
                                
                                if "javascript" in classes or "js" in classes:
                                    language = "javascript"
                                elif "typescript" in classes or "ts" in classes:
                                    language = "typescript"
                                elif "rust" in classes:
                                    language = "rust"
                                elif "python" in classes or "py" in classes:
                                    language = "python"
                                
                                # Add to result
                                result["samples"].append({
                                    "code": code_text,
                                    "language": language,
                                    "index": i
                                })
                
                result["success"] = len(result["samples"]) > 0
                return result
            
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }
        
        @tool
        def analyze_solana_api_docs() -> Dict[str, Any]:
            """
            Analyze Solana API documentation when on the Solana docs site.
            
            Returns:
                Dict[str, Any]: Extracted API documentation.
            """
            current_url = self.driver.current_url
            api_info = {"success": False, "data": {}}
            
            try:
                if "docs.solana.com" in current_url or "solana.com/docs" in current_url:
                    api_info["source"] = "Solana Docs"
                    
                    # Extract title
                    try:
                        title_element = self.driver.find_element(By.CSS_SELECTOR, "h1")
                        if title_element:
                            api_info["data"]["title"] = title_element.text
                    except:
                        pass
                    
                    # Extract code samples
                    try:
                        code_elements = self.driver.find_elements(By.CSS_SELECTOR, "pre code")
                        if code_elements:
                            api_info["data"]["code_samples"] = [elem.text for elem in code_elements]
                    except:
                        pass
                    
                    # Extract API method signatures
                    try:
                        method_elements = self.driver.find_elements(By.CSS_SELECTOR, ".method-signature, .function-signature")
                        if method_elements:
                            api_info["data"]["methods"] = [elem.text for elem in method_elements]
                    except:
                        pass
                    
                    # Extract parameter tables
                    try:
                        param_elements = self.driver.find_elements(By.CSS_SELECTOR, "table")
                        if param_elements:
                            tables = []
                            for table in param_elements:
                                rows = table.find_elements(By.TAG_NAME, "tr")
                                table_data = []
                                for row in rows:
                                    cells = row.find_elements(By.TAG_NAME, "td")
                                    if cells:
                                        row_data = [cell.text for cell in cells]
                                        table_data.append(row_data)
                                if table_data:
                                    tables.append(table_data)
                            if tables:
                                api_info["data"]["parameter_tables"] = tables
                    except:
                        pass
                    
                    api_info["success"] = len(api_info["data"]) > 0
                
                return api_info
            
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "url": current_url
                }
        
        # Add the tools to the agent
        self.agent = CodeAgent(
            tools=self.agent.tools + [extract_code_sample, analyze_solana_api_docs],
            model=self.agent.model,
            additional_authorized_imports=["helium"],
            step_callbacks=[self._save_screenshot],
            max_steps=20,
            verbosity_level=1,
        )
        
        # Re-import helium for the agent
        self.agent.python_executor("from helium import *", self.agent.state)
    
    def save_code_to_file(self, code: str, filename: str, directory: str = "./extracted_code") -> str:
        """
        Save extracted code to a file.
        
        Args:
            code: The code to save.
            filename: The name of the file.
            directory: The directory to save the file in.
            
        Returns:
            str: Path to the saved file.
        """
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(directory, filename)
        with open(file_path, "w") as f:
            f.write(code)
        
        return file_path


# Example usage:
if __name__ == "__main__":
    # Regular Solana browser for general tasks
    browser = SolanaWebBrowser(headless=False)
    result = browser.run("Go to solscan.io and find information about the SOL token")
    print(result)
    browser.close()
    
    # Developer browser for code extraction
    dev_browser = SolanaDeveloperBrowser(headless=False)
    result = dev_browser.run("Go to docs.metaplex.com and extract code samples for creating an NFT")
    print(result)
    
    # Extract and save code samples
    code_samples = dev_browser.agent.python_executor("extract_code_sample()", dev_browser.agent.state)
    if code_samples.get("success", False) and code_samples.get("samples"):
        for i, sample in enumerate(code_samples["samples"]):
            filename = f"metaplex_sample_{i}.{sample['language']}"
            file_path = dev_browser.save_code_to_file(sample["code"], filename)
            print(f"Saved code sample to {file_path}")
    
    dev_browser.close()
