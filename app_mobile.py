import streamlit as st
import sqlite3
import os

# Configuration de la page
st.set_page_config(page_title="Assistant CCN 3239", layout="centered")

DB_PATH = "CCN_3239.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

# --- STYLE CSS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; font-weight: bold; margin-bottom: 10px; border: 1px solid #dcdde1; }
    .question-box { background-color: #f8f9fa; padding: 20px; border-radius: 15px; border-left: 5px solid #1e3799; margin-bottom: 20px; }
    .essentiel-box { background-color: #ecfdf5; border-left: 5px solid #27ae60; padding: 15px; border-radius: 10px; font-size: 18px; }
    .titre-art { color: #1e3799; font-weight: bold; font-size: 22px; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- MAPPING MÉTIERS -> SOCLES ---
METIERS = {
    "🧸 Assistant Maternel": "SOCLE ASSISTANT MATERNEL",
    "👶 Assistant Parental (Garde d'enfants)": "SOCLE SALARIÉ DU PARTICULIER EMPLOYEUR",
    "🧹 Employé Familial": "SOCLE SALARIÉ DU PARTICULIER EMPLOYEUR",
    "👨‍🦽 Assistant de vie (Dépendance)": "SOCLE SALARIÉ DU PARTICULIER EMPLOYEUR",
    "🛠 Autres métiers": "DISPOSITIONS COMMUNES"
}

st.title("🛡️ Assistant CCN 3239")
st.write("Trouvez votre réponse en quelques clics.")

if not os.path.exists(DB_PATH):
    st.error("Base de données CCN_3239.db introuvable.")
else:
    if 'etape' not in st.session_state:
        st.session_state.etape = 1
        st.session_state.choix = {}

    conn = get_connection()

    # --- ÉTAPE 1 : LA SITUATION ---
    if st.session_state.etape == 1:
        st.markdown("<div class='question-box'><h3>1. Que se passe-t-il ?</h3></div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🐣 Embauche / Début"):
                st.session_state.choix['titre'] = 'TITRE 1  Formation du contrat de travail'
                st.session_state.etape = 2
                st.rerun()
        with col2:
            if st.button("🏁 Rupture / Fin"):
                st.session_state.choix['titre'] = 'TITRE 2  Rupture du contrat de travail'
                st.session_state.etape = 2
                st.rerun()

    # --- ÉTAPE 2 : LE MÉTIER ---
    elif st.session_state.etape == 2:
        st.markdown("<div class='question-box'><h3>2. Quel est le métier concerné ?</h3></div>", unsafe_allow_html=True)
        for metier, socle in METIERS.items():
            if st.button(metier):
                st.session_state.choix['socle'] = socle
                st.session_state.etape = 3
                st.rerun()
        if st.button("⬅️ Retour"):
            st.session_state.etape = 1
            st.rerun()

    # --- ÉTAPE 3 : LE THÈME (Chapitre) ---
    elif st.session_state.etape == 3:
        st.markdown("<div class='question-box'><h3>3. Quel est le sujet précis ?</h3></div>", unsafe_allow_html=True)
        query = "SELECT DISTINCT chapitres FROM convention_collective WHERE titres = ? AND socle = ? ORDER BY id"
        chaps = [r[0] for r in conn.execute(query, (st.session_state.choix['titre'], st.session_state.choix['socle'])).fetchall()]

        for c in chaps:
            nom_clair = c.split('CHAPITRE')[-1].strip() if 'CHAPITRE' in c else c
            if st.button(nom_clair):
                st.session_state.choix['chapitre'] = c
                st.session_state.etape = 4
                st.rerun()
        if st.button("⬅️ Retour"):
            st.session_state.etape = 2
            st.rerun()

    # --- ÉTAPE 4 : L'ARTICLE & RÉPONSE ---
    elif st.session_state.etape == 4:
        query = "SELECT numero_article_isole, affichage_article, texte_integral, texte_simplifie FROM convention_collective WHERE chapitres = ? AND socle = ? ORDER BY id"
        articles = conn.execute(query, (st.session_state.choix['chapitre'], st.session_state.choix['socle'])).fetchall()

        for art_num, art_titre, integral, simplifie in articles:
            st.markdown(f"<div class='titre-art'>Article {art_num} : {art_titre}</div>", unsafe_allow_html=True)
            
            # --- LOGIQUE DE RÉCUPÉRATION SI VIDE ---
            contenu_a_afficher = simplifie if (simplifie and simplifie.strip() != "") else integral
            label_entete = "💡 L'ESSENTIEL (A2)" if (simplifie and simplifie.strip() != "") else "⚖️ TEXTE DIRECT"

            st.markdown(f"**{label_entete}**")
            st.markdown(f"<div class='essentiel-box'>{contenu_a_afficher}</div>", unsafe_allow_html=True)
            
            # Si on a affiché le résumé, on met quand même l'officiel en dessous au cas où
            if simplifie and simplifie.strip() != "":
                with st.expander("Voir le texte officiel complet"):
                    st.write(integral)
            st.divider()

        if st.button("🔄 Nouvelle recherche"):
            st.session_state.etape = 1
            st.session_state.choix = {}
            st.rerun()

    conn.close()
