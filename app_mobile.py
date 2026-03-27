import streamlit as st
import sqlite3
from pathlib import Path

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Assistant CCN 3239", layout="centered")

# Gestion des chemins
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "CCN_3239.db"

def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # Permet d'accéder aux colonnes par nom
    return conn

# --- STYLE CSS POUR MOBILE ---
st.markdown("""
    <style>
    .stButton>button { 
        width: 100%; 
        border-radius: 12px; 
        min-height: 4em; 
        font-weight: bold; 
        margin-bottom: 12px; 
        border: 2px solid #1e3799; 
        white-space: normal;
        background-color: white;
    }
    .essentiel-box { 
        background-color: #ecfdf5; 
        border-left: 5px solid #27ae60; 
        padding: 15px; 
        border-radius: 10px; 
        font-size: 16px;
        color: #065f46;
        margin-bottom: 10px;
    }
    .situation-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION DES VARIABLES DE SESSION ---
if 'etape' not in st.session_state:
    st.session_state.etape = 1
    st.session_state.choix = {}

st.title("Le contrat de travail")
st.write("---")

conn = get_connection()

# --- ÉTAPE 1 : CHOIX DE LA PROFESSION (VERROUILLÉE) ---
if st.session_state.etape == 1:
    st.subheader("Quelle est votre profession ?")
    
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

# --- ÉTAPE 2 : LE MOTIF (VERROUILLÉE) ---
elif st.session_state.etape == 2:
    st.subheader("Envisagez-vous la fin de votre contrat ?")
    
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

# --- ÉTAPE 3 : LISTE DES QUESTIONS (FILTRAGE SQL) ---
elif st.session_state.etape == 3:
    st.subheader("Quelle est votre question ?")
    
    # Commande SQL avec jointure pour filtrer par Socle et Titre
    query = """
        SELECT q.id, q.question_texte, c.numero_article_isole 
        FROM questions_app q
        JOIN convention_collective c ON q.id = c.id
        WHERE c.socle = ? AND c.titres LIKE ?
    """
    
    socle_user = st.session_state.choix['socle']
    # On cherche "TITRE 1%" ou "TITRE 2%" selon la réponse à l'étape 2
    filtre_titre = f"{st.session_state.choix['titre_filtre']}%"
    
    questions = conn.execute(query, (socle_user, filtre_titre)).fetchall()

    if not questions:
        st.warning("Aucune question n'est encore répertoriée pour ce profil.")
    else:
        for q in questions:
            # On affiche le texte de la question stocké dans la table questions_app
            if st.button(q['question_texte']):
                # On mémorise l'article racine pour l'étape 4
                st.session_state.choix['article_racine'] = q['numero_article_isole']
                st.session_state.etape = 4
                st.rerun()

    if st.button("⬅️ Retour"):
        st.session_state.etape = 2
        st.rerun()

# --- ÉTAPE 4 : RÉSULTAT (DÉPLOIEMENT ARBORESCENT) ---
elif st.session_state.etape == 4:
    racine = st.session_state.choix['article_racine']
    socle_user = st.session_state.choix['socle']
    
    st.subheader(f"Détails : Article {racine}")
    
    # Sélectionne l'article racine ET ses sous-articles (41, 41-1, 41-2...)
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
        st.error("Aucune donnée trouvée pour cet article.")

    if st.button("🔄 Nouvelle recherche"):
        st.session_state.etape = 1
        st.session_state.choix = {}
        st.rerun()

conn.close()
