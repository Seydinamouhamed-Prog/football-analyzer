import copy
import pandas as pd
from collections import defaultdict
from src.ml_predictor import MatchPredictor


class SeasonSimulator:
    def __init__(self, standings_df: pd.DataFrame):
        self.base_standings = standings_df.copy()
        self.predictor = MatchPredictor()

    def _init_table(self):
        table = {}
        for _, row in self.base_standings.iterrows():
            table[row['team']] = {
                'points': row['points'],
                'goal_difference': row['goal_difference'],
                'played': row['played'],
                'goals_for': row['goals_for'],
                'goals_against': row['goals_against'],
                'won': row['won'],
                'draw': row['draw'],
                'lost': row['lost']
            }
        return table

    def simulate_match(self, home, away, table):
        home_data = table[home].copy()
        away_data = table[away].copy()

        # stats nécessaires au ML
        for t in (home_data, away_data):
            t['avg_goals_scored'] = t['goals_for'] / max(t['played'], 1)
            t['avg_goals_conceded'] = t['goals_against'] / max(t['played'], 1)
            t['form_points'] = t['won'] * 3 + t['draw']

        home_data['name'] = home
        away_data['name'] = away

        pred = self.predictor.predict_match(home_data, away_data)

        # résultat
        if pred['predicted_winner'] == 'home':
            table[home]['points'] += 3
            table[home]['won'] += 1
            table[away]['lost'] += 1
        elif pred['predicted_winner'] == 'away':
            table[away]['points'] += 3
            table[away]['won'] += 1
            table[home]['lost'] += 1
        else:
            table[home]['points'] += 1
            table[away]['points'] += 1
            table[home]['draw'] += 1
            table[away]['draw'] += 1

    def simulate_season(self, remaining_matches, n_simulations=500):
        results = defaultdict(list)

        for _ in range(n_simulations):
            table = self._init_table()

            for match in remaining_matches:
                home = match['homeTeam']['name']
                away = match['awayTeam']['name']

                if home in table and away in table:
                    self.simulate_match(home, away, table)

            final = (
                pd.DataFrame.from_dict(table, orient='index')
                .sort_values(['points', 'goal_difference'], ascending=False)
            )

            for pos, team in enumerate(final.index, start=1):
                results[team].append(pos)

        return results

    @staticmethod
    def summarize(results, relegation_spots=3):
        summary = []

        for team, positions in results.items():
            summary.append({
                'team': team,
                'avg_position': round(sum(positions) / len(positions), 2),
                'title_prob_%': round(positions.count(1) / len(positions) * 100, 1),
                'relegation_prob_%': round(
                    sum(p > (20 - relegation_spots) for p in positions) / len(positions) * 100, 1
                )
            })

        return pd.DataFrame(summary).sort_values('avg_position')
