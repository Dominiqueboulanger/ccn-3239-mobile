import streamlit as st
import sqlite3
import re
from pathlib import Path

# --- CONFIGURATION ---
st.set_page_config(page_title="Explorateur CCN 3239", layout="centered")

BASE_DIR = Path(__file__).parent
DB_PATH = (BASE_DIR / "CCN_3239.db").resolve()

def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row 
    return conn

# --- STYLE CSS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; min-height: 3.8em; font-weight: bold; margin-bottom: 10px; border: 2px solid #1e3799; background-color: white; }
    .question-box { background-color: #f8f9fa; padding: 20px; border-radius: 15px; border-left: 8px solid #1e3799; margin-bottom: 20px; }
    .essentiel-box { background-color: #ecfdf5; border-left: 5px solid #27ae60; padding: 15px; border-radius: 10px; color: #065f46; margin-bottom: 10px; }
    .renvoi-box { background-color: #fff9db; border: 2px dashed #f59f00; padding: 15px; border-radius: 10px; margin-bottom: 15px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

if 'etape' not in st.session_state:
    st.session_state.etape = 1
    st.session_state.choix = {}

st.title("📂 Explorateur CCN 3239")

# --- ÉTAPES 1 À 4 (Inchangées pour l'entonnoir) ---
# ... (Gardez votre logique de sélection Métier > Titre > Chapitre > Article) ...

# --- ÉTAPE 5 : AFFICHAGE FINAL (AVEC DÉTECTION DE RENVOI) ---
if st.session_state.etape == 5:
    art_id = st.session_state.choix['article_id']
    socle = st.session_state.choix['socle']
    
    conn = get_connection()
    article = conn.execute("SELECT * FROM convention_collective WHERE numero_article_isole = ? AND socle = ?", (art_id, socle)).fetchone()
    conn.close()

    if article:
        st.markdown(f"### 📄 Article {article['numero_article_isole']}")
        st.subheader(article['affichage_article'])
        
        # 1. Détection de renvoi dans le texte (ex: "article 47")
        texte_complet = f"{article['texte_integral']} {article['texte_simplifie']}"
        # Recherche du numéro d'article cité
        match = re.search(r"article\s+(\d+)", texte_complet, re.IGNORECASE)
        
        if match:
            num_cite = match.group(1)
            # On n'affiche le bouton que si c'est un renvoi vers un AUTRE article
            if str(num_cite) != str(art_id):
                st.markdown(f"<div class='renvoi-box'>🔗 <b>Renvoi détecté :</b> Cet article nécessite la lecture de l'article {num_cite} du socle commun.</div>", unsafe_allow_html=True)
                if st.button(f"👉 Ouvrir l'Article {num_cite}"):
                    st.session_state.choix['article_id'] = num_cite
                    st.session_state.choix['socle'] = "SOCLE COMMUN"
                    st.rerun()

        # 2. L'Essentiel
        if article['texte_simplifie']:
            st.markdown(f"<div class='essentiel-box'><b>💡 L'ESSENTIEL :</b><br>{article['texte_simplifie']}</div>", unsafe_allow_html=True)
        
        # 3. Texte Officiel
        st.markdown("**⚖️ Texte Officiel :**")
        st.write(article['texte_integral'])
    
    if st.button("🔄 Nouvelle recherche"):
        st.session_state.etape = 1
        st.rerun()
