# File: main.py
import os
from uagents import Bureau
from agents.portfolio_agent import agent as portfolio_agent
from agents.market_agent import agent as market_agent
from agents.strategy_agent import agent as strategy_agent

if __name__ == "__main__":
    # === THIS IS THE CHANGE ===
    # The Bureau now runs on a FIXED INTERNAL port.
    internal_port = 8001
    
    # It still advertises its public URL, which is correct.
    endpoint = os.environ.get("RENDER_EXTERNAL_URL", f"http://127.0.0.1:{internal_port}")

    bureau = Bureau(endpoint=endpoint, port=internal_port)

    print(f"Bureau is running on INTERNAL port {internal_port} and advertising endpoint {endpoint}")

    bureau.add(portfolio_agent)
    bureau.add(market_agent)
    bureau.add(strategy_agent)
    bureau.run()