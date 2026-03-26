#!/bin/bash
cd "$(dirname "$0")"

echo "=== Starting all services ==="

echo "[1/3] Starting FastAPI backend on port 8000..."
cd my_fastapi_project
python3 -m uvicorn app.main:app --reload --port 8000 &
cd ..

echo "[2/3] Starting React frontend on port 3000..."
cd pricingApp/frontend
npx react-scripts start &
cd ../..

echo "[3/3] Starting sampleShop on port 8080..."
cd sampleShop
python3 -m http.server 8080 &
cd ..

echo ""
echo "=== All services started ==="
echo "  - Backend:   http://localhost:8000"
echo "  - Frontend:  http://localhost:3000"
echo "  - sampleShop: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop all services"

wait