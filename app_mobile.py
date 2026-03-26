import streamlit as st
import sqlite3
from pathlib import Path

# --- CONFIGURATION MOBILE ---
st.set_page_config(page_title="Assistant CCN", layout="centered")

# Chemin relatif pour GitHub
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "CCN_3239.db"

# Style pour de gros boutons tactiles
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        height: 4em;
        border-radius: 15px;
        font-weight: bold;
        font-size: 18px;
        margin-bottom: 10px;
        border: 2px solid #1e3799;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ CCN 3239")
st.subheader("Choisissez un thème :")

# --- CONNEXION ET AFFICHAGE ---
if DB_PATH.exists():
    conn = sqlite3.connect(str(DB_PATH))
    try:
        # On récupère les thèmes uniques de la table de navigation
        query = "SELECT DISTINCT theme FROM navigation_pedagogique ORDER BY theme"
        themes = conn.execute(query).fetchall()

        if themes:
            for t in themes:
                # Création d'un bouton par thème
                if st.button(f"📂 {t[0]}"):
                    st.success(f"Vous avez choisi : {t[0]}")
                    st.info("Étape suivante : Nous allons lier ce bouton aux métiers.")
        else:
            st.warning("La table 'navigation_pedagogique' semble vide.")
            
    except Exception as e:
        st.error(f"Erreur lors de la lecture de la table : {e}")
    finally:
        conn.close()
else:
    st.error("Fichier CCN_3239.db introuvable sur GitHub.")

st.caption("Application pas-à-pas - Étape 1 : Structure de navigation")
