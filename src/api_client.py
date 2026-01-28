"""API client for Football Data"""

import requests
import logging
from typing import Dict
import time

from config import API_KEY, API_URL

logger = logging.getLogger(__name__)


class FootballDataClient:
    """Client for Football Data API"""
    
    def __init__(self):
        """Initialize the API client"""
        self.base_url = API_URL
        self.headers = {
            "X-Auth-Token": API_KEY
        }
        self.last_request_time = 0
        
    def _rate_limit(self) -> None:
        """Implement rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < 6:
            time.sleep(6 - elapsed)
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str) -> Dict:
        """Make API request with error handling"""
        self._rate_limit()
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            logger.info(f"Successfully fetched data from {endpoint}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    def get_competition_standings(self, competition_id: int) -> Dict:
        """Get current standings for a competition"""
        endpoint = f"competitions/{competition_id}/standings"
        return self._make_request(endpoint)
    
    def get_team_info(self, team_id: int) -> Dict:
        """Get information about a specific team"""
        endpoint = f"teams/{team_id}"
        return self._make_request(endpoint)
    
    def get_team_matches(self, team_id: int, status: str = "FINISHED") -> Dict:
        """Get matches for a team"""
        endpoint = f"teams/{team_id}/matches?status={status}"
        return self._make_request(endpoint)
    
    def get_competition_matches(self, competition_id: int) -> Dict:
        """Get all matches for a competition"""
        endpoint = f"competitions/{competition_id}/matches"
        return self._make_request(endpoint)
    def get_live_matches(self) -> Dict:
        """Get live matches"""
        endpoint = "matches?status=LIVE"
        return self._make_request(endpoint)
