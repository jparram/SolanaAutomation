from smolagents import CodeAgent, WebSearchTool, InferenceClientModel

# Initialize the model
model = InferenceClientModel()

# Create an agent with web search tool
agent = CodeAgent(tools=[WebSearchTool()], model=model)

# Run the agent with a query
agent.run("How many seconds would it take for a leopard at full speed to run through Pont des Arts?")