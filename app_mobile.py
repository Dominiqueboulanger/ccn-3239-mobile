import streamlit as st
import sqlite3

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Assistant CCN 3239", layout="centered")

# --- 2. DESIGN & FORÇAGE ALIGNEMENT ---
st.markdown("""
    <style>
    /* FORCE L'ALIGNEMENT HORIZONTAL DES COLONNES (Ligne 1) */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important; /* Interdit le passage à la ligne */
        align-items: center !important;
        justify-content: center !important;
    }

    /* Ajustement individuel des colonnes pour qu'elles ne prennent que l'espace nécessaire */
    [data-testid="column"] {
        flex: 0 1 auto !important;
        min-width: fit-content !important;
    }

    /* Style des boutons drapeaux (Nettoyage complet) */
    div.stButton > button[key^="lang_"] {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        background: transparent !important;
        padding: 0px 10px !important;
        height: 50px !important;
        width: 60px !important;
        font-size: 35px !important;
    }
    
    /* Suppression des effets au clic pour les drapeaux */
    div.stButton > button[key^="lang_"]:hover, 
    div.stButton > button[key^="lang_"]:active, 
    div.stButton > button[key^="lang_"]:focus {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        background: transparent !important;
    }

    /* Badge du Socle : Centré sur sa propre ligne */
    .socle-badge {
        background-color: #f0f2f6;
        border: 1px solid #d1d5db; 
        border-radius: 10px;
        text-align: center; 
        font-size: 16px !important; 
        font-weight: bold;
        color: #000000 !important;
        height: 45px;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%; 
        margin-top: 5px;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.05);
    }

    /* Style général des boutons de menu */
    div.stButton > button:not([key^="lang_"]) {
        width: 100%;
        height: 55px;
        border-radius: 12px;
        background-color: #FFFFFF !important; 
        color: #000000 !important;           
        border: 1px solid #E0E0E0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# (Gardez vos fonctions get_connection et afficher_dossier_article ici...)

# --- INITIALISATION SESSION ---
if 'step' not in st.session_state:
    st.session_state.step = 1
    st.session_state.choix = {}
if 'langue_choisie' not in st.session_state:
    st.session_state.langue_choisie = "Français"

# --- INTERFACE ---
lang_code = 'FR' if st.session_state.langue_choisie == "Français" else 'EN'

# --- LIGNE 1 : LES DRAPEAUX (FORCÉS CÔTE À CÔTE) ---
col1, col2 = st.columns(2)
with col1:
    if st.button("🇫🇷", key="lang_fr"):
        st.session_state.langue_choisie = "Français"
        st.rerun()
with col2:
    if st.button("🇬🇧", key="lang_en"):
        st.session_state.langue_choisie = "English"
        st.rerun()

# --- LIGNE 2 : LE BADGE (CENTRÉ EN DESSOUS) ---
# Dictionnaire simplifié pour l'exemple
socles = {"art_am": "Socle ASSMAT", "art_ef": "Socle SPE", "art_sc": "Socle commun"}
if 'colonne_metier' in st.session_state.choix:
    nom = socles.get(st.session_state.choix['colonne_metier'], "")
    st.markdown(f'<div class="socle-badge">{nom}</div>', unsafe_allow_html=True)
else:
    label = "Choisissez un métier" if lang_code == 'FR' else "Choose a job"
    st.markdown(f'<div class="socle-badge">{label}</div>', unsafe_allow_html=True)

st.title("⚖️ Guide CCN 3239" if lang_code == 'FR' else "⚖️ 3239 Agreement Guide")
st.divider()

# (... Suite de votre logique de navigation)
