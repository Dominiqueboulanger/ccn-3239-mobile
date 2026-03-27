import streamlit as st
import sqlite3
from pathlib import Path

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="🛡️ Assistant CCN 3239", layout="centered")

# Gestion du chemin vers la base de données
BASE_DIR = Path(__file__).parent
DB_PATH = (BASE_DIR / "CCN_3239.db").resolve()

def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row 
    return conn

# --- STYLE CSS POUR MOBILE ---
st.markdown("""
    <style>
    .stButton>button { 
        width: 100%; 
        border-radius: 12px; 
        min-height: 3.8em; 
        font-weight: bold; 
        margin-bottom: 10px; 
        border: 2px solid #1e3799; 
        white-space: normal;
        background-color: white;
    }
    .question-box { 
        background-color: #f8f9fa; 
        padding: 20px; 
        border-radius: 15px; 
        border-left: 8px solid #1e3799; 
        margin-bottom: 20px; 
    }
    .essentiel-box { 
        background-color: #ecfdf5; 
        border-left: 5px solid #27ae60; 
        padding: 15px; 
        border-radius: 10px; 
        color: #065f46; 
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION DE LA SESSION ---
if 'etape' not in st.session_state:
    st.session_state.etape = 1
    st.session_state.choix = {}

st.title("🛡️ Assistant CCN 3239")

# --- LOGIQUE DES ÉTAPES ---

# ÉTAPE 1 : LE MÉTIER
if st.session_state.etape == 1:
    st.markdown("<div class='question-box'><h3>1. Quel est votre métier ?</h3></div>", unsafe_allow_html=True)
    
    # Mapping synchronisé avec les valeurs en MAJUSCULES de votre base
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
            st.session_state.etape = 2
            st.rerun()

# ÉTAPE 2 : VIE OU RUPTURE DU CONTRAT
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

# ÉTAPE 3 : SÉLECTION DE LA QUESTION (Jointure SQL sur ID)
elif st.session_state.etape == 3:
    st.markdown("<div class='question-box'><h3>3. Quel sujet vous questionne ?</h3></div>", unsafe_allow_html=True)
    
    conn = get_connection()
    try:
        # On lie questions_app et convention_collective par l'ID
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
            st.info(f"Profil : {socle}")
            st.warning("Aucune question trouvée pour ce profil et ce motif.")
        else:
            for q in questions:
                if st.button(q['question_texte']):
                    st.session_state.choix['article_racine'] = q['numero_article_isole']
                    st.session_state.etape = 4
                    st.rerun()
    except Exception as e:
        st.error(f"Erreur de base de données : {e}")
    finally:
        conn.close()
    
    if st.button("⬅️ Retour"):
        st.session_state.etape = 2
        st.rerun()

# ÉTAPE 4 : AFFICHAGE DES RÉSULTATS (Articles racines et dérivés)
elif st.session_state.etape == 4:
    racine = st.session_state.choix['article_racine']
    socle = st.session_state.choix['socle']
    
    st.subheader(f"Détails : Article {racine}")
    
    conn = get_connection()
    # On affiche l'article racine ET ses variantes (ex: 41, 41-1, 41-2...)
    query = """
        SELECT numero_article_isole, affichage_article, texte_integral, texte_simplifie 
        FROM convention_collective 
        WHERE (numero_article_isole = ? OR numero_article_isole LIKE ?)
        AND socle = ?
        ORDER BY numero_article_isole ASC
    """
    search_pattern = f"{racine}-%"
    articles = conn.execute(query, (str(racine), search_pattern, socle)).fetchall()
    conn.close()

    if articles:
        for art in articles:
            with st.expander(f"📄 Article {art['numero_article_isole']} - {art['affichage_article'][:50]}..."):
                if art['texte_simplifie']:
                    st.markdown(f"<div class='essentiel-box'><b>💡 L'ESSENTIEL :</b><br>{art['texte_simplifie']}</div>", unsafe_allow_html=True)
                st.markdown("**⚖️ Texte Officiel :**")
                st.write(art['texte_integral'])
    else:
        st.error("Détails introuvables pour cet article.")

    if st.button("🔄 Nouvelle recherche"):
        st.session_state.etape = 1
        st.session_state.choix = {}
        st.rerun()
