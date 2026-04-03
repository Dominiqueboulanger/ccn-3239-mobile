import streamlit as st
import sqlite3
import os

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Assistant CCN 3239", layout="centered")

# Design adapté au mobile et à la barre latérale
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
    .stSuccess { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

def get_connection():
    conn = sqlite3.connect("CCN_3239.db")
    conn.row_factory = sqlite3.Row
    return conn

# --- FONCTION D'AFFICHAGE D'UN DOSSIER D'ARTICLES ---
def afficher_dossier_article(num_racine):
    conn = get_connection()
    cursor = conn.cursor()
    # On cherche l'article et ses sous-sections (ex: 47, 47-1...)
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
        st.error(f"L'article {num_racine} n'a pas été trouvé dans la base.")

# --- BARRE LATÉRALE (RECHERCHE DIRECTE) ---
with st.sidebar:
    st.title("🔍 Accès Direct")
    art_direct = st.text_input("Numéro d'article (ex: 139)")
    if st.button("Aller à l'article"):
        if art_direct:
            st.session_state.step = "DIRECT"
            st.session_state.art_cible = art_direct
            st.rerun()
    
    st.divider()
    if st.button("🏠 Retour à l'accueil"):
        st.session_state.step = 1
        st.session_state.choix = {}
        st.rerun()

# --- GESTION DE LA NAVIGATION PRINCIPALE ---
if 'step' not in st.session_state:
    st.session_state.step = 1
    st.session_state.choix = {}

def valider_etape(valeur, nom_cle):
    st.session_state.choix[nom_cle] = valeur
    st.session_state.step += 1
    st.rerun()

# --- INTERFACE PRINCIPALE ---

# MODE RECHERCHE DIRECTE
if st.session_state.step == "DIRECT":
    st.title(f"📖 Consultation Directe")
    afficher_dossier_article(st.session_state.art_cible)

# MODE ENTONNOIR (ÉTAPES 1 À 6)
elif st.session_state.step == 1:
    st.title("⚖️ Votre Guide CCN")
    st.subheader("1️⃣ Quel est votre métier ?")
    metiers = {"🍼 Assistant Maternel": "art_am", "🏠 Employé Familial": "art_ef", 
               "👵 Assistant de Vie": "art_ef", "🌳 Autres": "art_sc"}
    for label, col in metiers.items():
        if st.button(label): valider_etape(col, 'colonne_metier')

elif st.session_state.step == 2:
    st.subheader("2️⃣ Quel est le moment ?")
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT etape_vie FROM questions_app"); etapes = [r[0] for r in cursor.fetchall()]; conn.close()
    for e in etapes:
        if st.button(e): valider_etape(e, 'etape_vie')
    if st.button("⬅️ Retour"): st.session_state.step -= 1; st.rerun()

elif st.session_state.step == 3:
    st.subheader("3️⃣ Choisissez une catégorie")
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT famille FROM questions_app WHERE etape_vie = ?", (st.session_state.choix['etape_vie'],))
    familles = [r[0] for r in cursor.fetchall()]; conn.close()
    for f in familles:
        if st.button(f): valider_etape(f, 'famille')
    if st.button("⬅️ Retour"): st.session_state.step -= 1; st.rerun()

elif st.session_state.step == 4:
    st.subheader("4️⃣ Précisez votre sujet")
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT theme FROM questions_app WHERE famille = ?", (st.session_state.choix['famille'],))
    themes = [r[0] for r in cursor.fetchall()]; conn.close()
    for t in themes:
        if st.button(t): valider_etape(t, 'theme')
    if st.button("⬅️ Retour"): st.session_state.step -= 1; st.rerun()

elif st.session_state.step == 5:
    st.subheader("5️⃣ Quelle est votre question ?")
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("SELECT id, question_claire FROM questions_app WHERE theme = ?", (st.session_state.choix['theme'],))
    questions = cursor.fetchall(); conn.close()
    for q in questions:
        if st.button(q['question_claire']): valider_etape(q['id'], 'id_question')
    if st.button("⬅️ Retour"): st.session_state.step -= 1; st.rerun()

elif st.session_state.step == 6:
    conn = get_connection(); cursor = conn.cursor()
    col = st.session_state.choix['colonne_metier']
    cursor.execute(f"SELECT {col} FROM questions_app WHERE id = ?", (st.session_state.choix['id_question'],))
    num_article_racine = cursor.fetchone()[0]
    conn.close()
    
    afficher_dossier_article(num_article_racine)
    
    if st.button("🔄 Nouvelle recherche"):
        st.session_state.step = 1; st.session_state.choix = {}; st.rerun()
