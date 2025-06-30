# Ryanair Flight Assistant

A chat application that answers questions about Ryanair flights using Azure AI Search.

## Project Structure

- `app/` - FastAPI backend application
- `streamlit_app.py` - Streamlit frontend interface
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container configuration
- `deploy.sh` - Automated deployment script

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_CHAT_MODEL_ID=your_chat_model
AZURE_OPENAI_EMBEDDING_MODEL_ID=your_embedding_model
AZURE_SEARCH_SERVICE_ENDPOINT=your_search_endpoint
AZURE_SEARCH_INDEX_NAME=your_index_name
AZURE_SEARCH_API_KEY=your_search_key
```

## Running the Application

### Option 1: FastAPI Backend Only
```bash
cd app
uvicorn main:app --reload
```
Access the API at: http://localhost:8000

### Option 2: Streamlit Frontend (Recommended)
1. Start the FastAPI backend:
```bash
cd app
uvicorn main:app --reload
```

2. In a new terminal, start the Streamlit frontend:
```bash
streamlit run streamlit_app.py
```
Access the web interface at: http://localhost:8501

### Option 3: Docker (Local)
```bash
# Build the Docker image
docker build -t ryanair-flight-assistant .

# Run the container
docker run -p 8000:8000 -p 8501:8501 --env-file .env ryanair-flight-assistant
```

## Deployment to Azure Container Apps

### Prerequisites
- Azure CLI installed and logged in
- Docker installed
- Azure subscription with Container Apps enabled

### Automated Deployment (Linux/macOS)
```bash
# Make the script executable (Linux/macOS only)
chmod +x deploy.sh

# Run the deployment script
./deploy.sh
```

### Manual Deployment

1. **Build and push to Azure Container Registry:**
```bash
# Create resource group
az group create --name ryanair-flight-assistant-rg --location eastus

# Create Azure Container Registry
az acr create --resource-group ryanair-flight-assistant-rg --name ryanairflightacr --sku Basic --admin-enabled true

# Login to ACR
az acr login --name ryanairflightacr

# Build and push image
docker build -t ryanairflightacr.azurecr.io/ryanair-flight-assistant:latest .
docker push ryanairflightacr.azurecr.io/ryanair-flight-assistant:latest
```

2. **Create Container Apps Environment:**
```bash
az containerapp env create \
    --name ryanair-flight-assistant-env \
    --resource-group ryanair-flight-assistant-rg \
    --location eastus
```

3. **Deploy Container App:**
```bash
# Get environment ID
ENVIRONMENT_ID=$(az containerapp env show --name ryanair-flight-assistant-env --resource-group ryanair-flight-assistant-rg --query id -o tsv)

# Create Container App
az containerapp create \
    --name ryanair-flight-assistant \
    --resource-group ryanair-flight-assistant-rg \
    --environment $ENVIRONMENT_ID \
    --image ryanairflightacr.azurecr.io/ryanair-flight-assistant:latest \
    --target-port 8501 \
    --ingress external \
    --min-replicas 1 \
    --max-replicas 2 \
    --cpu 1.0 \
    --memory 2Gi
```

4. **Configure Secrets:**
```bash
az containerapp secret set \
    --name ryanair-flight-assistant \
    --resource-group ryanair-flight-assistant-rg \
    --secrets \
        azure-openai-api-key="your-api-key" \
        azure-openai-endpoint="your-endpoint" \
        azure-openai-chat-model-id="your-chat-model" \
        azure-openai-embedding-model-id="your-embedding-model" \
        azure-search-service-endpoint="your-search-endpoint" \
        azure-search-index-name="your-index-name" \
        azure-search-api-key="your-search-key"
```

5. **Update Environment Variables:**
```bash
az containerapp update \
    --name ryanair-flight-assistant \
    --resource-group ryanair-flight-assistant-rg \
    --set-env-vars \
        AZURE_OPENAI_API_KEY=secretref:azure-openai-api-key \
        AZURE_OPENAI_ENDPOINT=secretref:azure-openai-endpoint \
        AZURE_OPENAI_CHAT_MODEL_ID=secretref:azure-openai-chat-model-id \
        AZURE_OPENAI_EMBEDDING_MODEL_ID=secretref:azure-openai-embedding-model-id \
        AZURE_SEARCH_SERVICE_ENDPOINT=secretref:azure-search-service-endpoint \
        AZURE_SEARCH_INDEX_NAME=secretref:azure-search-index-name \
        AZURE_SEARCH_API_KEY=secretref:azure-search-api-key
```

## Features

- **Session Management**: Each chat session maintains its own history
- **Persistent Chat History**: Chat history persists across application restarts
- **Azure AI Integration**: Uses Azure OpenAI for chat completions
- **Vector Search**: Integrates with Azure AI Search for document retrieval
- **Modern UI**: Clean Streamlit interface with real-time chat
- **Container Ready**: Dockerized for easy deployment
- **Auto-scaling**: Scales based on HTTP traffic
- **Health Monitoring**: Built-in health checks

## API Endpoints

- `GET /health` - Health check endpoint
- `POST /chat` - Send a message and get a response
- `GET /chat/history` - Get chat history for a session
- `GET /chat` - Test endpoint with sample conversation

## Monitoring

- **Application Logs**: View in Azure Portal or using Azure CLI
- **Metrics**: Monitor CPU, memory, and request metrics
- **Scaling**: Automatic scaling based on HTTP traffic
- **Health Checks**: Built-in readiness and liveness probes 