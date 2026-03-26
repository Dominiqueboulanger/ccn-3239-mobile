import streamlit as st
import sqlite3
from pathlib import Path

# --- CONFIGURATION ---
st.set_page_config(page_title="CCN 3239 - Parcours Apprenant", layout="centered")

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "CCN_3239.db"

def get_connection():
    return sqlite3.connect(str(DB_PATH))

# --- STYLE CSS MOBILE ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.8em; font-weight: bold; margin-bottom: 10px; border: 2px solid #1e3799; white-space: normal; }
    .question-box { background-color: #f8f9fa; padding: 20px; border-radius: 15px; border-left: 8px solid #1e3799; margin-bottom: 20px; }
    .essentiel-box { background-color: #ecfdf5; border-left: 5px solid #27ae60; padding: 15px; border-radius: 10px; font-size: 17px; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION ---
if 'etape' not in st.session_state:
    st.session_state.etape = 1
    st.session_state.choix = {}

st.title("🛡️ Assistant CCN 3239")

conn = get_connection()

try:
    # ETAPE 1 : LE MÉTIER (5 OPTIONS)
    if st.session_state.etape == 1:
        st.markdown("<div class='question-box'><h3>1. Quel est votre métier ?</h3></div>", unsafe_allow_html=True)
        metiers = {
            "🧸 Assistant Maternel": "SOCLE ASSISTANT MATERNEL",
            "👶 Assistant Parental (Garde d'enfants)": "SOCLE SALARIÉ DU PARTICULIER EMPLOYEUR",
            "🏠 Employé Familial": "SOCLE SALARIÉ DU PARTICULIER EMPLOYEUR",
            "👴 Assistant de Vie (Dépendance)": "SOCLE SALARIÉ DU PARTICULIER EMPLOYEUR",
            "🛠 Autres (Socle Commun)": "DISPOSITIONS COMMUNES"
        }
        for label, socle_val in metiers.items():
            if st.button(label):
                st.session_state.choix['socle'] = socle_val
                st.session_state.choix['metier_label'] = label
                st.session_state.etape = 2
                st.rerun()

    # ETAPE 2 : VIE OU RUPTURE (Partie IV)
    elif st.session_state.etape == 2:
        st.markdown(f"<div class='question-box'><h3>2. Phase du contrat</h3><p>Métier : {st.session_state.choix['metier_label']}</p></div>", unsafe_allow_html=True)
        phases = ["Vie du contrat de travail", "Rupture du contrat de travail"]
        for phase in phases:
            if st.button(f"✨ {phase}"):
                st.session_state.choix['theme'] = phase
                st.session_state.etape = 3
                st.rerun()
        if st.button("⬅️ Retour"):
            st.session_state.etape = 1
            st.rerun()

    # ETAPE 3 : QUESTION PÉDAGOGIQUE (Thèmes de W1.csv)
    elif st.session_state.etape == 3:
        theme_sel = st.session_state.choix['theme']
        st.markdown(f"<div class='question-box'><h3>3. Quel sujet vous questionne ?</h3></div>", unsafe_allow_html=True)
        
        # On filtre les boutons selon le thème (Vie ou Rupture) choisi à l'étape 2
        query = "SELECT reponse_bouton, articles_lies FROM navigation_pedagogique WHERE theme = ?"
        options = conn.execute(query, (theme_sel,)).fetchall()

        for label, art_id in options:
            if st.button(label):
                st.session_state.choix['article_id'] = art_id
                st.session_state.etape = 4
                st.rerun()
        
        if st.button("⬅️ Retour"):
            st.session_state.etape = 2
            st.rerun()

    # ETAPE 4 : RÉSULTAT FINAL
    elif st.session_state.etape == 4:
        art_id = str(st.session_state.choix['article_id']).strip()
        socle_user = st.session_state.choix['socle']
        
        query = "SELECT affichage_article, texte_integral, texte_simplifie FROM convention_collective WHERE numero_article_isole = ? AND socle = ?"
        res = conn.execute(query, (art_id, socle_user)).fetchone()

        if res:
            titre, integral, simplifie = res
            st.subheader(f"Article {art_id}")
            st.write(f"**{titre}**")
            
            if simplifie and len(simplifie) > 10:
                st.success("💡 L'ESSENTIEL (Niveau A2)")
                st.markdown(f"<div class='essentiel-box'>{simplifie}</div>", unsafe_allow_html=True)
                with st.expander("⚖️ Texte Officiel Intégral"):
                    st.write(integral)
            else:
                st.info("⚖️ TEXTE OFFICIEL")
                st.markdown(f"<div class='essentiel-box'>{integral}</div>", unsafe_allow_html=True)
        else:
            st.warning("Information non spécifique ou article introuvable.")

        if st.button("🔄 Nouvelle recherche"):
            st.session_state.etape = 1
            st.rerun()

finally:
    conn.close()
