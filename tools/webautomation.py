from smolagents import InferenceClientModel

# Initialize the model (choose your preferred model)
model_id = "meta-llama/Llama-3.3-70B-Instruct"  # Can be changed to your preferred model
model = InferenceClientModel(model_id=model_id)

# Create the agent
agent = CodeAgent(
    tools=[go_back, close_popups, search_item_ctrl_f],
    model=model,
    additional_authorized_imports=["helium"],
    step_callbacks=[save_screenshot],
    max_steps=20,
    verbosity_level=2,
)

# Import helium for the agent
agent.python_executor("from helium import *", agent.state)