# Example: Search Wikipedia
search_request = """
Please navigate to https://en.wikipedia.org/wiki/Chicago and give me a sentence containing the word "1992" that mentions a construction accident.
"""

agent_output = agent.run(search_request + helium_instructions)
print("Final output:")
print(agent_output)