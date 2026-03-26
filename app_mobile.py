import streamlit as st
import sqlite3
import os
from pathlib import Path

# --- 1. CONFIGURATION DE LA PAGE & CHEMINS ---
st.set_page_config(page_title="Assistant CCN 3239", layout="centered")

# Utilisation d'un chemin relatif pour que GitHub trouve la base de données
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "CCN_3239.db"

def get_connection():
    """Crée une connexion à la base de données SQLite."""
    return sqlite3.connect(str(DB_PATH))

# --- 2. STYLE CSS (Optimisé pour Mobile) ---
st.markdown("""
    <style>
    /* Boutons larges et tactiles */
    .stButton>button { 
        width: 100%; 
        border-radius: 12px; 
        height: 3.8em; 
        font-weight: bold; 
        margin-bottom: 12px; 
        border: 2px solid #dcdde1;
        white-space: normal;
        font-size: 16px;
    }
    /* Boîte de question */
    .question-box { 
        background-color: #f1f2f6; 
        padding: 20px; 
        border-radius: 15px; 
        border-left: 8px solid #1e3799; 
        margin-bottom: 25px; 
    }
    /* Boîte de contenu (Résumé ou Texte brut) */
    .essentiel-box { 
        background-color: #ecfdf5; 
        border-left: 5px solid #27ae60; 
        padding: 20px; 
        border-radius: 10px; 
        font-size: 18px; 
        line-height: 1.6;
        color: #1e272e;
        margin-top: 10px;
    }
    .titre-art { 
        color: #1e3799; 
        font-weight: bold; 
        font-size: 22px; 
        margin-bottom: 5px; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. VÉRIFICATION DE LA BASE DE DONNÉES ---
if not DB_PATH.exists():
    st.error("⚠️ Erreur : La base de données 'CCN_3239.db' est introuvable.")
    st.info(f"Vérifiez que le fichier est bien présent sur GitHub à côté de ce script.")
    st.stop()

# --- 4. LOGIQUE DE NAVIGATION ---
if 'etape' not in st.session_state:
    st.session_state.etape = 1
    st.session_state.choix = {}

st.title("🛡️ Assistant CCN 3239")
conn = get_connection()

try:
    # --- ÉTAPE 1 : CHOIX DU MÉTIER (SOCLE) ---
    if st.session_state.etape == 1:
        st.markdown("<div class='question-box'><h3>1. Quel est votre métier ?</h3></div>", unsafe_allow_html=True)
        
        metiers = {
            "🧸 Assistant Maternel": "SOCLE ASSISTANT MATERNEL",
            "👶 Assistant Parental (Garde d'enfants)": "SOCLE SALARIÉ DU PARTICULIER EMPLOYEUR",
            "👨‍🦽 Assistant de Vie / Employé familial": "SOCLE SALARIÉ DU PARTICULIER EMPLOYEUR",
            "🛠 Autres / Dispositions Communes": "DISPOSITIONS COMMUNES"
        }
        
        for label, socle_val in metiers.items():
            if st.button(label):
                st.session_state.choix['socle'] = socle_val
                st.session_state.etape = 2
                st.rerun()

    # --- ÉTAPE 2 : CHOIX DU THÈME (CHAPITRE) ---
    elif st.session_state.etape == 2:
        st.markdown("<div class='question-box'><h3>2. Quel thème vous intéresse ?</h3></div>", unsafe_allow_html=True)
        
        # On récupère les thèmes uniques depuis la table de navigation
        themes = conn.execute("SELECT DISTINCT theme FROM navigation_pedagogique ORDER BY theme").fetchall()
        
        for t in themes:
            theme_nom = t[0]
            if st.button(theme_nom):
                st.session_state.choix['theme'] = theme_nom
                st.session_state.etape = 3
                st.rerun()
        
        if st.button("⬅️ Retour"):
            st.session_state.etape = 1
            st.rerun()

    # --- ÉTAPE 3 : CHOIX DE L'ARTICLE PRÉCIS ---
    elif st.session_state.etape == 3:
        theme_sel = st.session_state.choix['theme']
        st.markdown(f"<div class='question-box'><h3>3. {theme_sel}</h3><p>Choisissez un point précis :</p></div>", unsafe_allow_html=True)
        
        # On récupère les questions/boutons liés à ce thème
        query = "SELECT reponse_bouton, articles_lies FROM navigation_pedagogique WHERE theme = ?"
        options = conn.execute(query, (theme_sel,)).fetchall()

        for label_bouton, art_id in options:
            if st.button(label_bouton):
                st.session_state.choix['article_id'] = art_id
                st.session_state.etape = 4
                st.rerun()

        if st.button("⬅️ Retour"):
            st.session_state.etape = 2
            st.rerun()

    # --- ÉTAPE 4 : AFFICHAGE DU TEXTE (RÉSUMÉ OU INTÉGRAL) ---
    elif st.session_state.etape == 4:
        art_id = str(st.session_state.choix['article_id']).strip()
        socle_user = st.session_state.choix['socle']
        
        # Recherche du contenu dans la table principale
        # On cherche d'abord le socle spécifique, sinon on prend le premier trouvé (fallback)
        query = "SELECT affichage_article, texte_integral, texte_simplifie FROM convention_collective WHERE numero_article_isole = ? AND socle = ?"
        res = conn.execute(query, (art_id, socle_user)).fetchone()
        
        if not res:
            res = conn.execute("SELECT affichage_article, texte_integral, texte_simplifie FROM convention_collective WHERE numero_article_isole = ? LIMIT 1", (art_id,)).fetchone()

        if res:
            titre, integral, simplifie = res
            st.markdown(f"<div class='titre-art'>Article {art_id}</div>", unsafe_allow_html=True)
            st.markdown(f"**{titre}**")
            
            # --- LOGIQUE D'AFFICHAGE DEMANDÉE ---
            # On vérifie si le résumé existe (non vide)
            if simplifie and len(str(simplifie).strip()) > 10:
                st.success("💡 L'ESSENTIEL (Version simplifiée)")
                st.markdown(f"<div class='essentiel-box'>{simplifie}</div>", unsafe_allow_html=True)
                
                # Bouton pour lire le texte intégral
                st.write("")
                with st.expander("⚖️ Lire le texte intégral officiel"):
                    st.markdown(integral)
            else:
                # Si le résumé est vide, on affiche l'intégral directement
                st.info("⚖️ TEXTE OFFICIEL")
                st.markdown(f"<div class='essentiel-box'>{integral}</div>", unsafe_allow_html=True)
        else:
            st.error(f"Désolé, le contenu de l'article {art_id} est introuvable.")

        # Boutons de fin
        st.divider()
        if st.button("🔄 Faire une autre recherche"):
            st.session_state.etape = 1
            st.session_state.choix = {}
            st.rerun()
            
        if st.button("⬅️ Retour aux questions"):
            st.session_state.etape = 3
            st.rerun()

finally:
    conn.close()
