import streamlit as st
import sqlite3
import os

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Assistant CCN 3239", layout="centered")

# --- 2. DESIGN & FORÇAGE DE L'ALIGNEMENT (CSS) ---
# Ce bloc règle vos problèmes d'affichage sur mobile (portrait/paysage)
st.markdown("""
    <style>
    /* FORÇAGE HORIZONTAL : Empêche l'empilement des colonnes sur mobile */
    [data-testid="stHorizontalBlock"] > div {
        flex-direction: row !important;
        display: flex !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* Partage équitable de l'espace pour les colonnes de drapeaux */
    [data-testid="column"] {
        flex: 1 1 auto !important;
        width: 50% !important;
    }

    /* STYLE DES BOUTONS DRAPEAUX (Sans cadre, sans ombre) */
    div.stButton > button[key^="lang_"] {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        background: transparent !important;
        padding: 0px !important;
        margin: 0 auto !important;
        display: block !important;
        font-size: 40px !important;
    }

    /* Neutralisation des effets au clic pour les drapeaux */
    div.stButton > button[key^="lang_"]:focus,
    div.stButton > button[key^="lang_"]:active,
    div.stButton > button[key^="lang_"]:hover {
        border: none !important;
        outline: none !important;
        background: transparent !important;
        box-shadow: none !important;
    }

    /* BADGE DU SOCLE : Largeur pleine, centré sous les drapeaux */
    .socle-badge {
        background-color: #f0f2f6;
        border: 1px solid #d1d5db; 
        border-radius: 10px;
        text-align: center; 
        font-size: 16px !important; 
        font-weight: bold;
        color: #000000 !important;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%; 
        margin-top: 10px;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.05);
    }

    /* STYLE DES BOUTONS DE NAVIGATION CLASSIQUES */
    div.stButton > button:not([key^="lang_"]) {
        width: 100%;
        height: 55px;
        border-radius: 12px;
        background-color: #FFFFFF !important; 
        color: #000000 !important;           
        border: 1px solid #E0E0E0 !important;
    }
    
    .stTextInput > div > div > input {
        color: #000000 !important;
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
    # Recherche l'article exact ou ses sous-sections (ex: 139 et 139-1)
    cursor.execute("""
        SELECT * FROM convention_collective 
        WHERE numero_article_isole = ? 
        OR numero_article_isole LIKE ?
        ORDER BY CAST(numero_article_isole AS INTEGER) ASC
    """, (str(num_racine), str(num_racine) + "-%"))
    articles = cursor.fetchall()
    conn.close()

    labels = {
        'FR': {"d": "Dossier : Article", "e": "L'essentiel :", "o": "Texte officiel"},
        'EN': {"d": "File: Article", "e": "Key points:", "o": "Official text"}
    }
    l = labels[lang]

    if articles:
        st.success(f"### 🎯 {l['d']} {num_racine}")
        for art in articles:
            st.markdown(f"#### 📄 {art['affichage_article']}")
            col_res = 'texte_simplifie' if lang == 'FR' else 'texte_simplifie_en'
            if art[col_res]:
                st.info(f"**💡 {l['e']}** {art[col_res]}")
            with st.expander(f"⚖️ {l['o']}"):
                st.write(art['texte_integral'])
            st.divider()

# --- 4. INITIALISATION DE LA SESSION ---
if 'step' not in st.session_state:
    st.session_state.step = 1
    st.session_state.choix = {}
if 'langue_choisie' not in st.session_state:
    st.session_state.langue_choisie = "Français"

# --- 5. DICTIONNAIRE D'INTERFACE (MULTI-LANGUE) ---
UI = {
    'FR': {
        'titre': "⚖️ Guide CCN 3239",
        'recherche': "Recherche directe par n° d'article",
        'btn_home': "🏠 Accueil",
        'socles': {"art_am": "Socle ASSMAT", "art_ef": "Socle SPE", "art_sc": "Socle commun"}
    },
    'EN': {
        'titre': "⚖️ 3239 Agreement Guide",
        'recherche': "Direct search (Article #)",
        'btn_home': "🏠 Home",
        'socles': {"art_am": "ASSMAT Socle", "art_ef": "SPE Socle", "art_sc": "Common Socle"}
    }
}

lang_code = 'FR' if st.session_state.langue_choisie == "Français" else 'EN'
txt = UI[lang_code]

# --- 6. BARRE DE NAVIGATION SUPÉRIEURE (DRAPEAUX & SOCLE) ---
# Ligne 1 : Drapeaux
c1, c2 = st.columns(2)
with c1:
    if st.button("🇫🇷", key="lang_fr"):
        st.session_state.langue_choisie = "Français"
        st.rerun()
with c2:
    if st.button("🇬🇧", key="lang_en"):
        st.session_state.langue_choisie = "English"
        st.rerun()

# Ligne 2 : Badge du Socle dynamique
if 'colonne_metier' in st.session_state.choix:
    nom_socle = txt['socles'].get(st.session_state.choix['colonne_metier'], "")
    st.markdown(f'<div class="socle-badge">{nom_socle}</div>', unsafe_allow_html=True)
else:
    msg = "Choisissez un métier" if lang_code == 'FR' else "Choose a job"
    st.markdown(f'<div class="socle-badge">{msg}</div>', unsafe_allow_html=True)

st.title(txt['titre'])

# --- 7. SYSTÈME DE RECHERCHE DIRECTE ---
with st.expander(f"🔍 {txt['recherche']}"):
    col_in, col_go = st.columns([3, 1])
    with col_in:
        art_num = st.text_input("Ex: 139", key="search_bar", label_visibility="collapsed")
    with col_go:
        if st.button("OK"):
            st.session_state.step = "DIRECT"; st.session_state.art_target = art_num; st.rerun()

# --- 8. LOGIQUE DE NAVIGATION (TUNNEL DE QUESTIONS) ---
if st.session_state.step != 1:
    if st.button(txt['btn_home']):
        st.session_state.step = 1; st.session_state.choix = {}; st.rerun()

st.divider()

if st.session_state.step == "DIRECT":
    afficher_dossier_article(st.session_state.art_target, lang_code)

elif st.session_state.step == 1:
    st.subheader("1️⃣ Métier ?")
    # Simulation des boutons métiers (à lier à votre table questions)
    if st.button("🍼 Assistant Maternel"):
        st.session_state.choix['colonne_metier'] = "art_am"
        st.session_state.step = 2; st.rerun()
    # Ajoutez ici les autres métiers...

elif st.session_state.step == 2:
    st.subheader("2️⃣ Étape ?")
    # Logique SQL pour récupérer les étapes...
