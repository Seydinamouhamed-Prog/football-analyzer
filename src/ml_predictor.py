"""Machine Learning predictor for match outcomes"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class MatchPredictor:
    """Predict match outcomes using team statistics"""
    
    @staticmethod
    def calculate_team_strength(team_stats: Dict) -> float:
        """Calculate overall team strength score (0-100)"""
        if not team_stats:
            return 50.0
        
        # Weighted factors
        points_weight = 0.4
        goal_diff_weight = 0.3
        form_weight = 0.3
        
        # Normalize values
        max_points = 114  # Theoretical max for 38 games
        points_score = (team_stats.get('points', 0) / max_points) * 100
        
        # Goal difference (-50 to +50 range normalized)
        goal_diff = team_stats.get('goal_difference', 0)
        goal_diff_score = ((goal_diff + 50) / 100) * 100
        goal_diff_score = max(0, min(100, goal_diff_score))
        
        # Form (0-15 points possible in last 5 games)
        form_points = team_stats.get('form_points', 0)
        form_score = (form_points / 15) * 100
        
        # Calculate weighted strength
        strength = (
            points_score * points_weight +
            goal_diff_score * goal_diff_weight +
            form_score * form_weight
        )
        
        return round(strength, 2)
    
    @staticmethod
    def predict_match(
        home_team: Dict,
        away_team: Dict,
        home_advantage: float = 5.0
    ) -> Dict:
        """
        Predict match outcome
        
        Args:
            home_team: Home team stats
            away_team: Away team stats
            home_advantage: Home advantage bonus (default 5%)
            
        Returns:
            Dictionary with predictions
        """
        # Calculate strengths
        home_strength = MatchPredictor.calculate_team_strength(home_team)
        away_strength = MatchPredictor.calculate_team_strength(away_team)
        
        # Apply home advantage
        home_strength_adj = home_strength + home_advantage
        
        # Calculate probabilities
        total_strength = home_strength_adj + away_strength
        
        if total_strength == 0:
            home_win_prob = draw_prob = away_win_prob = 33.33
        else:
            # Base probabilities
            home_win_prob = (home_strength_adj / total_strength) * 100
            away_win_prob = (away_strength / total_strength) * 100
            
            # Draw probability (inverse of strength difference)
            strength_diff = abs(home_strength_adj - away_strength)
            draw_prob = max(15, 35 - (strength_diff * 0.3))
            
            # Adjust to ensure total = 100%
            remaining = 100 - draw_prob
            home_win_prob = (home_win_prob / (home_win_prob + away_win_prob)) * remaining
            away_win_prob = remaining - home_win_prob
            
        
        # Predict score based on avg goals
        home_avg_goals = home_team.get('avg_goals_scored', 1.5)
        away_avg_goals = away_team.get('avg_goals_scored', 1.5)
        home_avg_conceded = home_team.get('avg_goals_conceded', 1.0)
        away_avg_conceded = away_team.get('avg_goals_conceded', 1.0)
        
        # Expected goals
        home_expected = (home_avg_goals + away_avg_conceded) / 2
        away_expected = (away_avg_goals + home_avg_conceded) / 2
        
        # Add randomness
        home_score = max(0, round(home_expected))
        away_score = max(0, round(away_expected))
        
        # Determine winner
        if home_win_prob > away_win_prob and home_win_prob > draw_prob:
            predicted_winner = "home"
            if home_score <= away_score:
                home_score = away_score + 1
        elif away_win_prob > home_win_prob and away_win_prob > draw_prob:
            predicted_winner = "away"
            if away_score <= home_score:
                away_score = home_score + 1
        else:
            predicted_winner = "draw"
            away_score = home_score
        
        # Confidence (based on probability difference)
        max_prob = max(home_win_prob, draw_prob, away_win_prob)
        confidence = min(95, max_prob)
        
        return {
            'home_win_probability': round(home_win_prob, 1),
            'draw_probability': round(draw_prob, 1),
            'away_win_probability': round(away_win_prob, 1),
            'predicted_score': f"{home_score}-{away_score}",
            'predicted_winner': predicted_winner,
            'confidence': round(confidence, 1),
            'home_strength': round(home_strength, 1),
            'away_strength': round(away_strength, 1),
            'key_factors': MatchPredictor._get_key_factors(home_team, away_team)
        }
    
    @staticmethod
    def _get_key_factors(home_team: Dict, away_team: Dict) -> list:
        """Identify key factors influencing the prediction"""
        factors = []
        
        # Form comparison
        home_form = home_team.get('form_points', 0)
        away_form = away_team.get('form_points', 0)
        
        if home_form > away_form + 3:
            factors.append(f"🔥 {home_team['name']} en meilleure forme")
        elif away_form > home_form + 3:
            factors.append(f"🔥 {away_team['name']} en meilleure forme")
        
        # Goal difference
        home_gd = home_team.get('goal_difference', 0)
        away_gd = away_team.get('goal_difference', 0)
        
        if home_gd > away_gd + 10:
            factors.append(f"⚽ {home_team['name']} meilleure différence de buts")
        elif away_gd > home_gd + 10:
            factors.append(f"⚽ {away_team['name']} meilleure différence de buts")
        
        # Home advantage
        factors.append(f"🏠 Avantage domicile pour {home_team['name']}")
        
        # Attack vs Defense
        home_attack = home_team.get('avg_goals_scored', 0)
        away_defense = away_team.get('avg_goals_conceded', 100)
        
        if home_attack > 2.0 and away_defense > 1.5:
            factors.append(f"⚔️ Attaque {home_team['name']} vs Défense faible {away_team['name']}")
        
        return factors[:3]  # Return top 3 factors