"""Test script for Football Data API"""

from src.api_client import FootballDataClient

# Initialize client
client = FootballDataClient()

# Test 1: Get Premier League standings
print("=== TEST 1: Premier League Standings ===")
try:
    standings = client.get_competition_standings(2021)
    
    # Display top 5 teams
    table = standings['standings'][0]['table']
    print("\nTop 5 Teams:")
    for team in table[:5]:
        print(f"{team['position']}. {team['team']['name']} - {team['points']} pts")
    
    print("\n✅ API fonctionne !")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    print("\nVérifiez que:")
    print("1. Votre API Token est correct dans .env")
    print("2. Vous avez bien validé votre compte sur football-data.org")