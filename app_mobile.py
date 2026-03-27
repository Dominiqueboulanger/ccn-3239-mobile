import streamlit as st
import sqlite3
import re
from pathlib import Path

# --- CONFIGURATION ---
st.set_page_config(page_title="Assistant CCN 3239", layout="centered")

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

st.title("🛡️ Assistant CCN 3239")

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
    st.markdown("<div class='question-box'><h3>2. Votre situation</h3><p>Envisagez-vous la fin de votre contrat ?</p></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Non"):
            st.session_state.choix['titre_filtre'] = "TITRE 1"
            st.session_state.etape = 3
            st.rerun()
    with col2:
        if st.button("Oui"):
            st.session_state.choix['titre_filtre'] = "TITRE 2"
            st.session_state.etape = 3
            st.rerun()
    if st.button("⬅️ Retour"):
        st.session_state.etape = 1
        st.rerun()

# --- ÉTAPE 3 : QUESTIONS ---
elif st.session_state.etape == 3:
    st.markdown("<div class='question-box'><h3>3. Quel sujet vous questionne ?</h3></div>", unsafe_allow_html=True)
    conn = get_connection()
    try:
        query = "SELECT q.id, q.question_texte, c.numero_article_isole FROM questions_app q INNER JOIN convention_collective c ON q.id = c.id WHERE c.socle = ? AND c.titres LIKE ?"
        questions = conn.execute(query, (st.session_state.choix['socle'], f"{st.session_state.choix['titre_filtre']}%")).fetchall()
        if not questions:
            st.warning("Aucune question trouvée.")
        else:
            for q in questions:
                if st.button(q['question_texte'], key=f"q_{q['id']}"):
                    st.session_state.choix['article_racine'] = q['numero_article_isole']
                    st.session_state.etape = 4
                    st.rerun()
    finally:
        conn.close()
    if st.button("⬅️ Retour", key="back3"):
        st.session_state.etape = 2
        st.rerun()

# --- ÉTAPE 4 : RÉSULTATS + LIENS D'ARTICLES ---
elif st.session_state.etape == 4:
    racine = st.session_state.choix['article_racine']
    socle = st.session_state.choix['socle']
    
    conn = get_connection()
    query = """
        SELECT numero_article_isole, affichage_article, texte_integral, texte_simplifie 
        FROM convention_collective 
        WHERE (numero_article_isole = ? OR numero_article_isole LIKE ?)
        AND socle = ?
        ORDER BY numero_article_isole ASC
    """
    articles = conn.execute(query, (str(racine), f"{racine}-%", socle)).fetchall()
    conn.close()

    if articles:
        st.markdown(f"### 📖 Détails pour l'Article {racine}")
        for art in articles:
            titre_complet = f"📄 Article {art['numero_article_isole']} - {art['affichage_article']}"
            
            with st.expander(titre_complet, expanded=True):
                # --- SYSTÈME DE LIEN AUTOMATIQUE ---
                texte_scan = f"{art['texte_integral']} {art['texte_simplifie']}"
                match = re.search(r"article\s+(\d+)", texte_scan, re.IGNORECASE)
                
                if match:
                    num_cite = match.group(1)
                    # On affiche le lien si l'article cité est différent de l'article actuel
                    if str(num_cite) != str(art['numero_article_isole']):
                        st.markdown(f"<div class='renvoi-box'>🔗 <b>Besoin de précision ?</b><br>Consultez l'article {num_cite} cité dans ce texte.</div>", unsafe_allow_html=True)
                        if st.button(f"👉 Ouvrir l'Article {num_cite}", key=f"link_{art['numero_article_isole']}_{num_cite}"):
                            # On redirige vers l'article cité (souvent dans le socle commun)
                            st.session_state.choix['article_racine'] = num_cite
                            st.session_state.choix['socle'] = "SOCLE COMMUN"
                            st.rerun()

                # --- CONTENU ---
                if art['texte_simplifie']:
                    st.markdown(f"<div class='essentiel-box'><b>💡 L'ESSENTIEL :</b><br>{art['texte_simplifie']}</div>", unsafe_allow_html=True)
                
                st.markdown("**⚖️ Texte Officiel :**")
                st.write(art['texte_integral'])
    else:
        st.error("Détails introuvables.")
    
    if st.button("🔄 Nouvelle recherche"):
        st.session_state.etape = 1
        st.rerun()
