#!/bin/bash

# FlightsKB Development Server Launcher
# Starts both backend (FastAPI) and frontend (Vite) servers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track PIDs for cleanup
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
    echo -e "\n${YELLOW}Shutting down...${NC}"

    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null && echo -e "${RED}Stopped backend${NC}"
    fi

    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null && echo -e "${RED}Stopped frontend${NC}"
    fi

    exit 0
}

# Set up trap for clean exit
trap cleanup SIGINT SIGTERM

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   FlightsKB Development Server${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check for virtual environment, create if missing (requires Python 3.11+)
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    # Try python3.11, python3.12, then fall back to python3
    if command -v python3.12 &> /dev/null; then
        python3.12 -m venv .venv
    elif command -v python3.11 &> /dev/null; then
        python3.11 -m venv .venv
    else
        echo -e "${RED}Error: Python 3.11+ required. Install python3.11 or python3.12.${NC}"
        exit 1
    fi
fi

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip to support pyproject.toml editable installs
pip install -q --upgrade pip

# Install/update Python dependencies (with api extras for FastAPI/uvicorn)
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install -q -e ".[api,ingest]"

# Check for node_modules in console
if [ ! -d "console/node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    (cd console && npm install)
fi

# Start backend
echo -e "${GREEN}Starting backend...${NC}"
python -W ignore::RuntimeWarning -m src.api.app &
BACKEND_PID=$!
echo -e "  Backend PID: $BACKEND_PID"

# Give backend a moment to start
sleep 1

# Start frontend
echo -e "${GREEN}Starting frontend...${NC}"
(cd console && npm run dev) &
FRONTEND_PID=$!
echo -e "  Frontend PID: $FRONTEND_PID"

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Services running:${NC}"
echo -e "  Backend:  ${BLUE}http://localhost:8000${NC}"
echo -e "  Frontend: ${BLUE}http://localhost:5173${NC}"
echo -e "  API Docs: ${BLUE}http://localhost:8000/docs${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Wait for both processes
wait
