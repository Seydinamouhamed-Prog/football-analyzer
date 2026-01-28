"""Main Streamlit application for Football Analyzer"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api_client import FootballDataClient
from src.data_processor import FootballDataProcessor
from src.ml_predictor import MatchPredictor
from config import COMPETITIONS
# Custom CSS
st.markdown("""
<style>
    /* Header styling */
    h1 {
        color: #00d4aa;
        font-size: 3rem !important;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        color: #00d4aa;
        border-bottom: 2px solid #00d4aa;
        padding-bottom: 10px;
    }
    
    h3 {
        color: #fafafa;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(90deg, #00d4aa 0%, #00a896 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 15px 30px;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 212, 170, 0.4);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1d29 0%, #0e1117 100%);
    }
    
    /* Card effect for containers */
    .element-container {
        border-radius: 10px;
    }
    
    /* Table styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Success/Info boxes */
    .stSuccess, .stInfo {
        border-radius: 10px;
        border-left: 5px solid #00d4aa;
    }
    
    /* Footer */
    footer {
        text-align: center;
        color: #666;
        padding: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize
@st.cache_resource
def init_components():
    """Initialize API client and processor"""
    return FootballDataClient(), FootballDataProcessor()

client, processor = init_components()

# Title
st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <h1>⚽ FOOTBALL ANALYZER</h1>
        <p style='font-size: 1.2rem; color: #888;'>
            Analyse & Prédictions ML • Saison 2024-2025
        </p>
    </div>
""", unsafe_allow_html=True)
def fetch_upcoming_matches(competition_id: int):
    """Fetch upcoming matches for a competition"""
    client = FootballDataClient()
    data = client.get_competition_matches(competition_id)

    return [
        match for match in data.get("matches", [])
        if match["status"] == "SCHEDULED"
    ]
# Sidebar
# Sidebar
st.sidebar.markdown("""
    <div style='text-align: center; padding: 20px 0;'>
        <h2 style='color: #00d4aa; border: none;'>⚙️ CONFIGURATION</h2>
    </div>
""", unsafe_allow_html=True)

# Select competition
selected_competition = st.sidebar.selectbox(
    "Sélectionnez une ligue",
    list(COMPETITIONS.keys()),
    index=0
)

competition_id = COMPETITIONS[selected_competition]
# Navigation
page = st.sidebar.radio(
    "Navigation",
    ["📊 Classement", "🎯 Prédictions", "⚔️ Comparaison","📅 Matchs à Venir", "🏆 Simulation Saison","🔴 Matchs en direct"]
)

st.sidebar.markdown("---")
# Refresh button
if st.sidebar.button("🔄 Actualiser"):
    st.cache_data.clear()
    st.rerun()

# Fetch standings (needed for all pages)
@st.cache_data(ttl=600)
def fetch_standings(comp_id):
    """Fetch and cache standings"""
    try:
        return client.get_competition_standings(comp_id)
    except Exception as e:
        st.error(f"Erreur: {e}")
        return None

standings_data = fetch_standings(competition_id)

if not standings_data:
    st.error("❌ Impossible de charger les données")
    st.stop()

# Process standings
standings_df = processor.process_standings(standings_data)

# ========================================
# PAGE 1: CLASSEMENT
# ========================================
if page == "📊 Classement":
    st.header(f"📊 {selected_competition} - Classement")
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    leader = standings_df.iloc[0]
    with col1:
        st.metric("🥇 Leader", leader['team'], f"{leader['points']} pts")
    
    with col2:
        total_goals = standings_df['goals_for'].sum()
        st.metric("⚽ Total buts", int(total_goals))
    
    with col3:
        avg_goals = standings_df['goals_for'].mean()
        st.metric("📊 Moyenne buts/équipe", f"{avg_goals:.1f}")
    
    with col4:
        total_matches = standings_df['played'].sum() / len(standings_df)
        st.metric("🎮 Journées jouées", int(total_matches))
    
    # Standings table
    st.subheader("📋 Classement complet")
    
    st.dataframe(
        standings_df.style.background_gradient(
            subset=['points'], 
            cmap='RdYlGn'
        ),
        use_container_width=True,
        height=600
    )
    
    # Visualizations
    st.header("📈 Visualisations")
    
    tab1, tab2, tab3 = st.tabs(["Points", "Buts", "Forme"])
    
    with tab1:
        fig_points = px.bar(
            standings_df.head(10),
            x='team',
            y='points',
            title='Top 10 - Points',
            labels={'points': 'Points', 'team': 'Équipe'},
            color='points',
            color_continuous_scale='Blues'
        )
        fig_points.update_layout(xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig_points, use_container_width=True)
    
    with tab2:
        fig_goals = go.Figure()
        fig_goals.add_trace(go.Bar(
            name='Buts marqués',
            x=standings_df.head(10)['team'],
            y=standings_df.head(10)['goals_for'],
            marker_color='green'
        ))
        fig_goals.add_trace(go.Bar(
            name='Buts encaissés',
            x=standings_df.head(10)['team'],
            y=standings_df.head(10)['goals_against'],
            marker_color='red'
        ))
        fig_goals.update_layout(
            title='Top 10 - Buts marqués vs encaissés',
            xaxis_tickangle=-45,
            barmode='group',
            height=500
        )
        st.plotly_chart(fig_goals, use_container_width=True)
    
    with tab3:
        fig_form = go.Figure()
        fig_form.add_trace(go.Bar(
            name='Victoires',
            x=standings_df.head(10)['team'],
            y=standings_df.head(10)['won'],
            marker_color='green'
        ))
        fig_form.add_trace(go.Bar(
            name='Nuls',
            x=standings_df.head(10)['team'],
            y=standings_df.head(10)['draw'],
            marker_color='orange'
        ))
        fig_form.add_trace(go.Bar(
            name='Défaites',
            x=standings_df.head(10)['team'],
            y=standings_df.head(10)['lost'],
            marker_color='red'
        ))
        fig_form.update_layout(
            title='Top 10 - Forme (V/N/D)',
            xaxis_tickangle=-45,
            barmode='stack',
            height=500
        )
        st.plotly_chart(fig_form, use_container_width=True)

# ========================================
# PAGE 2: PRÉDICTIONS ML
# ========================================
elif page == "🎯 Prédictions":
    st.header("🎯 Prédiction de Match (Machine Learning)")
    st.markdown("*Sélectionnez deux équipes pour prédire le résultat*")
    
    # Team selection
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏠 Équipe à domicile")
        home_team_name = st.selectbox(
            "Sélectionnez l'équipe à domicile",
            standings_df['team'].tolist(),
            key="home"
        )
    
    with col2:
        st.subheader("✈️ Équipe à l'extérieur")
        away_team_name = st.selectbox(
            "Sélectionnez l'équipe à l'extérieur",
            standings_df['team'].tolist(),
            key="away"
        )
    
    # Predict button
    if st.button("🔮 PRÉDIRE LE RÉSULTAT", type="primary", use_container_width=True):
        if home_team_name == away_team_name:
            st.error("⚠️ Veuillez sélectionner deux équipes différentes !")
        else:
            with st.spinner("Analyse en cours..."):
                # Get team stats
                home_stats = standings_df[standings_df['team'] == home_team_name].iloc[0].to_dict()
                away_stats = standings_df[standings_df['team'] == away_team_name].iloc[0].to_dict()
                
                # Add team names
                home_stats['name'] = home_team_name
                away_stats['name'] = away_team_name
                
                # Calculate averages
                home_stats['avg_goals_scored'] = home_stats['goals_for'] / max(home_stats['played'], 1)
                home_stats['avg_goals_conceded'] = home_stats['goals_against'] / max(home_stats['played'], 1)
                away_stats['avg_goals_scored'] = away_stats['goals_for'] / max(away_stats['played'], 1)
                away_stats['avg_goals_conceded'] = away_stats['goals_against'] / max(away_stats['played'], 1)
                
                # Form points (simplified)
                home_stats['form_points'] = home_stats['won'] * 3 + home_stats['draw']
                away_stats['form_points'] = away_stats['won'] * 3 + away_stats['draw']
                
                # Predict
                predictor = MatchPredictor()
                prediction = predictor.predict_match(home_stats, away_stats)
                
                # Display results
                st.success("✅ Prédiction générée !")
                
                st.markdown("---")
                
                # Match header
                st.markdown(f"## {home_team_name} 🆚 {away_team_name}")
                
                # Probabilities
                st.subheader("📊 Probabilités")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        f"🏠 {home_team_name}",
                        f"{prediction['home_win_probability']}%",
                        delta="Victoire" if prediction['predicted_winner'] == 'home' else None
                    )
                
                with col2:
                    st.metric(
                        "🤝 Match Nul",
                        f"{prediction['draw_probability']}%",
                        delta="Nul" if prediction['predicted_winner'] == 'draw' else None
                    )
                
                with col3:
                    st.metric(
                        f"✈️ {away_team_name}",
                        f"{prediction['away_win_probability']}%",
                        delta="Victoire" if prediction['predicted_winner'] == 'away' else None
                    )
                
                # Probability chart
                fig_prob = go.Figure(data=[
                    go.Bar(
                        x=[home_team_name, 'Nul', away_team_name],
                        y=[prediction['home_win_probability'], 
                           prediction['draw_probability'],
                           prediction['away_win_probability']],
                        marker_color=['#2ecc71', '#f39c12', '#e74c3c']
                    )
                ])
                fig_prob.update_layout(
                    title="Probabilités de résultat",
                    yaxis_title="Probabilité (%)",
                    height=400
                )
                st.plotly_chart(fig_prob, use_container_width=True)
                
                # Predicted score
                st.markdown("---")
                st.subheader("⚽ Score Prédit")
                st.markdown(f"### {prediction['predicted_score']}")
                st.info(f"💡 Confiance du modèle : **{prediction['confidence']}%**")
                
                # Key factors
                st.markdown("---")
                st.subheader("🔑 Facteurs Clés")
                for factor in prediction['key_factors']:
                    st.markdown(f"- {factor}")
                
                # Team strengths
                st.markdown("---")
                st.subheader("💪 Force des Équipes")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(f"🏠 {home_team_name}", f"{prediction['home_strength']}/100")
                
                with col2:
                    st.metric(f"✈️ {away_team_name}", f"{prediction['away_strength']}/100")


# ========================================
# PAGE 3: COMPARAISON
# ========================================
elif page == "⚔️ Comparaison":
    st.header("⚔️ Comparaison d'Équipes")
    st.markdown("*Comparez deux équipes côte à côte*")
    
    # Team selection
    col1, col2 = st.columns(2)
    
    with col1:
        team1_name = st.selectbox(
            "Première équipe",
            standings_df['team'].tolist(),
            key="comp1"
        )
    
    with col2:
        team2_name = st.selectbox(
            "Deuxième équipe",
            standings_df['team'].tolist(),
            key="comp2",
            index=1
        )
    
    if team1_name == team2_name:
        st.warning("⚠️ Sélectionnez deux équipes différentes")
    else:
        # Get team stats
        team1 = standings_df[standings_df['team'] == team1_name].iloc[0]
        team2 = standings_df[standings_df['team'] == team2_name].iloc[0]
        
        # Header
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.markdown(f"### 🏠 {team1_name}")
        with col2:
            st.markdown("### 🆚")
        with col3:
            st.markdown(f"### ✈️ {team2_name}")
        
        st.markdown("---")
        
        # Classement
        st.subheader("📊 Classement")
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            st.metric("Position", f"#{int(team1['position'])}")
            st.metric("Points", int(team1['points']))
        
        with col2:
            st.markdown("")
        
        with col3:
            st.metric("Position", f"#{int(team2['position'])}")
            st.metric("Points", int(team2['points']))
        
        # Stats générales
        st.markdown("---")
        st.subheader("⚽ Statistiques Générales")
        
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            st.metric("Matchs joués", int(team1['played']))
            st.metric("Victoires", int(team1['won']), delta=f"{int(team1['won'])}/{int(team1['played'])}")
            st.metric("Nuls", int(team1['draw']))
            st.metric("Défaites", int(team1['lost']))
        
        with col2:
            st.markdown("")
        
        with col3:
            st.metric("Matchs joués", int(team2['played']))
            st.metric("Victoires", int(team2['won']), delta=f"{int(team2['won'])}/{int(team2['played'])}")
            st.metric("Nuls", int(team2['draw']))
            st.metric("Défaites", int(team2['lost']))
        
        # Buts
        st.markdown("---")
        st.subheader("🎯 Attaque & Défense")
        
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            st.metric("Buts marqués", int(team1['goals_for']))
            st.metric("Moyenne buts/match", f"{team1['goals_for']/team1['played']:.2f}")
            st.metric("Buts encaissés", int(team1['goals_against']))
            st.metric("Différence de buts", int(team1['goal_difference']), 
                     delta="Positif" if team1['goal_difference'] > 0 else "Négatif")
        
        with col2:
            st.markdown("")
        
        with col3:
            st.metric("Buts marqués", int(team2['goals_for']))
            st.metric("Moyenne buts/match", f"{team2['goals_for']/team2['played']:.2f}")
            st.metric("Buts encaissés", int(team2['goals_against']))
            st.metric("Différence de buts", int(team2['goal_difference']),
                     delta="Positif" if team2['goal_difference'] > 0 else "Négatif")
        
        # Graphiques comparatifs
        st.markdown("---")
        st.subheader("📈 Comparaison Visuelle")
        
        # Stats radar
        categories = ['Points', 'Victoires', 'Buts marqués', 'Différence buts']
        
        # Normalize values for radar
        max_points = standings_df['points'].max()
        max_wins = standings_df['won'].max()
        max_goals = standings_df['goals_for'].max()
        max_gd = standings_df['goal_difference'].max()
        
        team1_values = [
            (team1['points'] / max_points) * 100,
            (team1['won'] / max_wins) * 100,
            (team1['goals_for'] / max_goals) * 100,
            ((team1['goal_difference'] + abs(standings_df['goal_difference'].min())) / 
             (max_gd + abs(standings_df['goal_difference'].min()))) * 100
        ]
        
        team2_values = [
            (team2['points'] / max_points) * 100,
            (team2['won'] / max_wins) * 100,
            (team2['goals_for'] / max_goals) * 100,
            ((team2['goal_difference'] + abs(standings_df['goal_difference'].min())) / 
             (max_gd + abs(standings_df['goal_difference'].min()))) * 100
        ]
        
        fig_radar = go.Figure()
        
        fig_radar.add_trace(go.Scatterpolar(
            r=team1_values,
            theta=categories,
            fill='toself',
            name=team1_name,
            line_color='#2ecc71'
        ))
        
        fig_radar.add_trace(go.Scatterpolar(
            r=team2_values,
            theta=categories,
            fill='toself',
            name=team2_name,
            line_color='#e74c3c'
        ))
        
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            height=500,
            title="Comparaison des performances (normalisée)"
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # Bar comparison
        comparison_data = pd.DataFrame({
            'Statistique': ['Points', 'Victoires', 'Buts marqués', 'Buts encaissés'],
            team1_name: [team1['points'], team1['won'], team1['goals_for'], team1['goals_against']],
            team2_name: [team2['points'], team2['won'], team2['goals_for'], team2['goals_against']]
        })
        
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(name=team1_name, x=comparison_data['Statistique'], 
                                 y=comparison_data[team1_name], marker_color='#2ecc71'))
        fig_bar.add_trace(go.Bar(name=team2_name, x=comparison_data['Statistique'], 
                                 y=comparison_data[team2_name], marker_color='#e74c3c'))
        
        fig_bar.update_layout(barmode='group', height=400, title="Statistiques comparatives")
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Verdict
        st.markdown("---")
        st.subheader("🏆 Verdict")
        
        team1_score = team1['points'] + (team1['goal_difference'] * 0.5)
        team2_score = team2['points'] + (team2['goal_difference'] * 0.5)
        
        if team1_score > team2_score:
            st.success(f"✅ **{team1_name}** est actuellement la meilleure équipe !")
        elif team2_score > team1_score:
            st.success(f"✅ **{team2_name}** est actuellement la meilleure équipe !")
        else:
            st.info("🤝 Les deux équipes sont très équilibrées !")
# ========================================
# PAGE 5: MATCHS À VENIR
# ========================================
elif page == "📅 Matchs à Venir":
    st.header("📅 Prochains Matchs")
    st.markdown("*Calendrier des matchs à venir*")
    
    # Fetch upcoming matches
    @st.cache_data(ttl=600)
    def fetch_upcoming_matches(comp_id):
        """Fetch upcoming matches"""
        try:
            data = client.get_competition_matches(comp_id)
            return data.get('matches', [])
        except Exception as e:
            st.error(f"Erreur: {e}")
            return []
    
    matches = fetch_upcoming_matches(competition_id)
    
    if not matches:
        st.warning("Aucun match disponible")
    else:
        # Filter upcoming matches (SCHEDULED or TIMED status)
        upcoming = [m for m in matches if m.get('status') in ['SCHEDULED', 'TIMED']]
        
        if not upcoming:
            st.info("Aucun match à venir planifié pour le moment")
        else:
            st.success(f"✅ {len(upcoming)} matchs à venir")
            
            # Group by matchday
            from datetime import datetime
            
            # Parse and sort by date
            for match in upcoming[:15]:  # Show next 15 matches
                match_date = match.get('utcDate', '')
                home_team = match.get('homeTeam', {}).get('name', 'N/A')
                away_team = match.get('awayTeam', {}).get('name', 'N/A')
                
                try:
                    date_obj = datetime.fromisoformat(match_date.replace('Z', '+00:00'))
                    formatted_date = date_obj.strftime('%d/%m/%Y %H:%M')
                except:
                    formatted_date = match_date
                
                # Create match card
                with st.container():
                    col1, col2, col3 = st.columns([2, 1, 2])
                    
                    with col1:
                        st.markdown(f"**{home_team}**")
                    
                    with col2:
                        st.markdown("🆚")
                        st.caption(formatted_date)
                    
                    with col3:
                        st.markdown(f"**{away_team}**")
                    
                    # Add prediction button
                    if st.button(f"🔮 Prédire ce match", key=f"predict_{match.get('id')}"):
                        # Get team IDs from standings
                        home_stats = standings_df[standings_df['team'] == home_team]
                        away_stats = standings_df[standings_df['team'] == away_team]
                        
                        if not home_stats.empty and not away_stats.empty:
                            home_data = home_stats.iloc[0].to_dict()
                            away_data = away_stats.iloc[0].to_dict()
                            
                            home_data['name'] = home_team
                            away_data['name'] = away_team
                            home_data['avg_goals_scored'] = home_data['goals_for'] / max(home_data['played'], 1)
                            home_data['avg_goals_conceded'] = home_data['goals_against'] / max(home_data['played'], 1)
                            away_data['avg_goals_scored'] = away_data['goals_for'] / max(away_data['played'], 1)
                            away_data['avg_goals_conceded'] = away_data['goals_against'] / max(away_data['played'], 1)
                            home_data['form_points'] = home_data['won'] * 3 + home_data['draw']
                            away_data['form_points'] = away_data['won'] * 3 + away_data['draw']
                            
                            predictor = MatchPredictor()
                            prediction = predictor.predict_match(home_data, away_data)
                            
                            st.info(f"**Prédiction**: {prediction['predicted_score']}")
                            st.caption(f"Probabilités: {home_team} {prediction['home_win_probability']}% | Nul {prediction['draw_probability']}% | {away_team} {prediction['away_win_probability']}%")
                        else:
                            st.warning("Équipes non trouvées dans le classement")
                    
                    st.markdown("---")
# ========================================
#Similation Saison
######################################
elif page == "🏆 Simulation Saison":
    from src.season_similator import SeasonSimulator

    st.header("🏆 Simulation de fin de saison")
    st.markdown("*Monte Carlo sur les matchs restants*")

    n_sim = st.slider("Nombre de simulations", 100, 2000, 500, step=100)

    if st.button("🚀 Lancer la simulation"):
        with st.spinner("Simulation en cours..."):
            matches = fetch_upcoming_matches(competition_id)
            upcoming = [m for m in matches if m['status'] in ['SCHEDULED', 'TIMED']]

            simulator = SeasonSimulator(standings_df)
            results = simulator.simulate_season(upcoming, n_simulations=n_sim)
            summary = simulator.summarize(results)

        st.success("✅ Simulation terminée")

        st.subheader("📊 Classement final simulé (moyenne)")
        st.dataframe(summary, use_container_width=True)

        st.subheader("🏆 Probabilité de titre")
        st.bar_chart(
            summary.set_index('team')['title_prob_%'].head(10)
        )

        st.subheader("🚨 Probabilité de relégation")
        st.bar_chart(
            summary.set_index('team')['relegation_prob_%'].tail(10)
        )
# ========================================
# PAGE LIVE: MATCHS EN DIRECT
# ========================================
elif page == "🔴 Matchs en direct":
    st.header("🔴 Matchs en Direct")
    st.markdown("*Scores en temps réel*")

    @st.cache_data(ttl=60)
    def fetch_live_matches():
        try:
            data = client.get_live_matches()
            return data.get("matches", [])
        except Exception as e:
            st.error(f"Erreur API : {e}")
            return []

    live_matches = fetch_live_matches()

    if not live_matches:
        st.info("⏳ Aucun match en cours actuellement")
    else:
        st.success(f"⚽ {len(live_matches)} match(s) en cours")

        for match in live_matches:
            home = match["homeTeam"]["name"]
            away = match["awayTeam"]["name"]
            score = match["score"]["fullTime"]
            minute = match.get("minute", "—")
            status = match["status"]

            with st.container():
                col1, col2, col3 = st.columns([3, 2, 3])

                with col1:
                    st.markdown(f"### 🏠 {home}")

                with col2:
                    st.markdown(
                        f"## {score['home']} - {score['away']}"
                    )
                    st.caption(f"⏱ {minute}' • {status}")

                with col3:
                    st.markdown(f"### ✈️ {away}")

                # Prediction button
                if st.button(f"🔮 Prédire le score final", key=f"live_{match['id']}"):
                    home_stats = standings_df[standings_df["team"] == home]
                    away_stats = standings_df[standings_df["team"] == away]

                    if not home_stats.empty and not away_stats.empty:
                        h = home_stats.iloc[0].to_dict()
                        a = away_stats.iloc[0].to_dict()

                        h["name"] = home
                        a["name"] = away

                        h["avg_goals_scored"] = h["goals_for"] / max(h["played"], 1)
                        h["avg_goals_conceded"] = h["goals_against"] / max(h["played"], 1)
                        a["avg_goals_scored"] = a["goals_for"] / max(a["played"], 1)
                        a["avg_goals_conceded"] = a["goals_against"] / max(a["played"], 1)

                        h["form_points"] = h["won"] * 3 + h["draw"]
                        a["form_points"] = a["won"] * 3 + a["draw"]

                        pred = MatchPredictor().predict_match(h, a)

                        st.info(
                            f"📊 **Probabilités finales** — "
                            f"{home} {pred['home_win_probability']}% | "
                            f"Nul {pred['draw_probability']}% | "
                            f"{away} {pred['away_win_probability']}%"
                        )
                        st.caption(f"🔮 Score prédit : {pred['predicted_score']}")
                    else:
                        st.warning("Stats indisponibles pour ce match")

                st.markdown("---")

# Footer
st.markdown("---")
st.markdown("*Données fournies par football-data.org | Mis à jour toutes les 10 minutes*")