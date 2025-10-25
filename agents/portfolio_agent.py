# File: agents/portfolio_agent.py

from uagents import Agent, Context, Protocol
from uagents.setup import fund_agent_if_low
from datetime import datetime
from uuid import uuid4

from uagents_core.contrib.protocols.chat import (
   ChatAcknowledgement,
   ChatMessage,
   EndSessionContent,
   StartSessionContent,
   TextContent,
   chat_protocol_spec,
)

from models import (
    MarketDataRequest, MarketDataResponse, 
    StrategyRequest, StrategyResponse
)

# --- Configuration ---
MARKET_AGENT_ADDRESS = "agent1qfkkgvm6d2jg9wjhjausnl98shdxv28tr6deavwxx2ga3ah54c7ugzaw87t"
STRATEGY_AGENT_ADDRESS = "agent1qwjqcqaekr5l6tn8rujxk5jkkc0a9vvae255ptsty2gnru08hwggk3l9pqr"

agent = Agent(
    name="portfolio_agent",
    seed="portfolio_agent_secret_phrase",
)

fund_agent_if_low(agent.wallet.address())

chat_proto = Protocol(spec=chat_protocol_spec)

# --- Helper Functions ---

def format_knowledge_base(protocols: list) -> str:
    kb = ""
    for p in protocols:
        protocol_name = p['project'].replace('-', '_').replace(' ', '_')
        kb += f"(= (protocol.apy {protocol_name}) {p['apy']})\n"
        kb += f"(= (protocol.is_stable {protocol_name}) {'True' if p['stablecoin'] else 'False'})\n"
    return kb

def create_text_chat(text: str) -> ChatMessage:
    return ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=[TextContent(type="text", text=text)],
    )

# --- Main Chat Protocol Logic ---

@chat_proto.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    ctx.logger.info(f"Received chat message from {sender}")
    await ctx.send(sender, ChatAcknowledgement(timestamp=datetime.utcnow(), acknowledged_msg_id=msg.msg_id))

    for item in msg.content:
        if isinstance(item, StartSessionContent):
            ctx.logger.info(f"Session started with {sender}")
            response = create_text_chat("Hello! I am YieldWeaver, your DeFi optimization agent. Please state your risk profile ('conservative' or 'aggressive').")
            await ctx.send(sender, response)

        elif isinstance(item, TextContent):
            risk_profile = item.text.lower().strip()
            ctx.logger.info(f"Received risk profile: '{risk_profile}'")

            if risk_profile in ["conservative", "aggressive"]:
                ctx.storage.set("user_address", sender)
                ctx.storage.set("risk_profile", risk_profile)
                confirmation_msg = create_text_chat(f"Understood. Searching for the best '{risk_profile}' strategy. Please wait a moment...")
                await ctx.send(sender, confirmation_msg)
                await ctx.send(MARKET_AGENT_ADDRESS, MarketDataRequest())
            else:
                error_msg = create_text_chat("Sorry, that is not a valid risk profile. Please choose either 'conservative' or 'aggressive'.")
                await ctx.send(sender, error_msg)

# --- THIS IS THE MISSING HANDLER THAT FIXES THE ERROR ---
@chat_proto.on_message(ChatAcknowledgement)
async def handle_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handles acknowledgements for messages this agent has sent."""
    ctx.logger.info(f"Received acknowledgement from {sender} for message {msg.acknowledged_msg_id}")

# --- Internal Message Handlers (for communication with other agents) ---

@agent.on_message(model=MarketDataResponse)
async def handle_market_data(ctx: Context, _sender: str, msg: MarketDataResponse):
    ctx.logger.info("Received market data. Constructing knowledge base...")
    knowledge_base = format_knowledge_base(msg.protocols)
    risk_profile = ctx.storage.get("risk_profile")
    
    ctx.logger.info(f"Sending request to strategy agent for a '{risk_profile}' profile...")
    await ctx.send(STRATEGY_AGENT_ADDRESS, StrategyRequest(risk_profile=risk_profile, knowledge_base=knowledge_base))

@agent.on_message(model=StrategyResponse)
async def handle_strategy_response(ctx: Context, _sender: str, msg: StrategyResponse):
    ctx.logger.info("Received final strategy. Formatting response for user...")
    
    recommendation_text = (
        f"--- STRATEGY RECOMMENDATION ---\n"
        f"Profile: '{ctx.storage.get('risk_profile')}'\n"
        f"Protocol: {msg.protocol}\n"
        f"APY: {msg.apy}%\n"
        f"Rationale: {msg.rationale}"
    )
    
    final_response = create_text_chat(recommendation_text)
    user_address = ctx.storage.get("user_address")
    await ctx.send(user_address, final_response)

# --- Final Agent Setup ---
agent.include(chat_proto, publish_manifest=True)