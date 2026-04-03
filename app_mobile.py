import streamlit as st
import sqlite3

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Guide CCN 3239", layout="centered")

# --- STYLE CSS POUR SMARTPHONE (Gros boutons) ---
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        height: 70px;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 15px;
        border-radius: 15px;
        background-color: #ffffff;
        border: 2px solid #e0e0e0;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    div.stButton > button:hover {
        border-color: #2e7d32;
        color: #2e7d32;
    }
    .stAlert {
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

def get_connection():
    conn = sqlite3.connect("CCN_3239.db")
    conn.row_factory = sqlite3.Row
    return conn

# --- INITIALISATION DES VARIABLES DE NAVIGATION ---
if 'etape' not in st.session_state:
    st.session_state.etape = 1
    st.session_state.socle = None  # AM, EF, PE ou SC
    st.session_state.theme_choisi = None
    st.session_state.target_article = None

# --- LOGIQUE DE L'APPLICATION ---

st.title("⚖️ Mon Assistant CCN 3239")

# ETAPE 1 : QUEL EST VOTRE MÉTIER ?
if st.session_state.etape == 1:
    st.subheader("1️⃣ Quel est votre métier ?")
    
    if st.button("🍼 Assistant Maternel"):
        st.session_state.socle = "AM"
        st.session_state.etape = 2
        st.rerun()
        
    if st.button("👵 Assistant de Vie / Parental"):
        st.session_state.socle = "PE"
        st.session_state.etape = 2
        st.rerun()
        
    if st.button("🏠 Employé Familial"):
        st.session_state.socle = "EF"
        st.session_state.etape = 2
        st.rerun()

    if st.button("🌳 Autres (Jardinier, chauffeur...)"):
        st.session_state.socle = "SC"
        st.session_state.etape = 2
        st.rerun()

# ETAPE 2 : RUPTURE OU EXÉCUTION ?
elif st.session_state.etape == 2:
    st.subheader("2️⃣ Votre situation")
    
    if st.button("🛑 Souhaitez-vous mettre fin au contrat ?"):
        st.session_state.theme_choisi = "Rupture"
        st.session_state.etape = 3
        st.rerun()
        
    if st.button("📝 Question sur le travail au quotidien"):
        st.session_state.etape = 3
        st.rerun()
        
    if st.button("⬅️ Retour au métier"):
        st.session_state.etape = 1
        st.rerun()

# ETAPE 3 : CHOIX DE LA THÉMATIQUE (Dynamique)
elif st.session_state.etape == 3:
    st.subheader("3️⃣ De quoi parle votre question ?")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # On filtre les thèmes. Si "Rupture" a été choisi, on filtre sur les thèmes de fin de contrat.
    if st.session_state.theme_choisi == "Rupture":
        query = "SELECT DISTINCT theme FROM questions_app WHERE theme LIKE '%Rupture%' OR theme LIKE '%Préavis%' OR theme LIKE '%Indemnité%'"
    else:
        query = "SELECT DISTINCT theme FROM questions_app WHERE theme NOT LIKE '%Rupture%' AND theme NOT LIKE '%Préavis%' AND theme NOT LIKE '%Indemnité%'"
    
    cursor.execute(query)
    themes = [row['theme'] for row in cursor.fetchall()]
    
    for t in themes:
        if st.button(f"🔹 {t}"):
            st.session_state.theme_choisi = t
            st.session_state.etape = 4
            st.rerun()
            
    if st.button("⬅️ Retour"):
        st.session_state.theme_choisi = None
        st.session_state.etape = 2
        st.rerun()
    conn.close()

# ETAPE 4 : LA QUESTION FINALE
elif st.session_state.etape == 4:
    st.subheader(f"❓ Précisez votre question :")
    st.write(f"Thème : {st.session_state.theme_choisi}")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # On affiche les questions liées au thème
    cursor.execute("SELECT article_id, question_claire FROM questions_app WHERE theme = ?", (st.session_state.theme_choisi,))
    questions = cursor.fetchall()
    
    for q in questions:
        if st.button(q['question_claire']):
            st.session_state.target_article = q['article_id']
            st.session_state.etape = 5
            st.rerun()
            
    if st.button("⬅️ Retour aux thèmes"):
        st.session_state.etape = 3
        st.rerun()
    conn.close()

# ETAPE 5 : RÉSULTAT FINAL
elif st.session_state.etape == 5:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM convention_collective WHERE id = ?", (st.session_state.target_article,))
    art = cursor.fetchone()
    
    if art:
        st.success(f"### ✅ {art['affichage_article']}")
        
        st.markdown("#### 💡 L'essentiel à savoir :")
        st.info(art['texte_simplifie'])
        
        with st.expander("⚖️ Voir le texte officiel"):
            st.write(art['texte_integral'])
    else:
        st.error("Article non trouvé dans la base.")
        
    if st.button("🔄 Recommencer une recherche"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    conn.close()

# PIED DE PAGE
st.divider()
st.caption("Application de formation CCN 3239 - Secteur Particulier Employeur")
