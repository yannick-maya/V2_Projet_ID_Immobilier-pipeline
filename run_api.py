#!/usr/bin/env python
"""
Script de lancement de l'API FastAPI pour ID Immobilier
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire courant au PYTHONPATH
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Importer et lancer l'application
try:
    from api.main import app
    import uvicorn

    print("🚀 Démarrage de l'API ID Immobilier...")
    print(f"📁 Répertoire de travail: {current_dir}")
    print(f"🐍 Python path: {sys.path[0]}")

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
except ImportError as e:
    print(f"❌ Erreur d'importation: {e}")
    print("Vérifiez que tous les modules sont installés")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erreur générale: {e}")
    sys.exit(1)
