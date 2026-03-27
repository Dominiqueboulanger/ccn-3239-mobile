import streamlit as st
import sqlite3
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
    for label, socle_val in metiers.items():
        if st.button(label):
            st.session_state.choix['socle'] = socle_val
            st.session_state.etape = 2
            st.rerun()

# --- ÉTAPE 2 : SITUATION ---
elif st.session_state.etape == 2:
    st.markdown("<div class='question-box'><h3>2. Votre situation</h3><p>Souhaitez-vous consulter les règles de vie du contrat ou la fin du contrat ?</p></div>", unsafe_allow_html=True)
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

# --- ÉTAPE 3 : LISTE DES CHAPITRES ---
elif st.session_state.etape == 3:
    st.markdown(f"<div class='question-box'><h3>3. Choisissez un Chapitre</h3><p>Section : {st.session_state.choix['titre_filtre']}</p></div>", unsafe_allow_html=True)
    conn = get_connection()
    try:
        query = "SELECT DISTINCT chapitres FROM convention_collective WHERE socle = ? AND titres LIKE ? AND chapitres IS NOT NULL"
        chapitres = conn.execute(query, (st.session_state.choix['socle'], f"{st.session_state.choix['titre_filtre']}%")).fetchall()

        if not chapitres:
            st.warning("Aucun chapitre trouvé pour cette sélection.")
        else:
            for i, chap in enumerate(chapitres):
                nom_chap = chap['chapitres']
                if st.button(nom_chap, key=f"chap_{i}"):
                    st.session_state.choix['chapitre_selectionne'] = nom_chap
                    st.session_state.etape = 4
                    st.rerun()
    except Exception as e:
        st.error(f"Erreur : {e}")
    finally:
        conn.close()
    if st.button("⬅️ Retour"):
        st.session_state.etape = 2
        st.rerun()

# --- ÉTAPE 4 : LISTE DES ARTICLES DU CHAPITRE ---
elif st.session_state.etape == 4:
    st.markdown(f"<div class='question-box'><h3>4. Choisissez un Article</h3><p>Dans : {st.session_state.choix['chapitre_selectionne']}</p></div>", unsafe_allow_html=True)
    conn = get_connection()
    try:
        query = "SELECT numero_article_isole, affichage_article FROM convention_collective WHERE socle = ? AND chapitres = ? ORDER BY numero_article_isole ASC"
        articles = conn.execute(query, (st.session_state.choix['socle'], st.session_state.choix['chapitre_selectionne'])).fetchall()

        for i, art in enumerate(articles):
            label_art = f"Article {art['numero_article_isole']} - {art['affichage_article']}"
            if st.button(label_art, key=f"art_btn_{i}"):
                st.session_state.choix['article_id'] = art['numero_article_isole']
                st.session_state.etape = 5
                st.rerun()
    finally:
        conn.close()
    if st.button("⬅️ Retour"):
        st.session_state.etape = 3
        st.rerun()

# --- ÉTAPE 5 : AFFICHAGE FINAL ---
elif st.session_state.etape == 5:
    art_id = st.session_state.choix['article_id']
    socle = st.session_state.choix['socle']

    conn = get_connection()
    query = "SELECT * FROM convention_collective WHERE numero_article_isole = ? AND socle = ?"
    article = conn.execute(query, (art_id, socle)).fetchone()
    conn.close()

    if article:
        st.markdown(f"### 📄 Article {article['numero_article_isole']}")
        st.subheader(article['affichage_article'])

        if article['texte_simplifie']:
            st.markdown(f"<div class='essentiel-box'><b>💡 L'ESSENTIEL :</b><br>{article['texte_simplifie']}</div>", unsafe_allow_html=True)

        st.markdown("**⚖️ Texte Officiel :**")
        st.write(article['texte_integral'])

        # --- NOUVEAU : CHAMP DE SAISIE POUR NAVIGUER VERS UN AUTRE ARTICLE ---
        with st.form("nav_article"):
            st.markdown("**🔍 Aller à un autre article :**")
            col1, col2 = st.columns([3, 1])
            with col1:
                new_art_id = st.text_input("Numéro de l'article", placeholder="Ex: 1.2.3", label_visibility="collapsed")
            with col2:
                submitted = st.form_submit_button("Go")
            if submitted and new_art_id:
                st.session_state.choix['article_id'] = new_art_id
                st.rerun()

    if st.button("🔄 Nouvelle recherche"):
        st.session_state.etape = 1
        st.rerun()
