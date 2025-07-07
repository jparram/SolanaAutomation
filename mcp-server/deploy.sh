#!/bin/bash
# Deployment script for Solana MCP Server

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f "./solana-mcp/.env" ]; then
  echo -e "${YELLOW}Creating .env file from template...${NC}"
  cp ./solana-mcp/.env.example ./solana-mcp/.env
  echo -e "${GREEN}Created .env file. Please edit it to add your PHALA_API_KEY and other settings.${NC}"
fi

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Check if Node.js is installed
if ! command_exists node; then
  echo -e "${RED}Error: Node.js is not installed. Please install it and try again.${NC}"
  exit 1
fi

# Check if npm is installed
if ! command_exists npm; then
  echo -e "${RED}Error: npm is not installed. Please install it and try again.${NC}"
  exit 1
fi

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
cd ./solana-mcp
npm install
echo -e "${GREEN}Dependencies installed successfully.${NC}"

# Verify environment variables
echo -e "${YELLOW}Verifying environment variables...${NC}"
source .env 2>/dev/null || true

if [ -z "$PHALA_API_KEY" ]; then
  echo -e "${RED}Warning: PHALA_API_KEY is not set in .env file.${NC}"
  echo -e "${YELLOW}Please set it before deploying to production.${NC}"
fi

if [ -z "$BEARER_TOKEN" ]; then
  echo -e "${RED}Warning: BEARER_TOKEN is not set in .env file.${NC}"
  echo -e "${YELLOW}Please set it before deploying to production.${NC}"
fi

# Deploy options
echo -e "\n${GREEN}Select deployment option:${NC}"
echo "1) Run locally"
echo "2) Deploy to AWS"
echo "3) Deploy to Google Cloud"
echo "4) Deploy to Azure"
echo "5) Deploy to custom provider"
echo "6) Exit"

read -p "Enter your choice (1-6): " choice

case $choice in
  1)
    echo -e "${YELLOW}Starting local server...${NC}"
    npm start
    ;;
  2)
    echo -e "${YELLOW}Deploying to AWS...${NC}"
    node deployment.js
    ;;
  3)
    echo -e "${YELLOW}Deploying to Google Cloud...${NC}"
    export CLOUD_PROVIDER="gcp"
    node deployment.js
    ;;
  4)
    echo -e "${YELLOW}Deploying to Azure...${NC}"
    export CLOUD_PROVIDER="azure"
    node deployment.js
    ;;
  5)
    echo -e "${YELLOW}Deploying to custom provider...${NC}"
    export CLOUD_PROVIDER="custom"
    node deployment.js
    ;;
  6)
    echo -e "${YELLOW}Exiting...${NC}"
    exit 0
    ;;
  *)
    echo -e "${RED}Invalid option. Exiting...${NC}"
    exit 1
    ;;
esac

echo -e "${GREEN}Done!${NC}"
