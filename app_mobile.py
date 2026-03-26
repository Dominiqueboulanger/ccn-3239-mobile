import streamlit as st
import sqlite3
import os

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Assistant CCN 3239", layout="centered")

DB_PATH = "CCN_3239.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

# --- DICTIONNAIRE DE TRADUCTION (QUESTIONS PÉDAGOGIQUES) ---
# Ce dictionnaire remplace les noms de chapitres par vos questions
TRADUCTION_QUESTIONS = {
    "CHAPITRE I Formation du contrat de travail": "Comment rédiger le contrat et quels documents demander ?",
    "CHAPITRE II Période d’essai": "Combien de temps dure l'essai et comment l'arrêter ?",
    "CHAPITRE III Contrat de travail": "Quels sont les différents types de contrats (CDI, CDD) ?",
    "CHAPITRE I Départ à la retraite du salarié": "Quelles sont les règles pour le départ à la retraite ?",
    "CHAPITRE II Démission": "Comment démissionner et quel est le préavis ?",
    "CHAPITRE III Licenciement / Retrait d'emploi": "Comment se passe un licenciement (procédure, préavis) ?",
    "CHAPITRE IV Rupture conventionnelle": "Comment faire une rupture d'un commun accord ?",
    "CHAPITRE V Restitution du logement par le salarié à la fin du contrat de travail": "Que devient le logement de fonction à la fin du contrat ?"
}

# --- STYLE CSS POUR MOBILE ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 4em; font-weight: bold; margin-bottom: 10px; border: 2px solid #dcdde1; white-space: normal; }
    .question-box { background-color: #f1f2f6; padding: 20px; border-radius: 15px; border-left: 8px solid #1e3799; margin-bottom: 25px; }
    .essentiel-box { background-color: #ecfdf5; border-left: 5px solid #27ae60; padding: 18px; border-radius: 10px; font-size: 18px; color: #1e272e; }
    .titre-art { color: #1e3799; font-weight: bold; font-size: 20px; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Assistant CCN 3239")

if not os.path.exists(DB_PATH):
    st.error("Base de données CCN_3239.db introuvable.")
else:
    if 'etape' not in st.session_state:
        st.session_state.etape = 1
        st.session_state.choix = {}

    conn = get_connection()

    # --- ÉTAPE 1 : LA SITUATION ---
    if st.session_state.etape == 1:
        st.markdown("<div class='question-box'><h3>1. Que voulez-vous savoir ?</h3></div>", unsafe_allow_html=True)
        if st.button("🐣 Comment créer ou débuter le contrat ?"):
            st.session_state.choix['titre'] = 'TITRE 1  Formation du contrat de travail'
            st.session_state.etape = 2
            st.rerun()
        if st.button("🏁 Comment arrêter le contrat ?"):
            st.session_state.choix['titre'] = 'TITRE 2  Rupture du contrat de travail'
            st.session_state.etape = 2
            st.rerun()

    # --- ÉTAPE 2 : LE MÉTIER (AIGUILLAGE SOCLE) ---
    elif st.session_state.etape == 2:
        st.markdown("<div class='question-box'><h3>2. Pour quel métier ?</h3></div>", unsafe_allow_html=True)
        
        mapping = {
            "🧸 Assistant Maternel": "SOCLE ASSISTANT MATERNEL",
            "👶 Assistant Parental (Garde d'enfants)": "SOCLE SALARIÉ DU PARTICULIER EMPLOYEUR",
            "🧹 Employé Familial": "SOCLE SALARIÉ DU PARTICULIER EMPLOYEUR",
            "👨‍🦽 Assistant de Vie (Dépendance)": "SOCLE SALARIÉ DU PARTICULIER EMPLOYEUR",
            "🛠 Autres métiers / Socle Commun": "DISPOSITIONS COMMUNES"
        }

        for label, socle in mapping.items():
            if st.button(label):
                st.session_state.choix['socle'] = socle
                st.session_state.etape = 3
                st.rerun()
        
        if st.button("⬅️ Retour"):
            st.session_state.etape = 1
            st.rerun()

    # --- ÉTAPE 3 : LA QUESTION (CHAPITRE) ---
    elif st.session_state.etape == 3:
        st.markdown("<div class='question-box'><h3>3. Quelle est votre question précise ?</h3></div>", unsafe_allow_html=True)
        
        query = "SELECT DISTINCT chapitres FROM convention_collective WHERE titres = ? AND socle = ? ORDER BY id"
        chaps = [r[0] for r in conn.execute(query, (st.session_state.choix['titre'], st.session_state.choix['socle'])).fetchall()]

        for c in chaps:
            # On utilise la traduction pédagogique si elle existe, sinon le nom brut
            label_bouton = TRADUCTION_QUESTIONS.get(c, c)
            if st.button(label_bouton):
                st.session_state.choix['chapitre'] = c
                st.session_state.etape = 4
                st.rerun()

        if st.button("⬅️ Retour"):
            st.session_state.etape = 2
            st.rerun()

    # --- ÉTAPE 4 : LA RÉPONSE (ARTICLE) ---
    elif st.session_state.etape == 4:
        query = "SELECT numero_article_isole, affichage_article, texte_integral, texte_simplifie FROM convention_collective WHERE chapitres = ? AND socle = ? ORDER BY id"
        articles = conn.execute(query, (st.session_state.choix['chapitre'], st.session_state.choix['socle'])).fetchall()

        st.success(f"📍 {TRADUCTION_QUESTIONS.get(st.session_state.choix['chapitre'], 'Résultat')}")

        for num, titre, integral, simplifie in articles:
            st.markdown(f"<div class='titre-art'>Article {num} : {titre}</div>", unsafe_allow_html=True)
            
            # GESTION DU TEXTE VIDE OU COURT
            if simplifie and simplifie.strip() != "":
                st.markdown("**💡 L'ESSENTIEL (Niveau A2)**")
                st.markdown(f"<div class='essentiel-box'>{simplifie}</div>", unsafe_allow_html=True)
                with st.expander("⚖️ Voir le texte officiel complet"):
                    st.write(integral)
            else:
                st.markdown("**⚖️ TEXTE OFFICIEL (Direct)**")
                st.markdown(f"<div class='essentiel-box'>{integral}</div>", unsafe_allow_html=True)
            
            st.divider()

        if st.button("🔄 Nouvelle recherche"):
            st.session_state.etape = 1
            st.session_state.choix = {}
            st.rerun()

    conn.close()
