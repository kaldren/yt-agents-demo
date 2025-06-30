#!/bin/bash

# Install curl for health checks
apt-get update && apt-get install -y curl

# Set default values for environment variables
export PORT=${PORT:-8000}
export STREAMLIT_SERVER_PORT=${STREAMLIT_SERVER_PORT:-8501}
export STREAMLIT_SERVER_ADDRESS=${STREAMLIT_SERVER_ADDRESS:-0.0.0.0}

# Function to start FastAPI server
start_fastapi() {
    echo "Starting FastAPI server on port $PORT"
    cd /app/app
    uvicorn main:app --host 0.0.0.0 --port $PORT &
    FASTAPI_PID=$!
    echo "FastAPI server started with PID: $FASTAPI_PID"
}

# Function to start Streamlit server
start_streamlit() {
    echo "Starting Streamlit server on port $STREAMLIT_SERVER_PORT"
    cd /app
    streamlit run streamlit_app.py \
        --server.port $STREAMLIT_SERVER_PORT \
        --server.address $STREAMLIT_SERVER_ADDRESS \
        --server.headless true \
        --browser.gatherUsageStats false &
    STREAMLIT_PID=$!
    echo "Streamlit server started with PID: $STREAMLIT_PID"
}

# Function to handle shutdown
cleanup() {
    echo "Shutting down services..."
    if [ ! -z "$FASTAPI_PID" ]; then
        kill $FASTAPI_PID
    fi
    if [ ! -z "$STREAMLIT_PID" ]; then
        kill $STREAMLIT_PID
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Start both services
start_fastapi
start_streamlit

# Wait for both processes
wait 