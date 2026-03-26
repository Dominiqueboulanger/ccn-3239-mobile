import streamlit as st
import sqlite3
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="Assistant CCN 3239", layout="centered")

# Utilisez votre chemin complet si nécessaire
DB_PATH = "/Users/dominiqueboulanger/Desktop/CNN 3239/CNN 3239.db 2 tables/CCN_3239.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

# --- STYLE CSS POUR MOBILE ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; margin-bottom: 10px; border: 2px solid #dcdde1; white-space: normal; }
    .question-box { background-color: #f1f2f6; padding: 20px; border-radius: 15px; border-left: 8px solid #1e3799; margin-bottom: 25px; }
    .essentiel-box { background-color: #ecfdf5; border-left: 5px solid #27ae60; padding: 18px; border-radius: 10px; font-size: 18px; color: #1e272e; }
    .titre-art { color: #1e3799; font-weight: bold; font-size: 20px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Assistant CCN 3239")

if not os.path.exists(DB_PATH):
    st.error(f"Base de données introuvable à l'adresse : {DB_PATH}")
else:
    # Initialisation des variables de session
    if 'etape' not in st.session_state:
        st.session_state.etape = 1
        st.session_state.choix = {}

    conn = get_connection()

    # --- ÉTAPE 1 : CHOIX DU MÉTIER (SOCLE) ---
    if st.session_state.etape == 1:
        st.markdown("<div class='question-box'><h3>1. Quel est le métier concerné ?</h3></div>", unsafe_allow_html=True)
        metiers = {
            "🧸 Assistant Maternel": "SOCLE ASSISTANT MATERNEL",
            "👶 Assistant Parental (Garde d'enfants)": "SOCLE SALARIÉ DU PARTICULIER EMPLOYEUR",
            "🧹 Employé Familial": "SOCLE SALARIÉ DU PARTICULIER EMPLOYEUR",
            "👨‍🦽 Assistant de Vie (Dépendance)": "SOCLE SALARIÉ DU PARTICULIER EMPLOYEUR",
            "🛠 Autres métiers / Socle Commun": "DISPOSITIONS COMMUNES"
        }
        for label, socle in metiers.items():
            if st.button(label):
                st.session_state.choix['socle'] = socle
                st.session_state.etape = 2
                st.rerun()

    # --- ÉTAPE 2 : CHOIX DU THÈME (CHAPITRE) ---
    elif st.session_state.etape == 2:
        st.markdown("<div class='question-box'><h3>2. Quel thème vous intéresse ?</h3></div>", unsafe_allow_html=True)
        
        # On récupère les thèmes disponibles pour ce socle dans la table navigation
        # Note : On filtre par socle si votre fichier W1 contenait cette info, 
        # sinon on affiche tout ce qui est disponible dans la table de navigation.
        query = "SELECT DISTINCT theme FROM navigation_pedagogique ORDER BY theme"
        themes = [r[0] for r in conn.execute(query).fetchall()]

        for t in themes:
            if st.button(t):
                st.session_state.choix['theme'] = t
                st.session_state.etape = 3
                st.rerun()
        
        if st.button("⬅️ Retour"):
            st.session_state.etape = 1
            st.rerun()

    # --- ÉTAPE 3 : CHOIX DE L'ARTICLE ---
    elif st.session_state.etape == 3:
        st.markdown(f"<div class='question-box'><h3>3. {st.session_state.choix['theme']}</h3><p>Choisissez un point précis :</p></div>", unsafe_allow_html=True)
        
        # On liste les boutons (articles) liés à ce thème
        query = "SELECT reponse_bouton, articles_lies FROM navigation_pedagogique WHERE theme = ?"
        options = conn.execute(query, (st.session_state.choix['theme'],)).fetchall()

        for label_bouton, art_id in options:
            if st.button(label_bouton):
                st.session_state.choix['article_id'] = art_id
                st.session_state.etape = 4
                st.rerun()

        if st.button("⬅️ Retour"):
            st.session_state.etape = 2
            st.rerun()

    # --- ÉTAPE 4 : AFFICHAGE DU TEXTE ---
    elif st.session_state.etape == 4:
        art_id = st.session_state.choix['article_id']
        socle = st.session_state.choix['socle']
        
        # Récupération du contenu de l'article dans la table principale
        query = "SELECT affichage_article, texte_integral, texte_simplifie FROM convention_collective WHERE numero_article_isole = ? AND socle = ?"
        res = conn.execute(query, (art_id, socle)).fetchone()

        if res:
            titre, integral, simplifie = res
            st.markdown(f"<div class='titre-art'>Article {art_id} : {titre}</div>", unsafe_allow_html=True)
            
            # LOGIQUE : Priorité au résumé, sinon texte intégral brut
            if simplifie and simplifie.strip():
                st.markdown("**💡 L'ESSENTIEL (Niveau A2)**")
                st.markdown(f"<div class='essentiel-box'>{simplifie}</div>", unsafe_allow_html=True)
                
                # Bouton pour voir l'intégral si besoin
                with st.expander("⚖️ Voir le texte officiel intégral"):
                    st.write(integral)
            else:
                st.markdown("**⚖️ TEXTE OFFICIEL (Version brute)**")
                st.markdown(f"<div class='essentiel-box'>{integral}</div>", unsafe_allow_html=True)
        else:
            st.warning("Désolé, le contenu détaillé de cet article n'a pas été trouvé pour ce métier.")

        if st.button("🔄 Nouvelle recherche"):
            st.session_state.etape = 1
            st.session_state.choix = {}
            st.rerun()
            
        if st.button("⬅️ Retour aux questions"):
            st.session_state.etape = 3
            st.rerun()

    conn.close()
