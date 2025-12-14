#!/bin/bash

# GlyphScribe Docker Runner Script
# Usage: ./run.sh [batch|single|both|local-batch|local-single|local-both]

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}GlyphScribe Docker Runner${NC}"
echo -e "${BLUE}========================================${NC}"

# Check if credentials.json exists for Google Drive mode
check_credentials() {
    if [ ! -f "credentials.json" ]; then
        echo -e "${RED}Error: credentials.json not found!${NC}"
        echo -e "Please place your Google Drive OAuth credentials in credentials.json"
        echo -e "See GDRIVE_SETUP.md for instructions"
        exit 1
    fi
}

# Create gdrive_token directory if it doesn't exist
mkdir -p gdrive_token

# Function to run batch generator (Google Drive)
run_batch() {
    check_credentials
    echo -e "\n${GREEN}[1/2] Running Batch Generator (Google Drive upload)...${NC}"
    docker-compose run --rm batch-generator
    echo -e "${GREEN}✓ Batch generation complete!${NC}"
}

# Function to run single-word generator (Google Drive)
run_single() {
    check_credentials
    echo -e "\n${GREEN}[2/2] Running Single-Word Generator (Google Drive upload)...${NC}"
    docker-compose run --rm single-word-generator
    echo -e "${GREEN}✓ Single-word generation complete!${NC}"
}

# Function to run batch generator (local storage)
run_batch_local() {
    echo -e "\n${GREEN}[1/2] Running Batch Generator (local storage)...${NC}"
    docker-compose run --rm batch-generator-local
    echo -e "${GREEN}✓ Batch generation complete!${NC}"
}

# Function to run single-word generator (local storage)
run_single_local() {
    echo -e "\n${GREEN}[2/2] Running Single-Word Generator (local storage)...${NC}"
    docker-compose run --rm single-word-generator-local
    echo -e "${GREEN}✓ Single-word generation complete!${NC}"
}

# Parse command line argument
MODE=${1:-both}

case "$MODE" in
    batch)
        run_batch
        ;;
    single)
        run_single
        ;;
    both)
        run_batch
        run_single
        ;;
    local-batch)
        run_batch_local
        ;;
    local-single)
        run_single_local
        ;;
    local-both)
        run_batch_local
        run_single_local
        ;;
    *)
        echo -e "${RED}Error: Invalid argument '${MODE}'${NC}"
        echo "Usage: $0 [batch|single|both|local-batch|local-single|local-both]"
        echo ""
        echo "Google Drive modes (space-saving, recommended):"
        echo "  batch        - Run batch generator with Google Drive upload"
        echo "  single       - Run single-word generator with Google Drive upload"
        echo "  both         - Run both generators with Google Drive upload (default)"
        echo ""
        echo "Local storage modes (saves to ./out/):"
        echo "  local-batch  - Run batch generator with local storage"
        echo "  local-single - Run single-word generator with local storage"
        echo "  local-both   - Run both generators with local storage"
        exit 1
        ;;
esac

echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}✓ All tasks complete!${NC}"
echo -e "${BLUE}========================================${NC}"

if [[ "$MODE" == local-* ]]; then
    echo -e "Output location: ./out/"
    echo -e "  - Batch images: ./out/batch/images/"
    echo -e "  - Single-word images: ./out/single_words/images/"
else
    echo -e "Files uploaded to Google Drive!"
    echo -e "Check your Google Drive folder: ${YELLOW}GlyphScribe_Output${NC}"
fi
