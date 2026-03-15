#!/bin/bash
# EduAI - Start everything with one command
# Usage: ./start.sh

DIR="$(cd "$(dirname "$0")" && pwd)"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

cleanup() {
  echo ""
  echo -e "${BLUE}Shutting down...${NC}"
  kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
  exit 0
}
trap cleanup INT TERM

# 1. Check Ollama
echo -e "${BLUE}[1/4] Checking Ollama...${NC}"
if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
  echo -e "${GREEN}  Ollama is running${NC}"
else
  echo -e "${RED}  Ollama not running. Starting it...${NC}"
  ollama serve &>/dev/null &
  sleep 2
fi

# Check qwen2.5:3b model
if ollama list 2>/dev/null | grep -q "qwen2.5:3b"; then
  echo -e "${GREEN}  qwen2.5:3b model found${NC}"
else
  echo -e "${BLUE}  Pulling qwen2.5:3b (first time only, may take a few minutes)...${NC}"
  ollama pull qwen2.5:3b
fi

# 2. Install Python deps if needed
echo -e "${BLUE}[2/4] Setting up Python backend...${NC}"
if [ ! -d "$DIR/.venv" ]; then
  python3 -m venv "$DIR/.venv"
fi
source "$DIR/.venv/bin/activate"
pip install -q fastapi uvicorn pydantic sqlalchemy httpx requests beautifulsoup4 python-dotenv PyPDF2 python-docx python-pptx python-multipart 2>/dev/null

# 3. Start backend
echo -e "${BLUE}[3/4] Starting backend on http://localhost:8000 ...${NC}"
cd "$DIR/src/APIendpoints"
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
sleep 3

if curl -s http://localhost:8000/health >/dev/null 2>&1; then
  echo -e "${GREEN}  Backend is running${NC}"
else
  echo -e "${RED}  Backend failed to start. Check logs above.${NC}"
  exit 1
fi

# 4. Start frontend
echo -e "${BLUE}[4/4] Starting frontend on http://localhost:5173 ...${NC}"
cd "$DIR/frontEnd"
if [ ! -d "node_modules" ]; then
  npm install
fi
npm run dev &
FRONTEND_PID=$!
sleep 3

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  EduAI is running!${NC}"
echo -e "${GREEN}  Frontend: http://localhost:5173${NC}"
echo -e "${GREEN}  Backend:  http://localhost:8000${NC}"
echo -e "${GREEN}  API docs: http://localhost:8000/docs${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Press Ctrl+C to stop everything."

wait
