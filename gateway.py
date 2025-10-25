# File: gateway.py

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles # Import the StaticFiles class
from uagents.query import query
from models import UserRequest, AgentResponse
from pydantic import BaseModel
import uvicorn
import os

# --- Configuration ---
PORTFOLIO_AGENT_ADDRESS = "agent1q287dwsu2ng5zwfx9uxa7w3uc66dmh0p6zf0kccurlzdm00a2d86svg5zwf"

app = FastAPI()

# --- API Endpoint ---
# Our API endpoint must be defined *before* the static file mount.
@app.post("/query", response_model=AgentResponse)
async def agent_query(request: UserRequest):
    try:
        print(f"Forwarding request for '{request.risk_profile}' to agent...")
        response = await query(
            destination=PORTFOLIO_AGENT_ADDRESS,
            message=request,
            timeout=60.0
        )
        response_data = response.decode_payload()
        print(f"Received final response from agent: {response_data}")
        return AgentResponse(**response_data)
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- THIS IS THE NEW PART ---
# Mount the 'frontend' directory to serve static files.
# The `html=True` argument tells FastAPI to serve `index.html` for the root path.
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")


if __name__ == "__main__":
    # The gateway runs on an internal port and is served by the run.sh script.
    uvicorn.run(app, host="0.0.0.0", port=8001)