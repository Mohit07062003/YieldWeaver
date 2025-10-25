# File: agents/market_agent.py

import requests
from uagents import Agent, Context
from uagents.setup import fund_agent_if_low
from models import MarketDataRequest, MarketDataResponse

API_URL = "https://yields.llama.fi/pools"

agent = Agent(
    name="market_agent",
    seed="market_agent_secret_phrase",
)

fund_agent_if_low(agent.wallet.address())

def fetch_market_data():
    """Fetches and filters yield farming data from DeFiLlama."""
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        pools = response.json()['data']
        
        # Filter for high TVL and stablecoins, and extract needed data
        filtered_data = []
        for pool in pools:
            if pool['tvlUsd'] > 1000000: # TVL > $1M
                filtered_data.append({
                    'project': pool['project'],
                    'apy': pool['apy'],
                    'tvl': pool['tvlUsd'],
                    'stablecoin': pool['stablecoin'],
                })
        return filtered_data
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

@agent.on_message(model=MarketDataRequest)
async def handle_market_data_request(ctx: Context, sender: str, _msg: MarketDataRequest):
    ctx.logger.info(f"Received market data request from {sender}")
    protocols = fetch_market_data()
    ctx.logger.info(f"Found {len(protocols)} qualifying protocols.")
    await ctx.send(sender, MarketDataResponse(protocols=protocols))