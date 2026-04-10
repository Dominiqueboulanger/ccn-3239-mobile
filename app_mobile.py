import streamlit as st
import sqlite3
import os

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Assistant CCN 3239", layout="centered")

# --- 2. DESIGN (VERSION INITIALE + CORRECTIF DRAPEAUX) ---
st.markdown("""
    <style>
    /* Style initial des boutons */
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
    
    /* STYLE SPÉCIFIQUE POUR LES DRAPEAUX (En haut) */
    div.stButton > button[key^="lang_"] {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        font-size: 35px !important;
        height: 50px !important;
    }

    /* Forçage de l'alignement horizontal pour les colonnes des drapeaux */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
    }

    .stTextInput > div > div > input {
        height: 50px;
        font-size: 18px;
        color: #1e293b !important;
        background-color: #FFFFFF !important;
    }

    h1, h2, h3, h4 { color: #2c3e50; }
    .stInfo, .stSuccess { color: #1e293b !important; }
    </style>
    """, unsafe_allow_html=True)

def get_connection():
    conn = sqlite3.connect("CCN_3239.db")
    conn.row_factory = sqlite3.Row
    return conn

# --- 3. FONCTION D'AFFICHAGE ---
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

# --- 5. BANDEAU DE NAVIGATION (DRAPEAUX + MENU MÉTIER) ---
col_l1, col_l2 = st.columns(2)
with col_l1:
    if st.button("🇫🇷", key="lang_fr"):
        st.session_state.langue_choisie = "Français"; st.rerun()
with col_l2:
    if st.button("🇬🇧", key="lang_en"):
        st.session_state.langue_choisie = "English"; st.rerun()

# Menu déroulant pour le métier (Remplace l'étape 1)
metiers_dict = {
    "Français": {
        "Choisir un métier...": None,
        "🍼 Assistant Maternel": "art_am",
        "👶 Assistant Parental": "art_ef",
        "🏠 Employé Familial": "art_ef",
        "👵 Assistant de Vie": "art_ef",
        "🌳 Autres": "art_sc"
    },
    "English": {
        "Choose a job...": None,
        "🍼 Childminder": "art_am",
        "👶 Nanny": "art_ef",
        "🏠 Domestic Worker": "art_ef",
        "👵 Care Assistant": "art_ef",
        "🌳 Others": "art_sc"
    }
}

options = list(metiers_dict[st.session_state.langue_choisie].keys())
index_m = 0
if 'metier_label' in st.session_state.choix:
    if st.session_state.choix['metier_label'] in options:
        index_m = options.index(st.session_state.choix['metier_label'])

selected = st.selectbox("Votre métier :", options=options, index=index_m)

# Si un métier est sélectionné, on met à jour la session
if metiers_dict[st.session_state.langue_choisie][selected] is not None:
    if st.session_state.choix.get('metier_label') != selected:
        st.session_state.choix['metier_label'] = selected
        st.session_state.choix['colonne_metier'] = metiers_dict[st.session_state.langue_choisie][selected]
        st.session_state.step = 2 # On passe à la suite
        st.rerun()

lang_code = 'FR' if st.session_state.langue_choisie == "Français" else 'EN'

# --- 6. DICTIONNAIRE D'INTERFACE ---
UI = {
    'FR': {
        'titre': "⚖️ Guide CCN 3239", 'recherche_label': "Recherche directe par n° d'article",
        'btn_aller': "Aller", 'btn_home': "🏠 Accueil", 'btn_retour': "⬅️ Retour",
        'step2': "2️⃣ Quel est le moment ?", 'step3': "3️⃣ Choisissez une catégorie",
        'step4': "4️⃣ Précisez votre sujet", 'step5': "5️⃣ Quelle est votre question ?"
    },
    'EN': {
        'titre': "⚖️ 3239 Agreement Guide", 'recherche_label': "Direct search (Article #)",
        'btn_aller': "Go", 'btn_home': "🏠 Home", 'btn_retour': "⬅️ Back",
        'step2': "2️⃣ What is the timing?", 'step3': "3️⃣ Choose a category",
        'step4': "4️⃣ Specify your subject", 'step5': "5️⃣ What is your question?"
    }
}
txt = UI[lang_code]
st.title(txt['titre'])

# --- 7. RECHERCHE RAPIDE ---
with st.expander(f"🔍 {txt['recherche_label']}"):
    col1, col2 = st.columns([3, 1])
    with col1:
        art_direct = st.text_input("Ex: 139", key="search_input", label_visibility="collapsed")
    with col2:
        if st.button(txt['btn_aller'], key="go_search"):
            if art_direct:
                st.session_state.step = "DIRECT"; st.session_state.art_cible = art_direct; st.rerun()

if st.session_state.step != 1:
    if st.button(txt['btn_home'], key="home_main"):
        st.session_state.step = 1; st.session_state.choix = {}; st.rerun()

st.divider()

# --- 8. LOGIQUE DE NAVIGATION ---
if st.session_state.step == "DIRECT":
    afficher_dossier_article(st.session_state.art_cible, lang_code)

elif st.session_state.step == 1:
    st.info("👋 Bienvenue ! Veuillez sélectionner votre métier dans le menu ci-dessus pour commencer." if lang_code == 'FR' else "👋 Welcome! Please select your job in the menu above to start.")

elif st.session_state.step == 2:
    st.subheader(txt['step2'])
    conn = get_connection(); cursor = conn.cursor()
    col_db = "etape_vie" if lang_code == 'FR' else "etape_vie_en"
    cursor.execute(f"SELECT DISTINCT {col_db} FROM questions WHERE {col_db} IS NOT NULL AND {col_db} != ''")
    etapes = [r[0] for r in cursor.fetchall()]; conn.close()
    for e in etapes:
        if st.button(e):
            st.session_state.choix['etape_val'] = e; st.session_state.step = 3; st.rerun()

elif st.session_state.step == 3:
    st.subheader(txt['step3'])
    conn = get_connection(); cursor = conn.cursor()
    col_fam = "famille" if lang_code == 'FR' else "famille_en"
    cursor.execute(f"SELECT DISTINCT {col_fam} FROM questions WHERE etape_vie = ?", (st.session_state.choix['etape_val'],))
    familles = [r[0] for r in cursor.fetchall() if r[0]]; conn.close()
    for f in familles:
        if st.button(f):
            st.session_state.choix['famille_val'] = f; st.session_state.step = 4; st.rerun()
    if st.button(txt['btn_retour']): st.session_state.step = 2; st.rerun()

# ... (Continuez avec les étapes 4, 5 et 6 comme dans votre code initial)
