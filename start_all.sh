#!/bin/bash
cd "$(dirname "$0")"

echo "=== Starting all services ==="

echo "[1/5] Starting FastAPI backend on port 8000..."
cd adminPanel
python3 -m uvicorn app.main:app --reload --port 8000 &
cd ..

echo "[2/5] Starting React frontend on port 3000..."
cd adminPanel/frontend
npx react-scripts start &
cd ../..

echo "[3/5] Starting sampleShop on port 8080..."
cd sampleShop
python3 -m http.server 8080 &
cd ..

echo "[4/5] Starting PokeIdealo on port 81..."
cd PokeIdealo
python3 -m http.server 81 &
cd ..

echo "[5/5] Starting Price Randomizer (updates every 30s)..."
cd sampleShop
python3 price_randomizer.py &
cd ..

echo ""
echo "=== All services started ==="
echo "  - Backend:       http://localhost:8000"
echo "  - Frontend:      http://localhost:3000"
echo "  - sampleShop:    http://localhost:8080"
echo "  - PokeIdealo:    http://localhost:81"
echo "  - Randomizer:    Running (updates prices every 30s)"
echo ""
echo "Press Ctrl+C to stop all services"

wait