import streamlit as st
import sqlite3
from pathlib import Path

# --- CONFIGURATION ---
st.set_page_config(page_title="CCN 3239 - Parcours Apprenant", layout="centered")

BASE_DIR = Path(__file__).parent
DB_PATH = (BASE_DIR / "CCN_3239.db").resolve()

def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row 
    return conn

# --- STYLE CSS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; min-height: 3.8em; font-weight: bold; margin-bottom: 10px; border: 2px solid #1e3799; background-color: white; }
    .question-box { background-color: #f8f9fa; padding: 20px; border-radius: 15px; border-left: 8px solid #1e3799; margin-bottom: 20px; }
    .essentiel-box { background-color: #ecfdf5; border-left: 5px solid #27ae60; padding: 15px; border-radius: 10px; color: #065f46; }
    </style>
    """, unsafe_allow_html=True)

if 'etape' not in st.session_state:
    st.session_state.etape = 1
    st.session_state.choix = {}

st.title("🛡️ Assistant CCN 3239")

# ETAPE 1 : LE MÉTIER (Synchronisation des étiquettes SPE)
    if st.session_state.etape == 1:
        st.markdown("<div class='question-box'><h3>1. Quel est votre métier ?</h3></div>", unsafe_allow_html=True)
        
        # Le dictionnaire suivant fait le pont entre le bouton et votre base SQL
        metiers = {
            "🧸 Assistant Maternel": "SOCLE ASSISTANT MATERNEL",
            "👶 Assistant Parental (Garde d'enfants)": "SOCLE SALARIÉ DU PARTICULIER EMPLOYEUR",
            "👴 Assistant de Vie (Dépendance)": "SOCLE SALARIÉ DU PARTICULIER EMPLOYEUR",
            "🏠 Employé Familial": "SOCLE SALARIÉ DU PARTICULIER EMPLOYEUR",
            "🛠 Autres (Socle Commun)": "SOCLE COMMUN"
        }
        
        for label, socle_val in metiers.items():
            if st.button(label):
                st.session_state.choix['socle'] = socle_val
                st.session_state.choix['metier_label'] = label
                st.session_state.etape = 2
                st.rerun()

# --- ÉTAPE 2 : SITUATION ---
elif st.session_state.etape == 2:
    st.subheader("2. Envisagez-vous la fin de votre contrat ?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Non"):
            st.session_state.choix['titre_filtre'] = "TITRE 1" # Correspond au début de votre texte base
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

# --- ÉTAPE 3 : QUESTIONS (JOINTURE SUR ID) ---
elif st.session_state.etape == 3:
    st.subheader("3. Quel sujet vous questionne ?")
    
    conn = get_connection()
    try:
        # Utilisation de LIKE avec % pour ignorer les espaces bizarres après TITRE 1
        query = """
            SELECT q.question_texte, c.numero_article_isole 
            FROM questions_app q
            INNER JOIN convention_collective c ON q.id = c.id
            WHERE c.socle = ? AND c.titres LIKE ?
        """
        socle = st.session_state.choix['socle']
        titre_pattern = f"{st.session_state.choix['titre_filtre']}%"
        
        questions = conn.execute(query, (socle, titre_pattern)).fetchall()

        if not questions:
            st.info(f"Recherche pour : {socle} et {st.session_state.choix['titre_filtre']}")
            st.warning("Aucune question trouvée. Vérifiez que vos IDs sont bien liés pour ce socle.")
        else:
            for q in questions:
                if st.button(q['question_texte']):
                    st.session_state.choix['article_racine'] = q['numero_article_isole']
                    st.session_state.etape = 4
                    st.rerun()
    except Exception as e:
        st.error(f"Erreur : {e}")
    finally:
        conn.close()
    
    if st.button("⬅️ Retour"):
        st.session_state.etape = 2
        st.rerun()

# --- ÉTAPE 4 : RÉSULTATS ---
elif st.session_state.etape == 4:
    racine = st.session_state.choix['article_racine']
    socle = st.session_state.choix['socle']
    
    st.subheader(f"Détails : Article {racine}")
    
    conn = get_connection()
    # On cherche l'article et ses dérivés
    query = """
        SELECT numero_article_isole, affichage_article, texte_integral, texte_simplifie 
        FROM convention_collective 
        WHERE (numero_article_isole = ? OR numero_article_isole LIKE ?)
        AND socle = ?
        ORDER BY id ASC
    """
    articles = conn.execute(query, (str(racine), f"{racine}-%", socle)).fetchall()
    conn.close()

    if articles:
        for art in articles:
            with st.expander(f"📄 Article {art['numero_article_isole']}"):
                if art['texte_simplifie']:
                    st.markdown(f"<div class='essentiel-box'><b>💡 L'ESSENTIEL :</b><br>{art['texte_simplifie']}</div>", unsafe_allow_html=True)
                st.write(art['texte_integral'])
    
    if st.button("🔄 Nouvelle recherche"):
        st.session_state.etape = 1
        st.rerun()
