#!/usr/bin/env python
"""
Script de test de connexion - Teste l'authentification sans interface web
"""
import asyncio
import os
import sys
from typing import Optional
from dotenv import load_dotenv
import httpx

load_dotenv()

API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")

async def test_api_health() -> bool:
    """Vérifie que l'API est accessible"""
    print("\n🔌 TEST 1: Est-ce que l'API répond?")
    print("=" * 60)
    
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{API_BASE_URL}/")
            if response.status_code == 200:
                print(f"✅ API accessible: {API_BASE_URL}")
                print(f"   Status: {response.json()}")
                return True
            else:
                print(f"❌ API retourne {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Impossible de se connecter à {API_BASE_URL}")
        print(f"   Erreur: {str(e)}")
        print(f"\n💡 Solution: Lancez l'API en premier:")
        print(f"   cd d:\\PROJECTS\\Projet_Immobilier\\id_immobilier")
        print(f"   python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000")
        return False


async def test_login(email: str, password: str) -> Optional[dict]:
    """Teste la connexion avec email/password"""
    print(f"\n🔐 TEST 2: Test de connexion")
    print("=" * 60)
    print(f"Email: {email}")
    print(f"Password: {'*' * len(password)}")
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{API_BASE_URL}/auth/login",
                json={"email": email, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ CONNEXION RÉUSSIE!")
                print(f"   Token: {data['access_token'][:50]}...")
                print(f"   User: {data['user']['email']}")
                print(f"   Role: {data['user']['role']}")
                return data
            else:
                print(f"❌ Erreur {response.status_code}: {response.json().get('detail', 'Erreur inconnue')}")
                return None
    except Exception as e:
        print(f"❌ Erreur de connexion: {str(e)}")
        return None


async def main():
    print("\n" + "="*60)
    print("  TEST D'AUTHENTIFICATION - ID IMMOBILIER")
    print("="*60)
    
    # Vérifier l'API
    api_ok = await test_api_health()
    if not api_ok:
        sys.exit(1)
    
    # Lister les utilisateurs disponibles
    print(f"\n📋 UTILISATEURS DISPONIBLES")
    print("=" * 60)
    print("Utilisateurs de test connus:")
    print("  1. yannickmadjiadoum23@gmail.com (admin)")
    print("  2. yannickmadjiadoum@gmail.com (admin)")
    print("  3. nickson@gmail.com (user)")
    print("\n⚠️  Vous avez besoin du mot de passe pour ces comptes")
    
    # Demander l'email et le mot de passe
    print("\n" + "="*60)
    email = input("\nEntrez l'email: ").strip()
    password = input("Entrez le mot de passe: ").strip()
    
    if not email or not password:
        print("❌ Email et mot de passe requis!")
        sys.exit(1)
    
    # Tester la connexion
    result = await test_login(email, password)
    
    if result:
        print("\n" + "="*60)
        print("✅ AUTHENTIFICATION RÉUSSIE")
        print("="*60)
        print("\n🚀 Vous pouvez maintenant:")
        print("  1. Accéder au frontend: http://localhost:3000")
        print("  2. Accéder à l'admin: http://localhost:3001")
        print("  3. Accéder aux docs API: http://localhost:8000/docs")
    else:
        print("\n" + "="*60)
        print("❌ AUTHENTIFICATION ÉCHOUÉE")
        print("="*60)
        print("\nPossibilités:")
        print("  1. Vérifiez l'email et le mot de passe")
        print("  2. Le compte existe-t-il?")
        print("  3. Le compte est-il bloqué?")


if __name__ == "__main__":
    asyncio.run(main())
