import streamlit as st
import sqlite3
import os

# Configuration de la page
st.set_page_config(page_title="Assistant CCN 3239", layout="centered")

DB_PATH = "CCN_3239.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

# --- STYLE CSS POUR MOBILE ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; margin-bottom: 10px; }
    .question-box { background-color: #f0f2f6; padding: 20px; border-radius: 15px; border-left: 5px solid #1e3799; margin-bottom: 20px; }
    .essentiel-box { background-color: #ecfdf5; border-left: 5px solid #27ae60; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Votre Assistant CCN")
st.write("Répondez aux questions pour trouver la règle applicable à votre situation.")

if not os.path.exists(DB_PATH):
    st.error("Base de données introuvable.")
else:
    # Utilisation du "session_state" pour mémoriser les choix de l'apprenant
    if 'etape' not in st.session_state:
        st.session_state.etape = 1
        st.session_state.choix = {}

    conn = get_connection()

    # --- ÉTAPE 1 : LA SITUATION GÉNÉRALE ---
    if st.session_state.etape == 1:
        st.markdown("<div class='question-box'><h3>1. Quelle est la situation ?</h3></div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🐣 Embauche / Début de contrat"):
                st.session_state.choix['titre'] = 'TITRE 1  Formation du contrat de travail'
                st.session_state.etape = 2
                st.rerun()
        with col2:
            if st.button("🏁 Rupture / Fin de contrat"):
                st.session_state.choix['titre'] = 'TITRE 2  Rupture du contrat de travail'
                st.session_state.etape = 2
                st.rerun()
        
        if st.button("⚙️ Vie du contrat (Exécution)"):
            st.info("Cette partie sera bientôt disponible. Concentrez-vous sur l'Embauche ou la Rupture.")

    # --- ÉTAPE 2 : LE SOCLE (Public concerné) ---
    elif st.session_state.etape == 2:
        st.markdown(f"<div class='question-box'><h3>2. Quel est le métier concerné ?</h3></div>", unsafe_allow_html=True)
        
        socles = [r[0] for r in conn.execute("SELECT DISTINCT socle FROM convention_collective WHERE titres = ?", (st.session_state.choix['titre'],)).fetchall()]
        
        for s in socles:
            if st.button(s):
                st.session_state.choix['socle'] = s
                st.session_state.etape = 3
                st.rerun()
        
        if st.button("⬅️ Retour"):
            st.session_state.etape = 1
            st.rerun()

    # --- ÉTAPE 3 : LE CHAPITRE (Le problème précis) ---
    elif st.session_state.etape == 3:
        st.markdown("<div class='question-box'><h3>3. Quel est votre problème précis ?</h3></div>", unsafe_allow_html=True)
        
        chaps = [r[0] for r in conn.execute(
            "SELECT DISTINCT chapitres FROM convention_collective WHERE titres = ? AND socle = ?", 
            (st.session_state.choix['titre'], st.session_state.choix['socle'])
        ).fetchall()]

        for c in chaps:
            # On nettoie un peu le nom du chapitre pour l'affichage du bouton
            nom_bouton = c.split('Chapitre')[-1].strip() if 'Chapitre' in c else c
            if st.button(nom_bouton):
                st.session_state.choix['chapitre'] = c
                st.session_state.etape = 4
                st.rerun()

        if st.button("⬅️ Retour"):
            st.session_state.etape = 2
            st.rerun()

    # --- ÉTAPE 4 : L'ARTICLE FINAL ---
    elif st.session_state.etape == 4:
        articles = conn.execute(
            "SELECT numero_article_isole, affichage_article, texte_integral, texte_simplifie FROM convention_collective WHERE chapitres = ? AND socle = ?", 
            (st.session_state.choix['chapitre'], st.session_state.choix['socle'])
        ).fetchall()

        for art_num, art_titre, integral, simplifie in articles:
            st.success(f"✅ Solution trouvée : Article {art_num}")
            st.subheader(art_titre)
            
            if simplifie:
                st.markdown("### 💡 L'ESSENTIEL (Niveau A2)")
                st.markdown(f"<div class='essentiel-box'>{simplifie}</div>", unsafe_allow_html=True)
            
            with st.expander("⚖️ Voir le texte officiel"):
                st.write(integral)

        if st.button("🔄 Recommencer une recherche"):
            st.session_state.etape = 1
            st.session_state.choix = {}
            st.rerun()

    conn.close()

# --- RECHERCHE PAR MOTS-CLÉS (En bas de page) ---
with st.sidebar:
    st.header("🔍 Recherche directe")
    search = st.text_input("Un mot précis ?")
    if search:
        conn = get_connection()
        res = conn.execute("SELECT numero_article_isole, affichage_article FROM convention_collective WHERE (texte_integral LIKE ? OR mots_cles LIKE ?) AND partie LIKE '%PARTIE IV%' LIMIT 5", (f'%{search}%', f'%{search}%')).fetchall()
        for r in res:
            st.info(f"Art. {r[0]} : {r[1]}")
        conn.close()
