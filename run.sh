#!/bin/bash
# Start the agent bureau in the background
python3 main.py &
# Start the FastAPI gateway in the foreground
python3 gateway.py