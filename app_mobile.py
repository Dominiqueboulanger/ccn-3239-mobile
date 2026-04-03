import streamlit as st
import sqlite3
import os

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Assistant CCN 3239", layout="centered")

# Design optimisé
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        height: 60px;
        font-size: 18px;
        border-radius: 12px;
        margin-bottom: 10px;
        background-color: #FFFFFF;
        border: 2px solid #E0E0E0;
    }
    .stTextInput > div > div > input {
        height: 50px;
        font-size: 18px;
    }
    </style>
    """, unsafe_allow_html=True)

def get_connection():
    conn = sqlite3.connect("CCN_3239.db")
    conn.row_factory = sqlite3.Row
    return conn

def afficher_dossier_article(num_racine):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM convention_collective 
        WHERE numero_article_isole = ? 
        OR numero_article_isole LIKE ?
        ORDER BY numero_article_isole ASC
    """, (str(num_racine), str(num_racine) + "-%"))
    
    articles = cursor.fetchall()
    conn.close()

    if articles:
        st.success(f"### 🎯 Dossier : Article {num_racine}")
        for art in articles:
            with st.container():
                st.markdown(f"#### 📄 {art['affichage_article']}")
                st.info(f"**💡 L'essentiel :** {art['texte_simplifie']}")
                with st.expander(f"⚖️ Texte officiel ({art['numero_article_isole']})"):
                    st.write(art['texte_integral'])
                st.divider()
    else:
        st.error(f"L'article {num_racine} n'a pas été trouvé.")

# --- INITIALISATION ---
if 'step' not in st.session_state:
    st.session_state.step = 1
    st.session_state.choix = {}

# --- HAUT DE PAGE : RECHERCHE RAPIDE ---
st.title("⚖️ Guide CCN 3239")

with st.expander("🔍 Recherche directe par n° d'article"):
    col1, col2 = st.columns([3, 1])
    with col1:
        art_direct = st.text_input("Ex: 139", key="search_input", label_visibility="collapsed")
    with col2:
        if st.button("Aller"):
            if art_direct:
                st.session_state.step = "DIRECT"
                st.session_state.art_cible = art_direct
                st.rerun()

if st.session_state.step != 1:
    if st.button("🏠 Retour à l'accueil principal"):
        st.session_state.step = 1
        st.session_state.choix = {}
        st.rerun()

st.divider()

# --- LOGIQUE DE L'ENTONNOIR ---

# MODE DIRECT
if st.session_state.step == "DIRECT":
    afficher_dossier_article(st.session_state.art_cible)

# NIVEAU 1 : ACCUEIL ET MÉTIER
elif st.session_state.step == 1:
    # --- BLOC D'EXPLICATION AJOUTÉ ICI ---
    st.info("""
    **Bienvenue dans votre assistant !** 🚀
    
    Trouvez votre réponse en 3 étapes :
    1. **Identifiez votre métier.**
    2. **Précisez le contexte** (salaire, congés, fin de contrat...).
    3. **Sélectionnez votre question** pour voir l'article officiel simplifié.
    
    *Pour un article précis, utilisez la loupe 🔍 en haut.*
    """)
    
    st.subheader("1️⃣ Quel est votre métier ?")
    metiers = {"🍼 Assistant Maternel": "art_am", "🏠 Employé Familial": "art_ef", "👵 Assistant de Vie": "art_ef", "🌳 Autres": "art_sc"}
    for label, col in metiers.items():
        if st.button(label):
            st.session_state.choix['colonne_metier'] = col
            st.session_state.step = 2
            st.rerun()

# NIVEAU 2 (Vie ou Fin)
elif st.session_state.step == 2:
    st.subheader("2️⃣ Quel est le moment ?")
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT etape_vie FROM questions_app"); etapes = [r[0] for r in cursor.fetchall()]; conn.close()
    for e in etapes:
        if st.button(e):
            st.session_state.choix['etape_vie'] = e
            st.session_state.step = 3
            st.rerun()
    if st.button("⬅️ Retour"): st.session_state.step = 1; st.rerun()

# NIVEAU 3 (Famille)
elif st.session_state.step == 3:
    st.subheader("3️⃣ Choisissez une catégorie")
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT famille FROM questions_app WHERE etape_vie = ?", (st.session_state.choix['etape_vie'],))
    familles = [r[0] for r in cursor.fetchall()]; conn.close()
    for f in familles:
        if st.button(f):
            st.session_state.choix['famille'] = f
            st.session_state.step = 4
            st.rerun()
    if st.button("⬅️ Retour"): st.session_state.step = 2; st.rerun()

# NIVEAU 4 (Thème)
elif st.session_state.step == 4:
    st.subheader("4️⃣ Précisez votre sujet")
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT theme FROM questions_app WHERE famille = ?", (st.session_state.choix['famille'],))
    themes = [r[0] for r in cursor.fetchall()]; conn.close()
    for t in themes:
        if st.button(t):
            st.session_state.choix['theme'] = t
            st.session_state.step = 5
            st.rerun()
    if st.button("⬅️ Retour"): st.session_state.step = 3; st.rerun()

# NIVEAU 5 (Question)
elif st.session_state.step == 5:
    st.subheader("5️⃣ Quelle est votre question ?")
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("SELECT id, question_claire FROM questions_app WHERE theme = ?", (st.session_state.choix['theme'],))
    questions = cursor.fetchall(); conn.close()
    for q in questions:
        if st.button(q['question_claire']):
            st.session_state.choix['id_question'] = q['id']
            st.session_state.step = 6
            st.rerun()
    if st.button("⬅️ Retour"): st.session_state.step = 4; st.rerun()

# NIVEAU 6 (Réponse)
elif st.session_state.step == 6:
    conn = get_connection(); cursor = conn.cursor()
    col = st.session_state.choix['colonne_metier']
    cursor.execute(f"SELECT {col} FROM questions_app WHERE id = ?", (st.session_state.choix['id_question'],))
    num_article_racine = cursor.fetchone()[0]
    conn.close()
    afficher_dossier_article(num_article_racine)
