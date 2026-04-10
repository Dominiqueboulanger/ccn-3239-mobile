import streamlit as st
import sqlite3
import os

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Assistant CCN 3239", layout="centered")

# --- 2. DESIGN (BANDEAU FIXE + STYLE BOUTONS) ---
st.markdown("""
    <style>
    /* Style général des boutons (Texte sombre sur fond blanc) */
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
    
    /* Style spécifique pour les DRAPEAUX (Transparent et aligné) */
    div.stButton > button[key^="lang_"] {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        background: transparent !important;
        padding: 0px !important;
        margin: 0 auto !important;
        display: block !important;
        font-size: 35px !important;
        height: 50px !important;
        width: 50px !important;
    }

    /* LE BANDEAU FIXE (Modifié pour accueillir le selectbox) */
    .sticky-header {
        position: -webkit-sticky;
        position: sticky;
        top: 0;
        background-color: #f0f2f6;
        z-index: 1000;
        padding: 10px 20px;
        border-bottom: 2px solid #d1d5db;
        border-radius: 0 0 10px 10px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }

    /* Forçage horizontal pour les drapeaux */
    [data-testid="stHorizontalBlock"] > div {
        flex-direction: row !important;
        display: flex !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* Ajustement du label du menu déroulant dans le bandeau */
    .stSelectbox label {
        display: none; /* Cache le label pour gagner de la place */
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. GESTION BASE DE DONNÉES ---
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
    col_res = 'texte_simplifie' if lang == 'FR' else 'texte_simplifie_en'
    if articles:
        st.success(f"### 🎯 Article {num_racine}")
        for art in articles:
            st.markdown(f"#### 📄 {art['affichage_article']}")
            if art[col_res]: st.info(f"**💡 L'essentiel :** {art[col_res]}")
            with st.expander("⚖️ Texte officiel"):
                st.write(art['texte_integral'])
            st.divider()

# --- 4. INITIALISATION SESSION ---
if 'step' not in st.session_state:
    st.session_state.step = 1
    st.session_state.choix = {}
if 'langue_choisie' not in st.session_state:
    st.session_state.langue_choisie = "Français"

# --- 5. BANDEAU FIXE AVEC MENU DÉROULANT ---

# Définition des métiers et socles associés
metiers_data = {
    "Français": {
        "Choisir un métier...": None,
        "🍼 Assistant Maternel": "art_am",
        "👶 Assistant Parental": "art_ef",
        "🏠 Employé Familial": "art_ef",
        "👵 Assistant de Vie": "art_ef",
        "🌳 Autres (Socle commun)": "art_sc"
    },
    "English": {
        "Choose a job...": None,
        "🍼 Childminder": "art_am",
        "👶 Nanny": "art_ef",
        "🏠 Domestic Worker": "art_ef",
        "👵 Care Assistant": "art_ef",
        "🌳 Others (Common Socle)": "art_sc"
    }
}

# Affichage du bandeau sticky
with st.container():
    st.markdown('<div class="sticky-header">', unsafe_allow_html=True)
    
    # Choix de la langue (Drapeaux)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🇫🇷", key="lang_fr"):
            st.session_state.langue_choisie = "Français"; st.rerun()
    with c2:
        if st.button("🇬🇧", key="lang_en"):
            st.session_state.langue_choisie = "English"; st.rerun()
    
    # Menu déroulant des métiers
    options_metiers = list(metiers_data[st.session_state.langue_choisie].keys())
    
    # On cherche l'index actuel si déjà choisi
    current_index = 0
    if 'metier_label' in st.session_state.choix:
        if st.session_state.choix['metier_label'] in options_metiers:
            current_index = options_metiers.index(st.session_state.choix['metier_label'])

    selected_metier = st.selectbox(
        "Métier", 
        options=options_metiers, 
        index=current_index,
        key="metier_selector"
    )
    
    # Logique de mise à jour suite au changement de métier
    if metiers_data[st.session_state.langue_choisie][selected_metier] is not None:
        if st.session_state.choix.get('metier_label') != selected_metier:
            st.session_state.choix['metier_label'] = selected_metier
            st.session_state.choix['colonne_metier'] = metiers_data[st.session_state.langue_choisie][selected_metier]
            st.session_state.step = 2 # Passe directement à l'étape "Moment"
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)

# --- 6. LOGIQUE DE NAVIGATION ---
lang_code = 'FR' if st.session_state.langue_choisie == "Français" else 'EN'
UI = {
    'FR': {'titre': "⚖️ Guide CCN 3239", 'home': "🏠 Accueil", 'search': "Recherche n° article"},
    'EN': {'titre': "⚖️ 3239 Agreement Guide", 'home': "🏠 Home", 'search': "Search article #"}
}
txt = UI[lang_code]

st.title(txt['titre'])

# Recherche rapide
with st.expander(f"🔍 {txt['search']}"):
    ci, cb = st.columns([3, 1])
    with ci: art_in = st.text_input("Ex: 139", key="s_in", label_visibility="collapsed")
    with cb: 
        if st.button("OK"): 
            st.session_state.step = "DIRECT"; st.session_state.art_cible = art_in; st.rerun()

if st.session_state.step != 1:
    if st.button(txt['home']):
        st.session_state.step = 1; st.session_state.choix = {}; st.rerun()

st.divider()

# --- AFFICHAGE DES ÉTAPES ---
if st.session_state.step == "DIRECT":
    afficher_dossier_article(st.session_state.art_cible, lang_code)

elif st.session_state.step == 1:
    st.info("👋 Bienvenue ! Utilisez le menu en haut pour choisir votre métier et commencer." if lang_code == 'FR' else "👋 Welcome! Use the menu above to choose your job and start.")

elif st.session_state.step == 2:
    st.subheader("2️⃣ Quel est le moment ?" if lang_code == 'FR' else "2️⃣ What is the timing?")
    # Ici votre code SQL pour récupérer les étapes de vie...
    # (Exemple simplifié)
    if st.button("Embauche"): st.session_state.step = 3; st.rerun()
