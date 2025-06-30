#!/bin/bash

# Azure Container Apps Deployment Script
set -e

# Configuration
RESOURCE_GROUP="ryanair-flight-assistant-rg"
LOCATION="eastus"
ACR_NAME="ryanairflightacr"
CONTAINER_APP_NAME="ryanair-flight-assistant"
ENVIRONMENT_NAME="ryanair-flight-assistant-env"

echo "Starting deployment to Azure Container Apps..."

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "Azure CLI is not installed. Please install it first."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install it first."
    exit 1
fi

# Login to Azure
echo "Logging into Azure..."
az login

# Get subscription ID
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
echo "Using subscription: $SUBSCRIPTION_ID"

# Create resource group
echo "Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Container Registry
echo "Creating Azure Container Registry..."
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true

# Get ACR login server
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query loginServer -o tsv)

# Login to ACR
echo "Logging into Azure Container Registry..."
az acr login --name $ACR_NAME

# Build and push Docker image
echo "Building and pushing Docker image..."
docker build -t $ACR_LOGIN_SERVER/ryanair-flight-assistant:latest .
docker push $ACR_LOGIN_SERVER/ryanair-flight-assistant:latest

# Create Container Apps environment
echo "Creating Container Apps environment..."
az containerapp env create \
    --name $ENVIRONMENT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

# Get environment ID
ENVIRONMENT_ID=$(az containerapp env show --name $ENVIRONMENT_NAME --resource-group $RESOURCE_GROUP --query id -o tsv)

# Create Container App
echo "Creating Container App..."
az containerapp create \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $ENVIRONMENT_NAME \
    --image $ACR_LOGIN_SERVER/ryanair-flight-assistant:latest \
    --target-port 8501 \
    --ingress external \
    --min-replicas 1 \
    --max-replicas 2 \
    --cpu 1.0 \
    --memory 2Gi \
    --registry-server $ACR_LOGIN_SERVER \
    --registry-identity 'system' \
    --env-vars \
        PORT=8000 \
        STREAMLIT_SERVER_PORT=8501 \
        STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Set secrets (you'll need to provide these values)
echo "Setting up secrets..."
echo "Please provide the following values when prompted:"

read -p "Azure OpenAI API Key: " AZURE_OPENAI_API_KEY
read -p "Azure OpenAI Endpoint: " AZURE_OPENAI_ENDPOINT
read -p "Azure OpenAI Chat Model ID: " AZURE_OPENAI_CHAT_MODEL_ID
read -p "Azure OpenAI Embedding Model ID: " AZURE_OPENAI_EMBEDDING_MODEL_ID
read -p "Azure Search Service Endpoint: " AZURE_SEARCH_SERVICE_ENDPOINT
read -p "Azure Search Index Name: " AZURE_SEARCH_INDEX_NAME
read -p "Azure Search API Key: " AZURE_SEARCH_API_KEY

# Set secrets
az containerapp secret set \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --secrets \
        azure-openai-api-key="$AZURE_OPENAI_API_KEY" \
        azure-openai-endpoint="$AZURE_OPENAI_ENDPOINT" \
        azure-openai-chat-model-id="$AZURE_OPENAI_CHAT_MODEL_ID" \
        azure-openai-embedding-model-id="$AZURE_OPENAI_EMBEDDING_MODEL_ID" \
        azure-search-service-endpoint="$AZURE_SEARCH_SERVICE_ENDPOINT" \
        azure-search-index-name="$AZURE_SEARCH_INDEX_NAME" \
        azure-search-api-key="$AZURE_SEARCH_API_KEY"

# Update Container App with secret references
echo "Updating Container App with secret references..."
az containerapp update \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --set-env-vars \
        AZURE_OPENAI_API_KEY=secretref:azure-openai-api-key \
        AZURE_OPENAI_ENDPOINT=secretref:azure-openai-endpoint \
        AZURE_OPENAI_CHAT_MODEL_ID=secretref:azure-openai-chat-model-id \
        AZURE_OPENAI_EMBEDDING_MODEL_ID=secretref:azure-openai-embedding-model-id \
        AZURE_SEARCH_SERVICE_ENDPOINT=secretref:azure-search-service-endpoint \
        AZURE_SEARCH_INDEX_NAME=secretref:azure-search-index-name \
        AZURE_SEARCH_API_KEY=secretref:azure-search-api-key

# Get the application URL
APP_URL=$(az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv)

echo "Deployment completed successfully!"
echo "Your application is available at: https://$APP_URL"
echo "Monitor your app at: https://portal.azure.com/#@/resource/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.App/containerApps/$CONTAINER_APP_NAME" 