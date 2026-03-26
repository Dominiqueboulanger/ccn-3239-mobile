import streamlit as st
import sqlite3
from pathlib import Path

# --- CONFIGURATION ---
st.set_page_config(page_title="Assistant CCN 3239", layout="centered")

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "CCN_3239.db"

def get_connection():
    return sqlite3.connect(str(DB_PATH))

# --- STYLE CSS (Inchangé) ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.8em; font-weight: bold; margin-bottom: 12px; border: 2px solid #dcdde1; white-space: normal; }
    .question-box { background-color: #f8f9fa; padding: 20px; border-radius: 15px; border-left: 8px solid #1e3799; margin-bottom: 25px; }
    .essentiel-box { background-color: #ecfdf5; border-left: 5px solid #27ae60; padding: 20px; border-radius: 10px; font-size: 18px; color: #1e272e; }
    .titre-art { color: #1e3799; font-weight: bold; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIQUE DE NAVIGATION (L'ENTONNOIR) ---
if 'etape' not in st.session_state:
    st.session_state.etape = 1
    st.session_state.choix = {}

conn = get_connection()

try:
    # ETAPE 1 : LA THÉMATIQUE (Vie du contrat, Rupture, etc.)
    if st.session_state.etape == 1:
        st.markdown("<div class='question-box'><h3>1. Que souhaitez-vous aborder ?</h3></div>", unsafe_allow_html=True)
        # On récupère les thèmes (ex: Vie du contrat, Rupture...)
        themes = conn.execute("SELECT DISTINCT theme FROM navigation_pedagogique ORDER BY theme").fetchall()
        for t in themes:
            if st.button(t[0]):
                st.session_state.choix['theme'] = t[0]
                st.session_state.etape = 2
                st.rerun()

    # ETAPE 2 : LE MÉTIER (Le filtre de socle)
    elif st.session_state.etape == 2:
        st.markdown(f"<div class='question-box'><h3>2. Quel est le métier concerné ?</h3><p>Thème : {st.session_state.choix['theme']}</p></div>", unsafe_allow_html=True)
        metiers = {
            "🧸 Assistant Maternel": "SOCLE ASSISTANT MATERNEL",
            "👶 Assistant Parental (Garde d'enfants)": "SOCLE SALARIÉ DU PARTICULIER EMPLOYEUR",
            "🛠 Autres / Dispositions Communes": "DISPOSITIONS COMMUNES"
        }
        for label, socle_val in metiers.items():
            if st.button(label):
                st.session_state.choix['socle'] = socle_val
                st.session_state.etape = 3
                st.rerun()
        if st.button("⬅️ Retour"):
            st.session_state.etape = 1
            st.rerun()

    # ETAPE 3 : LA QUESTION PRÉCISE (Les boutons issus de W1)
    elif st.session_state.etape == 3:
        theme_sel = st.session_state.choix['theme']
        st.markdown(f"<div class='question-box'><h3>3. Précisez votre recherche</h3></div>", unsafe_allow_html=True)
        
        query = "SELECT reponse_bouton, articles_lies FROM navigation_pedagogique WHERE theme = ?"
        options = conn.execute(query, (theme_sel,)).fetchall()

        for label_bouton, art_id in options:
            if st.button(label_bouton):
                st.session_state.choix['article_id'] = art_id
                st.session_state.etape = 4
                st.rerun()
        
        if st.button("⬅️ Retour"):
            st.session_state.etape = 2
            st.rerun()

    # ETAPE 4 : AFFICHAGE FINAL
    elif st.session_state.etape == 4:
        art_id = str(st.session_state.choix['article_id']).strip()
        socle_user = st.session_state.choix['socle']
        
        # On cherche l'article correspondant au métier
        query = "SELECT affichage_article, texte_integral, texte_simplifie FROM convention_collective WHERE numero_article_isole = ? AND socle = ?"
        res = conn.execute(query, (art_id, socle_user)).fetchone()
        
        # Si pas trouvé dans ce socle, on cherche dans les dispositions communes (fallback)
        if not res:
            res = conn.execute("SELECT affichage_article, texte_integral, texte_simplifie FROM convention_collective WHERE numero_article_isole = ? LIMIT 1", (art_id,)).fetchone()

        if res:
            titre, integral, simplifie = res
            st.markdown(f"<div class='titre-art'>Article {art_id}</div>", unsafe_allow_html=True)
            st.write(f"**{titre}**")
            
            # Affichage de l'Essentiel (A2)
            if simplifie and len(str(simplifie)) > 10:
                st.success("💡 L'ESSENTIEL (Niveau A2)")
                st.markdown(f"<div class='essentiel-box'>{simplifie}</div>", unsafe_allow_html=True)
                # Texte officiel en expander
                with st.expander("⚖️ Consulter le texte officiel intégral"):
                    st.markdown(integral)
            else:
                # Si pas de résumé, texte officiel direct
                st.info("⚖️ TEXTE OFFICIEL")
                st.markdown(f"<div class='essentiel-box'>{integral}</div>", unsafe_allow_html=True)
        else:
            st.error("Détails de l'article introuvables.")

        if st.button("🔄 Nouvelle recherche"):
            st.session_state.etape = 1
            st.session_state.choix = {}
            st.rerun()

finally:
    conn.close()
