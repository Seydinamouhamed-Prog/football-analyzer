"""Test diagnostic pour l'API Token"""

import os
from dotenv import load_dotenv

# Charger le .env
load_dotenv()

# Afficher le token (masqué partiellement)
token = os.getenv("FOOTBALL_API_KEY")

if token:
    print(f"✅ Token trouvé : {token[:10]}...{token[-5:]}")
    print(f"   Longueur : {len(token)} caractères")
else:
    print("❌ Token NOT FOUND dans .env")

# Test direct de l'API
import requests

print("\n=== Test API direct ===")
url = "https://api.football-data.org/v4/competitions"
headers = {"X-Auth-Token": token}

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ API fonctionne !")
        data = response.json()
        print(f"Compétitions disponibles: {len(data.get('competitions', []))}")
    elif response.status_code == 403:
        print("❌ 403 Forbidden")
        print("Raisons possibles:")
        print("1. Token invalide ou expiré")
        print("2. Compte pas activé (vérifiez email)")
        print("3. Plan gratuit ne donne pas accès à cette ressource")
    else:
        print(f"❌ Erreur: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Erreur: {e}")