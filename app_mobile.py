import streamlit as st
import sqlite3
import re
from pathlib import Path

# --- CONFIGURATION ---
st.set_page_config(page_title="Navigation CCN 3239", layout="centered")

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

# --- ÉTAPE 1 : MÉTIER ---
if st.session_state.etape == 1:
    st.markdown("<div class='question-box'><h3>1. Quel est votre métier ?</h3></div>", unsafe_allow_html=True)
    metiers = {
        "Assistant Maternel": "SOCLE ASSISTANT MATERNEL",
        "Assistant Parental (Garde d'enfants)": "SOCLE SALARiÉ DU PARTICULIER EMPLOYEUR",
        "Assistant De Vie Dépendance": "SOCLE SALARiÉ DU PARTICULIER EMPLOYEUR",
        "Employé Familial": "SOCLE SALARiÉ DU PARTICULIER EMPLOYEUR",
        "Autres": "SOCLE COMMUN"
    }
    for i, (label, socle_val) in enumerate(metiers.items()):
        if st.button(label, key=f"m_{i}"):
            st.session_state.choix['socle'] = socle_val
            st.session_state.etape = 2
            st.rerun()

# --- ÉTAPE 2 : SITUATION ---
elif st.session_state.etape == 2:
    st.markdown("<div class='question-box'><h3>2. Votre situation</h3><p>Souhaitez-vous consulter la vie du contrat ou la fin du contrat ?</p></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Vie du contrat (Titre 1)"):
            st.session_state.choix['titre_filtre'] = "TITRE 1"
            st.session_state.etape = 3
            st.rerun()
    with col2:
        if st.button("Fin du contrat (Titre 2)"):
            st.session_state.choix['titre_filtre'] = "TITRE 2"
            st.session_state.etape = 3
            st.rerun()
    if st.button("⬅️ Retour"):
        st.session_state.etape = 1
        st.rerun()

# --- ÉTAPE 3 : CHAPITRES ---
elif st.session_state.etape == 3:
    st.markdown(f"### 📑 Choisissez un Chapitre")
    conn = get_connection()
    query = "SELECT DISTINCT chapitres FROM convention_collective WHERE socle = ? AND titres LIKE ? AND chapitres IS NOT NULL"
    chapitres = conn.execute(query, (st.session_state.choix['socle'], f"{st.session_state.choix['titre_filtre']}%")).fetchall()
    conn.close()
    
    for i, chap in enumerate(chapitres):
        if st.button(chap['chapitres'], key=f"c_{i}"):
            st.session_state.choix['chapitre_selectionne'] = chap['chapitres']
            st.session_state.etape = 4
            st.rerun()
    if st.button("⬅️ Retour"):
        st.session_state.etape = 2
        st.rerun()

# --- ÉTAPE 4 : ARTICLES ---
elif st.session_state.etape == 4:
    st.markdown(f"### 📄 Articles dans : {st.session_state.choix['chapitre_selectionne']}")
    conn = get_connection()
    query = "SELECT numero_article_isole, affichage_article FROM convention_collective WHERE socle = ? AND chapitres = ? ORDER BY numero_article_isole ASC"
    articles = conn.execute(query, (st.session_state.choix['socle'], st.session_state.choix['chapitre_selectionne'])).fetchall()
    conn.close()

    for i, art in enumerate(articles):
        if st.button(f"Art. {art['numero_article_isole']} - {art['affichage_article']}", key=f"a_{i}"):
            st.session_state.choix['article_id'] = art['numero_article_isole']
            st.session_state.etape = 5
            st.rerun()
    if st.button("⬅️ Retour"):
        st.session_state.etape = 3
        st.rerun()

# --- ÉTAPE 5 : AFFICHAGE FINAL AVEC LIEN AUTOMATIQUE ---
elif st.session_state.etape == 5:
    art_id = st.session_state.choix['article_id']
    socle = st.session_state.choix['socle']
    
    conn = get_connection()
    article = conn.execute("SELECT * FROM convention_collective WHERE numero_article_isole = ? AND socle = ?", (art_id, socle)).fetchone()
    conn.close()

    if article:
        st.markdown(f"### 📄 Article {article['numero_article_isole']}")
        st.subheader(article['affichage_article'])
        
        # --- DÉTECTION DU RENVOI (ex: Article 101 -> Article 47) ---
        texte_pour_scan = f"{article['texte_integral']} {article['texte_simplifie']}"
        match = re.search(r"article\s+(\d+)", texte_pour_scan, re.IGNORECASE)
        
        if match:
            num_cite = match.group(1)
            # On n'affiche le bouton que si le numéro cité est différent de l'article actuel
            if str(num_cite) != str(art_id):
                st.markdown(f"<div class='renvoi-box'>🔗 <b>Précision :</b> Cet article renvoie à l'article {num_cite} du socle commun.</div>", unsafe_allow_html=True)
                if st.button(f"👉 Consulter l'Article {num_cite}"):
                    st.session_state.choix['article_id'] = num_cite
                    st.session_state.choix['socle'] = "SOCLE COMMUN"
                    st.rerun()

        # --- CONTENU ---
        if article['texte_simplifie']:
            st.markdown(f"<div class='essentiel-box'><b>💡 L'ESSENTIEL :</b><br>{article['texte_simplifie']}</div>", unsafe_allow_html=True)
        
        st.markdown("**⚖️ Texte Officiel :**")
        st.write(article['texte_integral'])
    
    if st.button("🔄 Nouvelle recherche"):
        st.session_state.etape = 1
        st.rerun()
