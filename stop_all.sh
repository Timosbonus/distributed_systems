#!/bin/bash

echo "=== Stopping all services ==="

echo "Stopping FastAPI backend (port 8000)..."
pkill -f "uvicorn app.main:app" 2>/dev/null

echo "Stopping React frontend (port 3000)..."
pkill -f "react-scripts start" 2>/dev/null

echo "Stopping sampleShop (port 8080)..."
pkill -f "http.server 8080" 2>/dev/null

echo "Stopping PokeMart (port 81)..."
pkill -f "http.server 81" 2>/dev/null

echo ""
echo "=== All services stopped ==="