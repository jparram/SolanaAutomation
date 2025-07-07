import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_environment_variables():
    """Loads environment variables from .env file."""
    load_dotenv()
    logging.info("Attempting to load environment variables from .env file...")
    # Example: Accessing an environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        logging.info("OPENAI_API_KEY loaded successfully (partially hidden).")
    else:
        logging.warning("OPENAI_API_KEY not found. Ensure .env file is set up correctly.")
    # Add checks for other critical variables

class TradingAgent:
    """A simple class representing a trading agent."""
    def __init__(self, name, initial_capital, api_keys=None):
        self.name = name
        self.initial_capital = float(initial_capital)
        self.current_capital = float(initial_capital)
        self.api_keys = api_keys if api_keys else {}
        self.is_trading = False
        logging.info(f"Agent '{self.name}' initialized with capital: {self.initial_capital}")

    def start_trading(self):
        """Starts the trading activities for this agent."""
        if not self.is_trading:
            self.is_trading = True
            logging.info(f"Agent '{self.name}' has started trading.")
            # Placeholder for actual trading logic
            # e.g., connect to exchanges, monitor markets, execute trades
            print(f"Agent '{self.name}' is now active and trading.")
            self.monitor_market() # Example call
        else:
            logging.info(f"Agent '{self.name}' is already trading.")

    def stop_trading(self):
        """Stops the trading activities for this agent."""
        if self.is_trading:
            self.is_trading = False
            logging.info(f"Agent '{self.name}' has stopped trading.")
            # Placeholder for cleanup or closing positions
            print(f"Agent '{self.name}' has been deactivated.")
        else:
            logging.info(f"Agent '{self.name}' is not currently trading.")

    def monitor_market(self):
        """Placeholder for market monitoring logic."""
        if self.is_trading:
            # This would involve fetching market data, analyzing, etc.
            logging.info(f"Agent '{self.name}' is monitoring the market...")
            print(f"Agent '{self.name}' is monitoring market conditions...")
            # In a real scenario, this would be a continuous loop or scheduled task.

    def get_status(self):
        """Returns the current status of the agent."""
        return {
            "name": self.name,
            "initial_capital": self.initial_capital,
            "current_capital": self.current_capital,
            "is_trading": self.is_trading,
            "api_keys_loaded": {key: val is not None for key, val in self.api_keys.items()}
        }

def create_user_agent():
    """Guides the user to create their first trading agent."""
    logging.info("Starting the process to create a new user agent.")
    print("\\n--- Create Your First Trading Agent ---")
    
    agent_name = os.getenv("DEFAULT_AGENT_NAME", "MyTradingAgent")
    custom_name = input(f"Enter a name for your agent (default: {agent_name}): ")
    if custom_name:
        agent_name = custom_name

    initial_capital_default = os.getenv("INITIAL_TRADING_CAPITAL", "1000")
    initial_capital_str = input(f"Enter initial trading capital (default: {initial_capital_default}): ")
    initial_capital = float(initial_capital_str if initial_capital_str else initial_capital_default)

    # Load necessary API keys from environment
    api_keys = {
        "openai": os.getenv("OPENAI_API_KEY"),
        "solana_rpc": os.getenv("SOLANA_RPC_URL"),
        "birdeye": os.getenv("BIRDEYE_API_KEY")
    }
    
    # Basic validation for API keys
    if not all(api_keys.values()):
        logging.warning("One or more API keys are missing in the .env file.")
        print("Warning: Some API keys are missing. Please check your .env file.")
        # Decide if agent creation should proceed or halt
        # For now, let's allow it but with a warning.

    agent = TradingAgent(name=agent_name, initial_capital=initial_capital, api_keys=api_keys)
    logging.info(f"Agent '{agent.name}' created successfully.")
    print(f"Agent '{agent.name}' created with ${agent.initial_capital} capital.")
    return agent

def main_menu(agent):
    """Displays the main menu and handles user input."""
    if not agent:
        logging.error("No agent available for the main menu.")
        print("Error: Agent not created. Exiting.")
        return

    while True:
        print("\\n--- Main Menu ---")
        print(f"Agent: {agent.name} | Status: {'Trading' if agent.is_trading else 'Idle'}")
        print("1. Start Trading")
        print("2. Stop Trading")
        print("3. View Agent Status")
        print("4. Exit")
        
        choice = input("Select an option: ")
        
        if choice == '1':
            agent.start_trading()
        elif choice == '2':
            agent.stop_trading()
        elif choice == '3':
            status = agent.get_status()
            print("\\n--- Agent Status ---")
            for key, value in status.items():
                print(f"{key.replace('_', ' ').title()}: {value}")
        elif choice == '4':
            logging.info("User chose to exit.")
            print("Exiting application.")
            if agent.is_trading:
                agent.stop_trading() # Ensure trading stops on exit
            break
        else:
            logging.warning(f"Invalid menu choice: {choice}")
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    logging.info("Application starting...")
    print("Welcome to the Solana Trading Agent Platform!")

    load_environment_variables()
    
    # Check if a .env file exists, if not, guide user
    if not os.path.exists(".env"):
        logging.warning(".env file not found.")
        print("\\nIMPORTANT: '.env' file not found.")
        print("Please create a '.env' file by copying '.env.example' and filling in your details.")
        print("Example: cp .env.example .env")
        print("Then, edit the .env file with your actual API keys and configurations.")
        # Optionally, exit if .env is critical for first run
        # For now, we'll proceed to agent creation, which will also warn about missing keys.

    current_agent = create_user_agent()
    
    if current_agent:
        main_menu(current_agent)
    else:
        logging.error("Failed to create an agent. Application cannot proceed.")
        print("Could not initialize a trading agent. Please check logs and configuration.")

    logging.info("Application finished.")
