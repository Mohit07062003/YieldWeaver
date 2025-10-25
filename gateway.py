from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
import requests # Use the standard requests library
from models import UserRequest
from pydantic import BaseModel
import uvicorn
import os

PORTFOLIO_AGENT_ADDRESS = "agent1q287dwsu2ng5zwfx9uxa7w3uc66dmh0p6zf0kccurlzdm00a2d86svg5zwf"
# The Bureau is running on the same machine, on its internal port.
AGENT_BUREAU_URL = "http://127.0.0.1:8001/submit" 

app = FastAPI()
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")

@app.post("/submit_job")
async def submit_job(request: UserRequest):
    """
    This endpoint reliably submits a job to the agent bureau and returns immediately.
    """
    try:
        print(f"Submitting job for '{request.risk_profile}' to agent bureau...")
        
        # Manually construct the message payload for the Bureau
        payload = {
            "destination": PORTFOLIO_AGENT_ADDRESS,
            "message": request.dict(),
            "message_type": "UserRequest" # This must match the model on the agent
        }

        # Send the job to the Bureau's /submit endpoint
        response = requests.post(AGENT_BUREAU_URL, json=payload, timeout=10.0)
        response.raise_for_status() # Raise an error for bad status codes

        return {"status": "success", "message": "Job successfully submitted. Please monitor agent logs for the result."}

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)