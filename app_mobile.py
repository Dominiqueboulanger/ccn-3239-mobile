import streamlit as st
import sqlite3
import os

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Assistant CCN 3239", layout="centered")

# Style CSS pour optimiser l'affichage mobile
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        height: 60px;
        font-size: 18px;
        border-radius: 15px;
        margin-bottom: 10px;
        background-color: #f0f2f6;
        border: 1px solid #d1d5db;
    }
    .stSuccess { border-radius: 15px; }
    .stInfo { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

def get_connection():
    conn = sqlite3.connect("CCN_3239.db")
    conn.row_factory = sqlite3.Row
    return conn

# --- INITIALISATION DES ÉTAPES (SESSION STATE) ---
if 'step' not in st.session_state:
    st.session_state.step = 1
    st.session_state.choix = {}

def next_step(valeur, label_cle):
    st.session_state.choix[label_cle] = valeur
    st.session_state.step += 1
    st.rerun()

def reset():
    st.session_state.step = 1
    st.session_state.choix = {}
    st.rerun()

st.title("⚖️ Guide Interactif CCN")

# --- NIVEAU 1 : MÉTIER (PROFIL) ---
if st.session_state.step == 1:
    st.subheader("1️⃣ Quel est votre métier ?")
    options = {
        "🍼 Assistant Maternel": "art_am",
        "🏠 Employé Familial": "art_ef",
        "👵 Assistant de Vie": "art_ef",  # Particulier Employeur utilise souvent le socle EF/PE
        "🌳 Autres (Jardinier...)": "art_sc"
    }
    for label, col in options.items():
        if st.button(label):
            next_step(col, 'col_article')

# --- NIVEAU 2 : ÉTAPE DE VIE (CONTEXTE) ---
elif st.session_state.step == 2:
    st.subheader("2️⃣ Quel est le moment ?")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT etape_vie FROM questions_app")
    etapes = [row[0] for row in cursor.fetchall()]
    conn.close()

    for etape in etapes:
        if st.button(etape):
            next_step(etape, 'etape_vie')
    
    if st.button("⬅️ Retour"): st.session_state.step -= 1; st.rerun()

# --- NIVEAU 3 : FAMILLE (DOMAINE) ---
elif st.session_state.step == 3:
    st.subheader("3️⃣ Choisissez une catégorie")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT famille FROM questions_app WHERE etape_vie = ?", (st.session_state.choix['etape_vie'],))
    familles = [row[0] for row in cursor.fetchall()]
    conn.close()

    for famille in familles:
        if st.button(famille):
            next_step(famille, 'famille')
    
    if st.button("⬅️ Retour"): st.session_state.step -= 1; st.rerun()

# --- NIVEAU 4 : THÈME (CIBLE) ---
elif st.session_state.step == 4:
    st.subheader("4️⃣ Précisez votre recherche")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT theme FROM questions_app WHERE famille = ?", (st.session_state.choix['famille'],))
    themes = [row[0] for row in cursor.fetchall()]
    conn.close()

    for theme in themes:
        if st.button(theme):
            next_step(theme, 'theme')
    
    if st.button("⬅️ Retour"): st.session_state.step -= 1; st.rerun()

# --- NIVEAU 5 : QUESTION FINALE (BESOIN) ---
elif st.session_state.step == 5:
    st.subheader("5️⃣ Votre question")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT question_claire, id FROM questions_app WHERE theme = ?", (st.session_state.choix['theme'],))
    questions = cursor.fetchall()
    conn.close()

    for q in questions:
        if st.button(q['question_claire']):
            # On stocke l'ID de la ligne de la question pour récupérer l'article correspondant
            next_step(q['id'], 'question_id')
    
    if st.button("⬅️ Retour"): st.session_state.step -= 1; st.rerun()

# --- NIVEAU 6 : RÉPONSE (ARTICLE FINAL) ---
elif st.session_state.step == 6:
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. On récupère d'abord le numéro de l'article spécifique au métier dans questions_app
    cursor.execute(f"SELECT {st.session_state.choix['col_article']} FROM questions_app WHERE id = ?", (st.session_state.choix['question_id'],))
    num_article = cursor.fetchone()[0]
    
    # 2. On va chercher le contenu de cet article dans la table convention_collective
    cursor.execute("SELECT * FROM convention_collective WHERE numero_article_isole = ?", (str(num_article),))
    art = cursor.fetchone()
    conn.close()

    if art:
        st.success(f"### 🎯 Article {art['numero_article_isole']} : {art['affichage_article']}")
        st.info(f"**💡 L'essentiel à retenir :**\n\n{art['texte_simplifie']}")
        
        with st.expander("⚖️ Voir le texte officiel (Loi)"):
            st.write(art['texte_integral'])
    else:
        st.error(f"Désolé, le texte de l'article {num_article} n'est pas encore disponible.")

    if st.button("🔄 Recommencer une recherche"):
        reset()
