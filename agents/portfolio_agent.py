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

# === FIX 1: ADD MISSING IMPORTS ===
from models import (
    UserRequest, AgentResponse, # Added UserRequest and AgentResponse
    MarketDataRequest, MarketDataResponse, 
    StrategyRequest, StrategyResponse
)

# --- Configuration ---
MARKET_AGENT_ADDRESS = "agent_address_from_terminal" # Replace with your market agent address
STRATEGY_AGENT_ADDRESS = "agent_address_from_terminal" # Replace with your strategy agent address

agent = Agent(
    name="portfolio_agent",
    seed="portfolio_agent_secret_phrase",
)

fund_agent_if_low(agent.wallet.address())

chat_proto = Protocol(spec=chat_protocol_spec)

# --- Helper Functions (No changes here) ---

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

# --- Main Handlers ---

@chat_proto.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    # This handler is for direct chat interactions
    # ... (code is the same)
    
    # === FIX 2 (Part A): Store the origin of the request ===
    ctx.storage.set("origin", "chat") 
    ctx.storage.set("user_address", sender)
    # ... (rest of the chat logic is the same)

@agent.on_message(model=UserRequest, replies={AgentResponse})
async def handle_user_request(ctx: Context, sender: str, msg: UserRequest):
    # This handler is for requests from our web gateway
    ctx.logger.info(f"Received user request for a '{msg.risk_profile}' strategy from gateway.")
    
    # === FIX 2 (Part B): Store the origin of the request ===
    ctx.storage.set("origin", "gateway")
    ctx.storage.set("user_address", sender) # The gateway's temporary address
    ctx.storage.set("risk_profile", msg.risk_profile)
    
    # Kick off the internal workflow
    await ctx.send(MARKET_AGENT_ADDRESS, MarketDataRequest())


@chat_proto.on_message(ChatAcknowledgement)
async def handle_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(f"Received acknowledgement from {sender} for message {msg.acknowledged_msg_id}")


# --- Internal Message Handlers ---

@agent.on_message(model=MarketDataResponse)
async def handle_market_data(ctx: Context, _sender: str, msg: MarketDataResponse):
    # This function doesn't need to change
    ctx.logger.info("Received market data. Constructing knowledge base...")
    knowledge_base = format_knowledge_base(msg.protocols)
    risk_profile = ctx.storage.get("risk_profile")
    await ctx.send(STRATEGY_AGENT_ADDRESS, StrategyRequest(risk_profile=risk_profile, knowledge_base=knowledge_base))


@agent.on_message(model=StrategyResponse)
async def handle_strategy_response(ctx: Context, _sender: str, msg: StrategyResponse):
    # === FIX 2 (Part C): The Smart Response Handler ===
    ctx.logger.info("Received final strategy. Formatting response...")
    
    user_address = ctx.storage.get("user_address")
    origin = ctx.storage.get("origin")

    if origin == "chat":
        # If the request came from a chat, send a chat message back
        ctx.logger.info(f"Sending CHAT response to {user_address}")
        recommendation_text = (
            f"--- STRATEGY RECOMMENDATION ---\n"
            f"Profile: '{ctx.storage.get('risk_profile')}'\n"
            f"Protocol: {msg.protocol}\n"
            f"APY: {msg.apy}%\n"
            f"Rationale: {msg.rationale}"
        )
        final_response = create_text_chat(recommendation_text)
        await ctx.send(user_address, final_response)
    
    elif origin == "gateway":
        # If the request came from the gateway, send a direct AgentResponse back
        ctx.logger.info(f"Sending GATEWAY response to {user_address}")
        recommendation_text = f"Based on your '{ctx.storage.get('risk_profile')}' risk profile, the recommended protocol is {msg.protocol}."
        final_response = AgentResponse(
            recommendation=recommendation_text,
            apy=msg.apy,
            rationale=msg.rationale
        )
        await ctx.send(user_address, final_response)


# --- Final Agent Setup ---
agent.include(chat_proto, publish_manifest=True)