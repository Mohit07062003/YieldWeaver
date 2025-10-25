# File: agents/strategy_agent.py

from hyperon import MeTTa
from uagents import Agent, Context
from uagents.setup import fund_agent_if_low
from models import StrategyRequest, StrategyResponse

agent = Agent(
    name="strategy_agent",
    seed="strategy_agent_secret_phrase",
)

fund_agent_if_low(agent.wallet.address())

# Your reasoning rules file should be in knowledge_base/defi_rules.metta
with open("knowledge_base/defi_rules.metta", "r") as f:
    METTA_RULES = f.read()

def run_metta_logic(kb: str, risk_profile: str) -> dict:
    """Runs the MeTTa engine to get the best strategy."""
    metta = MeTTa()
    # Load rules and dynamic knowledge base
    metta.run(METTA_RULES)
    metta.run(kb)
    
    # Execute the query based on risk profile
    query = f"!(get-best-strategy {risk_profile})"
    result = metta.run(query)
    
    # Process the result
    if result and result[0]:
        # Assuming the result format is [(protocol_name, apy_value)]
        best_protocol, apy = result[0]
        return {
            'protocol': str(best_protocol),
            'apy': float(apy),
            'rationale': f'Selected as the best option for a "{risk_profile}" profile based on reasoning rules.'
        }
    return {}

@agent.on_message(model=StrategyRequest)
async def handle_strategy_request(ctx: Context, sender: str, msg: StrategyRequest):
    ctx.logger.info(f"Received strategy request for profile: {msg.risk_profile}")
    
    strategy = run_metta_logic(msg.knowledge_base, msg.risk_profile)
    
    if strategy:
        ctx.logger.info(f"Strategy found: {strategy['protocol']} with APY {strategy['apy']}%")
        await ctx.send(sender, StrategyResponse(
            protocol=strategy['protocol'],
            apy=strategy['apy'],
            rationale=strategy['rationale']
        ))
    else:
        ctx.logger.error("Could not determine a strategy.")