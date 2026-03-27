import streamlit as st
import sqlite3
from pathlib import Path

# --- CONFIGURATION ---
st.set_page_config(page_title="CCN 3239 - Parcours Apprenant", layout="centered")

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "CCN_3239.db"

def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row # Crucial pour accéder aux colonnes par nom
    return conn

# --- STYLE CSS MOBILE ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; min-height: 3.8em; font-weight: bold; margin-bottom: 10px; border: 2px solid #1e3799; white-space: normal; background-color: white; }
    .question-box { background-color: #f8f9fa; padding: 20px; border-radius: 15px; border-left: 8px solid #1e3799; margin-bottom: 20px; }
    .essentiel-box { background-color: #ecfdf5; border-left: 5px solid #27ae60; padding: 15px; border-radius: 10px; font-size: 17px; color: #065f46; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION ---
if 'etape' not in st.session_state:
    st.session_state.etape = 1
    st.session_state.choix = {}

st.title("🛡️ Assistant CCN 3239")

conn = get_connection()

try:
    # ETAPE 1 : LE MÉTIER (VOTRE VERSION VERROUILLÉE)
    if st.session_state.etape == 1:
        st.markdown("<div class='question-box'><h3>1. Quel est votre métier ?</h3></div>", unsafe_allow_html=True)
        
        if st.button("Assistant Maternel"):
            st.session_state.choix['socle'] = "Assistant maternel"
            st.session_state.etape = 2
            st.rerun()
            
        if st.button("Assistant Parental (Garde d'enfants)"):
            st.session_state.choix['socle'] = "Salarié du particulier employeur"
            st.session_state.etape = 2
            st.rerun()

        if st.button("Assistant de Vie Dépendance"):
            st.session_state.choix['socle'] = "Salarié du particulier employeur"
            st.session_state.etape = 2
            st.rerun()

        if st.button("Employé Familial (Ménage, cuisine...)"):
            st.session_state.choix['socle'] = "Salarié du particulier employeur"
            st.session_state.etape = 2
            st.rerun()

        if st.button("Autres"):
            st.session_state.choix['socle'] = "socle commun"
            st.session_state.etape = 2
            st.rerun()

    # ETAPE 2 : BINAIRE (FIN DE CONTRAT)
    elif st.session_state.etape == 2:
        st.markdown("<div class='question-box'><h3>2. Votre situation</h3><p>Envisagez-vous la fin de votre contrat ?</p></div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Non"):
                st.session_state.choix['titre_filtre'] = "TITRE 1"
                st.session_state.etape = 3
                st.rerun()
        with col2:
            if st.button("Oui"):
                st.session_state.choix['titre_filtre'] = "TITRE 2"
                st.session_state.etape = 3
                st.rerun()
        
        if st.button("⬅️ Retour"):
            st.session_state.etape = 1
            st.rerun()

    # ETAPE 3 : SELECTION DE LA QUESTION (TABLE questions_app)
    elif st.session_state.etape == 3:
        st.markdown(f"<div class='question-box'><h3>3. Quel sujet vous questionne ?</h3></div>", unsafe_allow_html=True)
        
        # Jointure correcte avec vos tables réelles
        query = """
            SELECT q.id, q.question_texte, c.numero_article_isole 
            FROM questions_app q
            JOIN convention_collective c ON q.id = c.id
            WHERE c.socle = ? AND c.titres LIKE ?
        """
        socle_user = st.session_state.choix['socle']
        filtre_titre = f"{st.session_state.choix['titre_filtre']}%"
        
        questions = conn.execute(query, (socle_user, filtre_titre)).fetchall()

        if not questions:
            st.warning("Aucune question trouvée pour ce profil.")
        else:
            for q in questions:
                if st.button(q['question_texte']):
                    st.session_state.choix['article_racine'] = q['numero_article_isole']
                    st.session_state.etape = 4
                    st.rerun()
        
        if st.button("⬅️ Retour"):
            st.session_state.etape = 2
            st.rerun()

    # ETAPE 4 : RÉSULTAT (LOGIQUE D'ARTICLES RACINES)
    elif st.session_state.etape == 4:
        racine = st.session_state.choix['article_racine']
        socle_user = st.session_state.choix['socle']
        
        st.subheader(f"Détails : Article {racine}")
        
        # On cherche l'article racine ET ses dérivés (41, 41-1...)
        query = """
            SELECT numero_article_isole, affichage_article, texte_integral, texte_simplifie 
            FROM convention_collective 
            WHERE (numero_article_isole = ? OR numero_article_isole LIKE ?)
            AND socle = ?
            ORDER BY numero_article_isole ASC
        """
        search_pattern = f"{racine}-%"
        articles = conn.execute(query, (racine, search_pattern, socle_user)).fetchall()

        if articles:
            for art in articles:
                with st.expander(f"📄 Article {art['numero_article_isole']} - {art['affichage_article'][:50]}..."):
                    if art['texte_simplifie']:
                        st.markdown(f"<div class='essentiel-box'><b>💡 L'ESSENTIEL :</b><br>{art['texte_simplifie']}</div>", unsafe_allow_html=True)
                    st.markdown("**⚖️ Texte Officiel :**")
                    st.write(art['texte_integral'])
        else:
            st.error("Détails introuvables.")

        if st.button("🔄 Nouvelle recherche"):
            st.session_state.etape = 1
            st.session_state.choix = {}
            st.rerun()

except sqlite3.Error as e:
    st.error(f"Erreur de base de données : {e}")

finally:
    conn.close()
