import streamlit as st
import sqlite3
import os

# Configuration de la page
st.set_page_config(page_title="Assistant CCN 3239", layout="centered")

DB_PATH = "CCN_3239.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

# --- INTERFACE & BOUTONS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.8em; font-weight: bold; margin-bottom: 12px; border: 2px solid #dcdde1; font-size: 16px; }
    .stButton>button:hover { border: 2px solid #1e3799; color: #1e3799; }
    .question-box { background-color: #f1f2f6; padding: 20px; border-radius: 15px; border-left: 8px solid #1e3799; margin-bottom: 25px; }
    .essentiel-box { background-color: #ecfdf5; border-left: 5px solid #27ae60; padding: 18px; border-radius: 10px; font-size: 18px; line-height: 1.5; }
    .titre-art { color: #1e3799; font-weight: bold; font-size: 22px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIQUE D'AIGUILLAGE MÉTIERS ---
METIERS = {
    "🧸 Assistant Maternel": "SOCLE ASSISTANT MATERNEL",
    "👶 Assistant Parental (Garde d'enfants)": "SOCLE SALARIÉ DU PARTICULIER EMPLOYEUR",
    "🧹 Employé Familial": "SOCLE SALARIÉ DU PARTICULIER EMPLOYEUR",
    "👨‍🦽 Assistant de vie (Dépendance)": "SOCLE SALARIÉ DU PARTICULIER EMPLOYEUR",
    "🛠 Autres métiers": "DISPOSITIONS COMMUNES"
}

st.title("🛡️ Assistant CCN 3239")

if not os.path.exists(DB_PATH):
    st.error("Base de données introuvable. Assurez-vous que CCN_3239.db est au bon endroit.")
else:
    if 'etape' not in st.session_state:
        st.session_state.etape = 1
        st.session_state.choix = {}

    conn = get_connection()

    # --- ÉTAPE 1 : SITUATION GLOBALE ---
    if st.session_state.etape == 1:
        st.markdown("<div class='question-box'><h3>1. Quelle est la situation du contrat ?</h3></div>", unsafe_allow_html=True)
        if st.button("🐣 C'est le début (Embauche, essai, signature)"):
            st.session_state.choix['titre'] = 'TITRE 1  Formation du contrat de travail'
            st.session_state.etape = 2
            st.rerun()
        if st.button("🏁 C'est la fin (Démission, licenciement, retraite)"):
            st.session_state.choix['titre'] = 'TITRE 2  Rupture du contrat de travail'
            st.session_state.etape = 2
            st.rerun()

    # --- ÉTAPE 2 : LE MÉTIER ---
    elif st.session_state.etape == 2:
        st.markdown("<div class='question-box'><h3>2. Quel est le métier exercé ?</h3></div>", unsafe_allow_html=True)
        for label, socle in METIERS.items():
            if st.button(label):
                st.session_state.choix['socle'] = socle
                st.session_state.etape = 3
                st.rerun()
        if st.button("⬅️ Retour"):
            st.session_state.etape = 1
            st.rerun()

    # --- ÉTAPE 3 : LE PROBLÈME PRÉCIS ---
    elif st.session_state.etape == 3:
        st.markdown("<div class='question-box'><h3>3. Quel est votre sujet de recherche ?</h3></div>", unsafe_allow_html=True)
        
        # On récupère les chapitres disponibles pour ce Titre et ce Socle
        query = "SELECT DISTINCT chapitres FROM convention_collective WHERE titres = ? AND socle = ? ORDER BY id"
        chaps = [r[0] for r in conn.execute(query, (st.session_state.choix['titre'], st.session_state.choix['socle'])).fetchall()]

        if not chaps:
            st.warning("Aucun chapitre trouvé pour cette combinaison. Essayez un autre métier ou situation.")
        else:
            for c in chaps:
                # Nettoyage pour n'afficher que le texte après "CHAPITRE X"
                label_bouton = c.split('CHAPITRE')[-1].strip() if 'CHAPITRE' in c else c
                if st.button(label_bouton):
                    st.session_state.choix['chapitre'] = c
                    st.session_state.etape = 4
                    st.rerun()
        
        if st.button("⬅️ Retour"):
            st.session_state.etape = 2
            st.rerun()

    # --- ÉTAPE 4 : RÉSULTATS ---
    elif st.session_state.etape == 4:
        query = "SELECT numero_article_isole, affichage_article, texte_integral, texte_simplifie FROM convention_collective WHERE chapitres = ? AND socle = ? ORDER BY id"
        articles = conn.execute(query, (st.session_state.choix['chapitre'], st.session_state.choix['socle'])).fetchall()

        st.info(f"📍 {st.session_state.choix['chapitre']}")

        for art_num, art_titre, integral, simplifie in articles:
            st.markdown(f"<div class='titre-art'>Article {art_num} : {art_titre}</div>", unsafe_allow_html=True)
            
            # Vérification : si le résumé est vide, on prend l'intégral
            a_afficher = simplifie if (simplifie and simplifie.strip() != "") else integral
            type_label = "💡 L'ESSENTIEL (Niveau A2)" if (simplifie and simplifie.strip() != "") else "⚖️ TEXTE OFFICIEL"

            st.write(f"**{type_label}**")
            st.markdown(f"<div class='essentiel-box'>{a_afficher}</div>", unsafe_allow_html=True)
            
            # Si on a montré un résumé, on garde l'officiel en option
            if simplifie and simplifie.strip() != "":
                with st.expander("Consulter le texte juridique complet"):
                    st.write(integral)
            st.divider()

        if st.button("🔄 Recommencer une recherche"):
            st.session_state.etape = 1
            st.session_state.choix = {}
            st.rerun()

    conn.close()
