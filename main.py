import os # Import the os library at the top
from uagents import Bureau
from agents.portfolio_agent import agent as portfolio_agent
from agents.market_agent import agent as market_agent
from agents.strategy_agent import agent as strategy_agent

if __name__ == "__main__":
    # Get the port from the environment variable provided by Render, defaulting to 8000
    port = int(os.environ.get("PORT", 8000))

    # Create a Bureau and specify its endpoint using the dynamic port
    bureau = Bureau(endpoint=f"http://0.0.0.0:{port}", port=port)

    # Add all three agents to the Bureau (no changes here)
    print(f"Adding portfolio agent to bureau: {portfolio_agent.address}")
    bureau.add(portfolio_agent)

    print(f"Adding market agent to bureau: {market_agent.address}")
    bureau.add(market_agent)

    print(f"Adding strategy agent to bureau: {strategy_agent.address}")
    bureau.add(strategy_agent)

    # Run the Bureau (no changes here)
    print(f"Starting bureau with 3 agents on port {port}...")
    bureau.run()