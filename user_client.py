# File: user_client.py

from uagents import Agent, Context
from models import UserRequest, AgentResponse

# This is the address of the portfolio agent, which is correct
PORTFOLIO_AGENT_ADDRESS = "agent1q287dwsu2ng5zwfx9uxa7w3uc66dmh0p6zf0kccurlzdm00a2d86svg5zwf"

# --- AGENT DEFINITION ---
user_agent = Agent(
    name="user_agent",
    seed="user_secret_phrase",
    # Give the client its own unique local port to listen for replies. 8001 is fine.
    port=8001, 
    # === THIS IS THE ONLY LINE THAT MATTERS FOR THE FIX ===
    # It MUST point to your live Render service URL.
    mailbox="my_api_key@https://yieldweaver.onrender.com",
)

@user_agent.on_event("startup")
async def send_initial_request(ctx: Context):
    """Sends the initial request to the portfolio agent upon startup."""
    risk_profile = "aggressive"
    
    ctx.logger.info(f"Sending request to LIVE YieldWeaver agent for a '{risk_profile}' strategy...")
    await ctx.send(
        PORTFOLIO_AGENT_ADDRESS, 
        UserRequest(risk_profile=risk_profile)
    )

@user_agent.on_message(model=AgentResponse)
async def handle_agent_response(ctx: Context, sender: str, msg: AgentResponse):
    """Handles the final recommendation from the portfolio agent."""
    ctx.logger.info(f"Received final response from live agent {sender}:")
    
    print("\n--- LIVE AGENT STRATEGY RECOMMENDATION ---")
    print(f"  Recommendation: {msg.recommendation}")
    print(f"  APY: {msg.apy}%")
    print(f"  Reasoning: {msg.rationale}")
    print("------------------------------------------\n")
    
    ctx.stop()

if __name__ == "__main__":
    user_agent.run()