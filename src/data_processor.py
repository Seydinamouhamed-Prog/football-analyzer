"""Data processing for football statistics"""

import pandas as pd
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class FootballDataProcessor:
    """Process football data for analysis"""
    
    @staticmethod
    def process_standings(standings_data: Dict) -> pd.DataFrame:
        """Convert standings data to DataFrame"""
        table = standings_data['standings'][0]['table']
        
        df = pd.DataFrame([{
            'position': team['position'],
            'team': team['team']['name'],
            'played': team['playedGames'],
            'won': team['won'],
            'draw': team['draw'],
            'lost': team['lost'],
            'goals_for': team['goalsFor'],
            'goals_against': team['goalsAgainst'],
            'goal_difference': team['goalDifference'],
            'points': team['points']
        } for team in table])
        
        return df
    
    @staticmethod
    def calculate_form(matches: List[Dict], last_n: int = 5) -> Dict:
        """Calculate team form from last N matches"""
        if not matches or len(matches) == 0:
            return {
                'form_string': 'N/A',
                'wins': 0,
                'draws': 0,
                'losses': 0,
                'goals_scored': 0,
                'goals_conceded': 0,
                'points': 0
            }
        
        recent_matches = matches[:last_n]
        
        wins = draws = losses = 0
        goals_scored = goals_conceded = 0
        form_letters = []
        
        for match in recent_matches:
            home_score = match['score']['fullTime']['home']
            away_score = match['score']['fullTime']['away']
            
            # Determine if team is home or away
            is_home = match['homeTeam']['id'] == match.get('team_id')
            
            if is_home:
                team_score = home_score
                opponent_score = away_score
            else:
                team_score = away_score
                opponent_score = home_score
            
            goals_scored += team_score if team_score else 0
            goals_conceded += opponent_score if opponent_score else 0
            
            if team_score > opponent_score:
                wins += 1
                form_letters.append('W')
            elif team_score < opponent_score:
                losses += 1
                form_letters.append('L')
            else:
                draws += 1
                form_letters.append('D')
        
        return {
            'form_string': ''.join(form_letters),
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'goals_scored': goals_scored,
            'goals_conceded': goals_conceded,
            'points': wins * 3 + draws
        }
    
    @staticmethod
    def calculate_team_stats(team_matches: List[Dict]) -> Dict:
        """Calculate comprehensive team statistics"""
        if not team_matches:
            return {}
        
        total_matches = len(team_matches)
        home_matches = [m for m in team_matches if m.get('venue') == 'HOME']
        away_matches = [m for m in team_matches if m.get('venue') == 'AWAY']
        
        # Overall stats
        total_goals_scored = sum(m['score']['fullTime']['home'] if m.get('venue') == 'HOME' 
                                else m['score']['fullTime']['away'] 
                                for m in team_matches if m['score']['fullTime']['home'] is not None)
        
        total_goals_conceded = sum(m['score']['fullTime']['away'] if m.get('venue') == 'HOME' 
                                  else m['score']['fullTime']['home'] 
                                  for m in team_matches if m['score']['fullTime']['home'] is not None)
        
        return {
            'total_matches': total_matches,
            'home_matches': len(home_matches),
            'away_matches': len(away_matches),
            'goals_scored': total_goals_scored,
            'goals_conceded': total_goals_conceded,
            'avg_goals_scored': round(total_goals_scored / total_matches, 2) if total_matches > 0 else 0,
            'avg_goals_conceded': round(total_goals_conceded / total_matches, 2) if total_matches > 0 else 0
        }