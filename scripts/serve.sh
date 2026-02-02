#!/bin/bash
# Script pour lancer un serveur HTTP local et tester le site Help Car

echo "🚗 Help Car - Serveur de développement"
echo "======================================"
echo ""
echo "Lancement du serveur sur http://localhost:8000"
echo "Appuyez sur Ctrl+C pour arrêter"
echo ""

cd build/fr
python3 -m http.server 8000
