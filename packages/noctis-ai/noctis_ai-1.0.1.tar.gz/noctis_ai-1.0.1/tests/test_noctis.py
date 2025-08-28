from noctis.tools import run_tool

# Create agent
agent = run_tool("agent.create", {
    "name": "bind9_agent",
    "goal": "Gather info about BIND9 vulnerabilities",
    "tools": ["web.search", "web.fetch"]
})

# Run agent with a query
output = run_tool("agent.run", {"agent": agent, "query": "BIND9 DNS vulnerabilities"})

print(output)
