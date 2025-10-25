# File: gateway.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uagents.query import query
from pydantic import BaseModel
import uvicorn
import os

# Configuration - This must match the agent running on the same server
PORTFOLIO_AGENT_ADDRESS = "agent1q287dwsu2ng5zwfx9uxa7w3uc66dmh0p6zf0kccurlzdm00a2d86svg5zwf"
AGENT_BUREAU_URL = "http://127.0.0.1:8000" # The gateway talks to the bureau locally

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    risk_profile: str

@app.post("/query")
async def run_query(request: QueryRequest):
    try:
        # We don't have a direct query model, so we simulate a chat interaction
        # This is a placeholder for a more robust query/response flow
        # For the hackathon, this demonstrates the frontend connectivity
        print(f"Received query for profile: {request.risk_profile}")
        return {"status": "success", "message": f"Request for '{request.risk_profile}' profile sent to agent network. Please check agent logs."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)