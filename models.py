# File: models.py

from uagents import Model
from typing import List, Dict, Any

# Model for the user to send a request to the portfolio agent
class UserRequest(Model):
    risk_profile: str  # e.g., "conservative", "aggressive"

# Model for the portfolio agent to request data from the market agent
class MarketDataRequest(Model):
    pass  # This message doesn't need to carry any data, it's just a trigger

# Model for the market agent to send data back to the portfolio agent
class MarketDataResponse(Model):
    protocols: List[Dict[str, Any]] # A list of dictionaries, each representing a protocol

# Model for the portfolio agent to request a strategy from the strategy agent
class StrategyRequest(Model):
    risk_profile: str
    knowledge_base: str # The dynamically generated MeTTa knowledge base as a string

# Model for the strategy agent to send its decision back
class StrategyResponse(Model):
    protocol: str
    apy: float
    rationale: str

# Final model for the portfolio agent to respond to the user
class AgentResponse(Model):
    recommendation: str
    apy: float
    rationale: str