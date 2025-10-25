# File: main.py
import os
from uagents import Bureau
from agents.portfolio_agent import agent as portfolio_agent
from agents.market_agent import agent as market_agent
from agents.strategy_agent import agent as strategy_agent

if __name__ == "__main__":
    # Get the port from the environment variable provided by Render
    port = int(os.environ.get("PORT", 8000))

    # Get the public URL from the environment variable provided by Render
    # This is the crucial fix.
    endpoint = os.environ.get("RENDER_EXTERNAL_URL", f"http://127.0.0.1:{port}")

    # Create a Bureau that binds to the internal port but advertises its public endpoint
    bureau = Bureau(endpoint=endpoint, port=port)

    print(f"Bureau is running on port {port} and advertising endpoint {endpoint}")

    # Add agents (no changes here)
    bureau.add(portfolio_agent)
    bureau.add(market_agent)
    bureau.add(strategy_agent)

    # Run the Bureau
    bureau.run()