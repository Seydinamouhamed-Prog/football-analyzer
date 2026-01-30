# ⚽ Football Performance Analyzer

Application web d'analyse de football avec prédictions Machine Learning - Projet M2 Software 2025-2026

## 👤 Auteurs

- **Seydina Mouhamad Fall** - Master 2 Data Science
- **Moustapha Touré** - Master 2 Data Science
- **Aminata Diaw** - Master 2 Data Science
## 📋 Description

Ce projet est une application d'analyse de football qui permet de :
- Consulter les classements en temps réel de plusieurs championnats européens
- Comparer les statistiques de différentes équipes
- Prédire les résultats de matchs avec du Machine Learning
- Simuler la fin de saison
- Suivre les matchs en direct

L'application utilise l'API gratuite de football-data.org pour récupérer les données en temps réel.

## 🎯 Fonctionnalités

### 1. Classement
- Affichage du classement actuel
- Statistiques par équipe (buts, victoires, défaites...)
- Graphiques interactifs

### 2. Prédictions ML
- Prédiction du résultat d'un match entre deux équipes
- Probabilités de victoire/nul/défaite
- Score probable
- Facteurs clés de la prédiction
- Confiance du modèle

### 3. Comparaison d'équipes
- Comparaison côte à côte de deux équipes
- Graphiques radar
- Statistiques détaillées

### 4. Matchs à venir
- Liste des prochains matchs
- Possibilité de prédire chaque match

### 5. Simulation de saison
- Simulation Monte Carlo de la fin de saison
- Probabilités de titre et de relégation

### 6. Matchs en direct
- Scores en temps réel
- Prédictions du score final

## 🛠 Technologies utilisées

- **Python 3.11**
- **Streamlit** - Interface web
- **Pandas / NumPy** - Traitement des données
- **Plotly** - Visualisations interactives
- **Scikit-learn** - Machine Learning
- **Docker** - Containerisation
- **API Football-Data** - Données en temps réel

## 📦 Installation et lancement

### Prérequis

- Docker et Docker Compose installés
- OU Python 3.11+ installé

### Avec Docker (recommandé)
```bash
# Cloner le projet
git clone https://github.com/Seydinamouhamed-Prog/football-analyzer
cd football-analyzer
Puis ouvrir .env et mettre :
FOOTBALL_API_KEY=VOTRE_TOKEN_API_ICI
FOOTBALL_API_URL=https://api.football-data.org/v4

# Lancer avec Docker Compose
docker-compose up --build

# L'application sera accessible sur http://localhost:8501
```

### Sans Docker
```bash
# Cloner le projet
git clone https://github.com/Seydinamouhamed-Prog/football-analyzer
cd football-analyzer

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
streamlit run app/streamlit_app.py
```

L'application sera accessible sur http://localhost:8501

## 🔑 Configuration

Le projet utilise l'API gratuite de football-data.org.

1. Créez un compte sur https://www.football-data.org/
2. Récupérez votre token API
3. Créez un fichier `.env` à la racine :
```
FOOTBALL_API_KEY=votre_token_ici
FOOTBALL_API_URL=https://api.football-data.org/v4
```

## 📁 Structure du projet
```
football-analyzer/
├── src/                      # Code source
│   ├── api_client.py        # Client API
│   ├── data_processor.py    # Traitement des données
│   ├── ml_predictor.py      # Modèle de prédiction
│   └── season_simulator.py  # Simulateur de saison
├── app/
│   └── streamlit_app.py     # Application principale
├── .streamlit/
│   └── config.toml          # Configuration Streamlit
├── config.py                # Configuration générale
├── requirements.txt         # Dépendances Python
├── Dockerfile              # Configuration Docker
├── docker-compose.yml      # Orchestration Docker
├── .gitignore
├── .dockerignore
└── README.md
```

## 🤖 Modèle de prédiction

Le modèle de prédiction utilise :
- La force calculée de chaque équipe (basée sur points, différence de buts, forme)
- L'avantage du terrain (5% bonus pour l'équipe à domicile)
- Les moyennes de buts marqués et encaissés
- La forme récente des équipes

Le modèle calcule les probabilités de victoire/nul/défaite et propose un score probable.

## ⚠️ Limitations

- L'API gratuite est limitée à 10 requêtes par minute
- Les données sont mises en cache pendant 10 minutes
- Les prédictions sont à but pédagogique uniquement
- Plan gratuit : 13 compétitions disponibles

## 📝 Notes

- Projet réalisé dans le cadre du cours "Data-Driven Application" - Master 2
- Les prédictions ne doivent pas être utilisées pour des paris
- Toutes les données proviennent de football-data.org

## 🔗 Liens

- **Repository GitHub** : https://github.com/Seydinamouhamed-Prog/football-analyzer
- **API Football-Data** : https://www.football-data.org/

## 📧 Contact

Pour toute question : seydina.mouhamad-fall@etu.univ-amu.fr

---

**Projet M2 Software - Université d'Aix-Marseille - Janvier 2026**
