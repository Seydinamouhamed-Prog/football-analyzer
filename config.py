"""Configuration for Football Analyzer"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = BASE_DIR / "models"

# Create directories
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# API Configuration
API_KEY = os.getenv("FOOTBALL_API_KEY", "")
API_URL = os.getenv("FOOTBALL_API_URL", "https://api.football-data.org/v4")

# Saison en cours
CURRENT_SEASON = "2024-2025"

# Available competitions (IDs football-data.org)
COMPETITIONS = {
    "Premier League": 2021,
    "La Liga": 2014,
    "Bundesliga": 2002,
    "Serie A": 2019,
    "Ligue 1": 2015,
    "Champions League": 2001,
    "Europa League": 2146
}

# Prediction parameters
RECENT_MATCHES = 5  # Nombre de matchs récents pour analyser la forme
MIN_MATCHES_FOR_PREDICTION = 10  # Minimum de matchs pour prédire

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"