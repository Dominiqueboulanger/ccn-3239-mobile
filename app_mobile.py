import streamlit as st
import sqlite3
import os

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Assistant CCN 3239", layout="centered")

# --- 2. DESIGN (FUSION BOUTONS BLANCS + CORRECTIF MOBILE DRAPEAUX) ---
st.markdown("""
    <style>
    /* 1. Style général des boutons (Texte noir sur fond blanc) */
    div.stButton > button {
        width: 100%;
        height: 60px;
        font-size: 18px;
        border-radius: 12px;
        margin-bottom: 10px;
        background-color: #FFFFFF !important; 
        color: #1e293b !important;           
        border: 2px solid #E0E0E0 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* 2. Visibilité du texte saisi */
    .stTextInput > div > div > input {
        height: 50px;
        font-size: 18px;
        color: #1e293b !important;
        background-color: #FFFFFF !important;
    }

    /* 3. Couleurs de texte pour titres et blocs */
    h1, h2, h3, h4 { color: #2c3e50; }
    .stInfo, .stSuccess { color: #1e293b !important; }

    /* --- CORRECTIF SPÉCIFIQUE DRAPEAUX & MOBILE --- */
    
    /* Force l'alignement horizontal des colonnes même en mode portrait sur iPhone */
    [data-testid="stHorizontalBlock"] > div {
        flex-direction: row !important;
        display: flex !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* Style spécifique pour les boutons drapeaux (Neutralisation du style général) */
    div.stButton > button[key^="lang_"] {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        background: transparent !important;
        padding: 0px !important;
        margin: 0 auto !important;
        display: block !important;
        font-size: 40px !important;
        height: auto !important;
        width: auto !important;
    }

    /* Suppression des bordures au clic/focus pour les drapeaux */
    div.stButton > button[key^="lang_"]:focus,
    div.stButton > button[key^="lang_"]:active,
    div.stButton > button[key^="lang_"]:hover {
        border: none !important;
        outline: none !important;
        background: transparent !important;
        box-shadow: none !important;
    }

    /* Badge du Socle (Ligne 2) */
    .socle-badge {
        background-color: #f0f2f6;
        border: 1px solid #d1d5db; 
        border-radius: 10px;
        text-align: center; 
        font-size: 16px !important; 
        font-weight: bold;
        color: #1e293b !important;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%; 
        margin-top: 10px;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. GESTION DE LA BASE DE DONNÉES ---
def get_connection():
    conn = sqlite3.connect("CCN_3239.db")
    conn.row_factory = sqlite3.Row
    return conn

def afficher_dossier_article(num_racine, lang='FR'):
    conn = get_connection()
    cursor = conn.cursor()
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
                titre = art['affichage_article'] if 'affichage_article' in art.keys() else f"Article {art['numero_article_isole']}"
                st.markdown(f"#### 📄 {titre}")
                if col_resume in art.keys() and art[col_resume]:
                    st.info(f"**💡 {l['essentiel']}** {art[col_resume]}")
                with st.expander(f"⚖️ {l['officiel']} ({art['numero_article_isole']})"):
                    st.write(art['texte_integral'])
                st.divider()
    else:
        st.error(f"Article {num_racine} {l['introuvable']}")

# --- 4. INITIALISATION SESSION ---
if 'step' not in st.session_state:
    st.session_state.step = 1
    st.session_state.choix = {}
if 'langue_choisie' not in st.session_state:
    st.session_state.langue_choisie = "Français"

# --- 5. INTERFACE SUPÉRIEURE (DRAPEAUX & BADGE) ---
col_l1, col_l2 = st.columns(2)
with col_l1:
    if st.button("🇫🇷", key="lang_fr"):
        st.session_state.langue_choisie = "Français"
        st.rerun()
with col_l2:
    if st.button("🇬🇧", key="lang_en"):
        st.session_state.langue_choisie = "English"
        st.rerun()

lang_code = 'FR' if st.session_state.langue_choisie == "Français" else 'EN'

# Dictionnaire pour l'interface
UI = {
    'FR': {
        'titre': "⚖️ Guide CCN 3239",
        'recherche_label': "Recherche directe par n° d'article",
        'btn_aller': "Aller", 'btn_home': "🏠 Accueil", 'btn_retour': "⬅️ Retour",
        'intro': "**Bienvenue !** 🚀\nTrouvez votre réponse en quelques clics.",
        'step1': "1️⃣ Quel est votre métier ?",
        'metiers': {
            "🍼 Assistant Maternel": "art_am", "👶 Assistant Parental": "art_ef", 
            "🏠 Employé Familial": "art_ef", "👵 Assistant de Vie": "art_ef", "🌳 Autres": "art_sc"
        },
        'socles': {"art_am": "Socle ASSMAT", "art_ef": "Socle SPE", "art_sc": "Socle commun"}
    },
    'EN': {
        'titre': "⚖️ 3239 Agreement Guide",
        'recherche_label': "Direct search (Article #)",
        'btn_aller': "Go", 'btn_home': "🏠 Home", 'btn_retour': "⬅️ Back",
        'intro': "**Welcome!** 🚀\nFind your answer in a few clicks.",
        'step1': "1️⃣ What is your job?",
        'metiers': {
            "🍼 Childminder": "art_am", "👶 Nanny": "art_ef", 
            "🏠 Domestic Worker": "art_ef", "👵 Care Assistant": "art_ef", "🌳 Others": "art_sc"
        },
        'socles': {"art_am": "ASSMAT Socle", "art_ef": "SPE Socle", "art_sc": "Common Socle"}
    }
}
txt = UI[lang_code]

# Affichage du badge du socle (Ligne 2)
if 'colonne_metier' in st.session_state.choix:
    nom_socle = txt['socles'].get(st.session_state.choix['colonne_metier'], "")
    st.markdown(f'<div class="socle-badge">{nom_socle}</div>', unsafe_allow_html=True)
else:
    msg = "Choisissez un métier" if lang_code == 'FR' else "Choose a job"
    st.markdown(f'<div class="socle-badge">{msg}</div>', unsafe_allow_html=True)

st.title(txt['titre'])

# --- 6. RECHERCHE RAPIDE ---
with st.expander(f"🔍 {txt['recherche_label']}"):
    c_in, c_bt = st.columns([3, 1])
    with c_in:
        art_direct = st.text_input("Ex: 139", key="search_input", label_visibility="collapsed")
    with c_bt:
        if st.button(txt['btn_aller'], key="btn_go_direct"):
            if art_direct:
                st.session_state.step = "DIRECT"; st.session_state.art_cible = art_direct; st.rerun()

if st.session_state.step != 1:
    if st.button(txt['btn_home'], key="btn_home_nav"):
        st.session_state.step = 1; st.session_state.choix = {}; st.rerun()

st.divider()

# --- 7. LOGIQUE DE NAVIGATION ---
if st.session_state.step == "DIRECT":
    afficher_dossier_article(st.session_state.art_cible, lang_code)

elif st.session_state.step == 1:
    st.info(txt['intro'])
    st.subheader(txt['step1'])
    for label, col in txt['metiers'].items():
        if st.button(label):
            st.session_state.choix['colonne_metier'] = col
            st.session_state.step = 2; st.rerun()

elif st.session_state.step == 2:
    st.subheader("2️⃣ Quel est le moment ?" if lang_code == 'FR' else "2️⃣ What is the timing?")
    conn = get_connection(); cursor = conn.cursor()
    col_db = "etape_vie" if lang_code == 'FR' else "etape_vie_en"
    cursor.execute(f"SELECT DISTINCT {col_db} FROM questions WHERE {col_db} IS NOT NULL AND {col_db} != ''")
    etapes = [r[0] for r in cursor.fetchall()]; conn.close()
    for e in etapes:
        if st.button(e):
            st.session_state.choix['etape_val'] = e; st.session_state.step = 3; st.rerun()
    if st.button(txt['btn_retour']): st.session_state.step = 1; st.rerun()

elif st.session_state.step == 3:
    st.subheader("3️⃣ Choisissez une catégorie" if lang_code == 'FR' else "3️⃣ Choose a category")
    conn = get_connection(); cursor = conn.cursor()
    col_fam = "famille" if lang_code == 'FR' else "famille_en"
    col_etp = "etape_vie" if lang_code == 'FR' else "etape_vie_en"
    cursor.execute(f"SELECT DISTINCT {col_fam} FROM questions WHERE {col_etp} = ?", (st.session_state.choix['etape_val'],))
    familles = [r[0] for r in cursor.fetchall() if r[0]]; conn.close()
    for f in familles:
        if st.button(f):
            st.session_state.choix['famille_val'] = f; st.session_state.step = 4; st.rerun()
    if st.button(txt['btn_retour']): st.session_state.step = 2; st.rerun()

elif st.session_state.step == 4:
    st.subheader("4️⃣ Précisez votre sujet" if lang_code == 'FR' else "4️⃣ Specify your subject")
    conn = get_connection(); cursor = conn.cursor()
    col_th = "theme" if lang_code == 'FR' else "theme_en"
    col_fam = "famille" if lang_code == 'FR' else "famille_en"
    cursor.execute(f"SELECT DISTINCT {col_th} FROM questions WHERE {col_fam} = ?", (st.session_state.choix['famille_val'],))
    themes = [r[0] for r in cursor.fetchall() if r[0]]; conn.close()
    for t in themes:
        if st.button(t):
            st.session_state.choix['theme'] = t; st.session_state.step = 5; st.rerun()
    if st.button(txt['btn_retour']): st.session_state.step = 3; st.rerun()

elif st.session_state.step == 5:
    st.subheader("5️⃣ Quelle est votre question ?" if lang_code == 'FR' else "5️⃣ What is your question?")
    conn = get_connection(); cursor = conn.cursor()
    col_q = "question_claire" if lang_code == 'FR' else "question_en"
    col_th = "theme" if lang_code == 'FR' else "theme_en"
    cursor.execute(f"SELECT id, {col_q} FROM questions WHERE {col_th} = ?", (st.session_state.choix['theme'],))
    questions = cursor.fetchall(); conn.close()
    for q in questions:
        if st.button(q[col_q]):
            st.session_state.choix['id_question'] = q['id']; st.session_state.step = 6; st.rerun()
    if st.button(txt['btn_retour']): st.session_state.step = 4; st.rerun()

elif st.session_state.step == 6:
    conn = get_connection(); cursor = conn.cursor()
    col_metier = st.session_state.choix['colonne_metier']
    id_q = st.session_state.choix['id_question']
    cursor.execute(f"SELECT {col_metier} FROM questions WHERE id = ?", (id_q,))
    res = cursor.fetchone(); conn.close()
    if res and res[0]:
        afficher_dossier_article(str(res[0]).strip(), lang_code)
    else:
        st.warning("⚠️ Article non renseigné.")
    if st.button(txt['btn_retour']): st.session_state.step = 5; st.rerun()
