import streamlit as st
import sqlite3
import os

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Assistant CCN 3239", layout="centered")

# Design optimisé pour mobile
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
    """Établit la connexion avec la base SQLite."""
    conn = sqlite3.connect("CCN_3239.db")
    conn.row_factory = sqlite3.Row
    return conn

def afficher_dossier_article(num_racine, lang='FR'):
    """Affiche l'article et ses sous-articles avec gestion bilingue."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Recherche l'article (ex: 139) et ses dérivés (ex: 139-1)
    cursor.execute("""
        SELECT * FROM convention_collective 
        WHERE numero_article_isole = ? 
        OR numero_article_isole LIKE ?
        ORDER BY CAST(numero_article_isole AS INTEGER) ASC
    """, (str(num_racine), str(num_racine) + "-%"))
    
    articles = cursor.fetchall()
    conn.close()

    col_resume = 'texte_simplifie' if lang == 'FR' else 'texte_simplifie_en'

    labels = {
        'FR': {"dossier": "Dossier : Article", "essentiel": "L'essentiel :", "officiel": "Texte officiel", "introuvable": "n'a pas été trouvé."},
        'EN': {"dossier": "File: Article", "essentiel": "Key points:", "officiel": "Official text", "introuvable": "was not found."}
    }
    l = labels[lang]

    if articles:
        st.success(f"### 🎯 {l['dossier']} {num_racine}")
        for art in articles:
            with st.container():
                cols_disponibles = art.keys()
                titre_art = art['affichage_article'] if 'affichage_article' in cols_disponibles else f"Article {art['numero_article_isole']}"
                st.markdown(f"#### 📄 {titre_art}")
                
                if col_resume in cols_disponibles and art[col_resume]:
                    st.info(f"**💡 {l['essentiel']}** {art[col_resume]}")
                else:
                    st.warning(f"Résumé non disponible en {lang}")
                
                with st.expander(f"⚖️ {l['officiel']} ({art['numero_article_isole']})"):
                    st.write(art['texte_integral'])
                st.divider()
    else:
        st.error(f"Article {num_racine} {l['introuvable']}")

# --- INITIALISATION SESSION ---
if 'step' not in st.session_state:
    st.session_state.step = 1
    st.session_state.choix = {}

# Barre latérale : Langue
with st.sidebar:
    st.title("🌐 Language")
    langue = st.radio("Select your language", ("Français", "English"))
    lang_code = 'FR' if langue == "Français" else 'EN'

# Interface Trilingue
UI = {
    'FR': {
        'titre': "⚖️ Guide CCN 3239",
        'recherche_label': "Recherche directe par n° d'article",
        'btn_aller': "Aller",
        'btn_home': "🏠 Accueil",
        'btn_retour': "⬅️ Retour",
        'intro': "**Bienvenue !** 🚀\nTrouvez votre réponse en quelques clics.",
        'step1': "1️⃣ Quel est votre métier ?",
        'step2': "2️⃣ Quel est le moment ?",
        'step3': "3️⃣ Choisissez une catégorie",
        'step4': "4️⃣ Précisez votre sujet",
        'step5': "5️⃣ Quelle est votre question ?",
        'metiers': {
            "🍼 Assistant Maternel": "art_am", 
            "👶 Assistant Parental": "art_ef", 
            "🏠 Employé Familial": "art_ef", 
            "👵 Assistant de Vie": "art_ef", 
            "🌳 Autres": "art_sc"
        }
    },
    'EN': {
        'titre': "⚖️ 3239 Agreement Guide",
        'recherche_label': "Direct search (Article #)",
        'btn_aller': "Go",
        'btn_home': "🏠 Home",
        'btn_retour': "⬅️ Back",
        'intro': "**Welcome!** 🚀\nFind your answer in a few clicks.",
        'step1': "1️⃣ What is your job?",
        'step2': "2️⃣ What is the timing?",
        'step3': "3️⃣ Choose a category",
        'step4': "4️⃣ Specify your subject",
        'step5': "5️⃣ What is your question?",
        'metiers': {
            "🍼 Childminder": "art_am", 
            "👶 Nanny / Parental Asst": "art_ef", 
            "🏠 Domestic Worker": "art_ef", 
            "👵 Care Assistant": "art_ef", 
            "🌳 Others": "art_sc"
        }
    }
}

txt = UI[lang_code]
st.title(txt['titre'])

# Recherche rapide
with st.expander(f"🔍 {txt['recherche_label']}"):
    col1, col2 = st.columns([3, 1])
    with col1:
        art_direct = st.text_input("Ex: 139", key="search_input", label_visibility="collapsed")
    with col2:
        if st.button(txt['btn_aller']):
            if art_direct:
                st.session_state.step = "DIRECT"
                st.session_state.art_cible = art_direct
                st.rerun()

if st.session_state.step != 1:
    if st.button(txt['btn_home']):
        st.session_state.step = 1
        st.session_state.choix = {}
        st.rerun()

st.divider()

# --- LOGIQUE DE L'ENTONNOIR ---

if st.session_state.step == "DIRECT":
    afficher_dossier_article(st.session_state.art_cible, lang_code)

elif st.session_state.step == 1:
    st.info(txt['intro'])
    st.subheader(txt['step1'])
    for label, col in txt['metiers'].items():
        if st.button(label):
            st.session_state.choix['colonne_metier'] = col
            st.session_state.step = 2
            st.rerun()

elif st.session_state.step == 2:
    st.subheader(txt['step2'])
    conn = get_connection(); cursor = conn.cursor()
    col_db = "etape_vie" if lang_code == 'FR' else "etape_vie_en"
    cursor.execute(f"SELECT DISTINCT {col_db} FROM questions WHERE {col_db} IS NOT NULL AND {col_db} != ''")
    etapes = [r[0] for r in cursor.fetchall()]; conn.close()
    for e in etapes:
        if st.button(e):
            st.session_state.choix['etape_val'] = e
            st.session_state.step = 3
            st.rerun()
    if st.button(txt['btn_retour']): st.session_state.step = 1; st.rerun()

elif st.session_state.step == 3:
    st.subheader(txt['step3'])
    conn = get_connection(); cursor = conn.cursor()
    col_famille = "famille" if lang_code == 'FR' else "famille_en"
    col_etape = "etape_vie" if lang_code == 'FR' else "etape_vie_en"
    cursor.execute(f"SELECT DISTINCT {col_famille} FROM questions WHERE {col_etape} = ?", (st.session_state.choix['etape_val'],))
    familles = [r[0] for r in cursor.fetchall() if r[0]]; conn.close()
    for f in familles:
        if st.button(f):
            st.session_state.choix['famille_val'] = f
            st.session_state.step = 4
            st.rerun()
    if st.button(txt['btn_retour']): st.session_state.step = 2; st.rerun()

elif st.session_state.step == 4:
    st.subheader(txt['step4'])
    conn = get_connection(); cursor = conn.cursor()
    # CORRECTION TRADUCTION THEME
    col_theme = "theme" if lang_code == 'FR' else "theme_en"
    col_famille = "famille" if lang_code == 'FR' else "famille_en"
    cursor.execute(f"SELECT DISTINCT {col_theme} FROM questions WHERE {col_famille} = ?", (st.session_state.choix['famille_val'],))
    themes = [r[0] for r in cursor.fetchall() if r[0]]; conn.close()
    for t in themes:
        if st.button(t):
            st.session_state.choix['theme'] = t
            st.session_state.step = 5
            st.rerun()
    if st.button(txt['btn_retour']): st.session_state.step = 3; st.rerun()

elif st.session_state.step == 5:
    st.subheader(txt['step5'])
    conn = get_connection(); cursor = conn.cursor()
    col_q = "question_claire" if lang_code == 'FR' else "question_en"
    # On cherche en fonction du thème sélectionné (qui est déjà dans la bonne langue)
    col_theme = "theme" if lang_code == 'FR' else "theme_en"
    cursor.execute(f"SELECT id, {col_q} FROM questions WHERE {col_theme} = ?", (st.session_state.choix['theme'],))
    questions = cursor.fetchall(); conn.close()
    for q in questions:
        if st.button(q[col_q]):
            st.session_state.choix['id_question'] = q['id']
            st.session_state.step = 6
            st.rerun()
    if st.button(txt['btn_retour']): st.session_state.step = 4; st.rerun()

elif st.session_state.step == 6:
    conn = get_connection(); cursor = conn.cursor()
    col_metier = st.session_state.choix['colonne_metier']
    id_q = st.session_state.choix['id_question']
    cursor.execute(f"SELECT {col_metier} FROM questions WHERE id = ?", (id_q,))
    res = cursor.fetchone()
    conn.close()
    if res and res[0]:
        # Simple conversion string car la base est maintenant propre (TEXT)
        article_propre = str(res[0]).strip()
        afficher_dossier_article(article_propre, lang_code)
    else:
        st.warning("⚠️ Article non renseigné pour ce profil.")
    if st.button(txt['btn_retour']): st.session_state.step = 5; st.rerun()
