#!/usr/bin/env python
"""
Script de diagnostic pour la connexion aux bases de données et test d'authentification
"""
import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import sys

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "id_immobilier")

async def test_mongodb_connection():
    """Test la connexion à MongoDB"""
    print("=" * 60)
    print("TEST 1: Connexion à MongoDB")
    print("=" * 60)
    
    if not MONGO_URI:
        print("❌ MONGO_URI manquante dans le fichier .env")
        return False
    
    print(f"✓ MONGO_URI trouvée")
    print(f"  Base de données: {MONGO_DB}")
    
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        db = client[MONGO_DB]
        
        # Test de connexion simple
        await client.server_info()
        print("✓ Connexion à MongoDB réussie!")
        
        # Lister les collections
        collections = await db.list_collection_names()
        print(f"\n✓ Collections trouvées: {', '.join(collections)}")
        
        # Compter les utilisateurs
        users = await db["users"].count_documents({})
        print(f"✓ Nombre d'utilisateurs: {users}")
        
        if users == 0:
            print("\n⚠️  PROBLÈME: Aucun utilisateur trouvé dans la base de données!")
            print("    => Vous devez créer au minimum un utilisateur pour tester la connexion")
        else:
            # Afficher les utilisateurs existants
            print("\n📋 Utilisateurs existants:")
            all_users = await db["users"].find({}, {"email": 1, "role": 1, "blocked": 1}).to_list(None)
            for user in all_users:
                role = user.get("role", "N/A")
                blocked = "❌ BLOQUÉ" if user.get("blocked") else "✓ Actif"
                print(f"   - {user.get('email')}: {role} ({blocked})")
        
        await client.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connexion: {str(e)}")
        print("\nVérifiez:")
        print("  1. La URL MongoDB dans le fichier .env")
        print("  2. Les identifiants MongoDB (utilisateur:mot_de_passe)")
        print("  3. L'accès réseau vers MongoDB Atlas")
        return False


async def create_test_user():
    """Crée un utilisateur de test"""
    print("\n" + "=" * 60)
    print("TEST 2: Création d'utilisateur de test")
    print("=" * 60)
    
    from api.auth.password import hash_password
    from api.utils import utc_now_iso
    
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        db = client[MONGO_DB]
        
        # Utilisateur de test
        test_email = "test@id-immobilier.togo"
        test_password = "TestPassword123"
        
        existing = await db["users"].find_one({"email": test_email})
        if existing:
            print(f"✓ Utilisateur test existe déjà: {test_email}")
            print(f"  Mot de passe: {test_password}")
            await client.close()
            return True
        
        user = {
            "email": test_email,
            "nom": "Test",
            "prenom": "Utilisateur",
            "hashed_password": hash_password(test_password),
            "role": "user",
            "favoris": [],
            "blocked": False,
            "created_at": utc_now_iso(),
        }
        
        result = await db["users"].insert_one(user)
        print(f"✓ Utilisateur créé avec succès!")
        print(f"  Email: {test_email}")
        print(f"  Password: {test_password}")
        print(f"  ID: {result.inserted_id}")
        
        # Créer aussi un admin
        admin_email = "admin@id-immobilier.togo"
        admin_password = "AdminPassword123"
        
        existing_admin = await db["users"].find_one({"email": admin_email})
        if not existing_admin:
            admin = {
                "email": admin_email,
                "nom": "Admin",
                "prenom": "Utilisateur",
                "hashed_password": hash_password(admin_password),
                "role": "admin",
                "favoris": [],
                "blocked": False,
                "created_at": utc_now_iso(),
            }
            
            result = await db["users"].insert_one(admin)
            print(f"\n✓ Admin créé avec succès!")
            print(f"  Email: {admin_email}")
            print(f"  Password: {admin_password}")
            print(f"  ID: {result.inserted_id}")
        else:
            print(f"\n✓ Admin existe déjà: {admin_email}")
        
        await client.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création: {str(e)}")
        return False


async def main():
    print("\n🔍 DIAGNOSTIC DE CONNEXION - ID IMMOBILIER\n")
    
    # Test 1: MongoDB
    mongo_ok = await test_mongodb_connection()
    
    if mongo_ok:
        # Test 2: Créer utilisateurs de test
        create_ok = await create_test_user()
        
        if create_ok:
            print("\n" + "=" * 60)
            print("✅ SETUP COMPLÈTE")
            print("=" * 60)
            print("\n📝 Instructions pour tester:")
            print("  1. Lancez l'API: python -m uvicorn api.main:app --reload")
            print("  2. Frontend utilisateur: npm start (port 3000)")
            print("  3. Admin interface: npm start (port 3001)")
            print("\n🔐 Identifiants de test:")
            print("  USER: test@id-immobilier.togo / TestPassword123")
            print("  ADMIN: admin@id-immobilier.togo / AdminPassword123")
    else:
        print("\n❌ Impossible de diagnostiquer: vérifiez la connexion MongoDB d'abord")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
