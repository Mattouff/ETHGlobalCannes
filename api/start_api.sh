#!/bin/bash
# Script de démarrage pour l'API IntentFi CCIP

echo "🚀 Starting IntentFi CCIP API Server"
echo "=================================="

# Vérifier l'environnement Python
if [ ! -d "/Users/matteo/ETHGlobalCannes/.venv" ]; then
    echo "❌ Virtual environment not found. Please run 'configure_python_environment' first."
    exit 1
fi

# Activer l'environnement virtuel et lancer l'API
cd /Users/matteo/ETHGlobalCannes/api

echo "📦 Environment: Virtual Environment Python 3.13.5"
echo "🌐 API will be available at: http://localhost:5001"
echo "📖 API Documentation: http://localhost:5001/"
echo ""
echo "🔧 Starting server..."

# Lancer l'API avec l'environnement Python configuré
/Users/matteo/ETHGlobalCannes/.venv/bin/python app.py
