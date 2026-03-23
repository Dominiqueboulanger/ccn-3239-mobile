import streamlit as st
import sqlite3

# Configuration pour éviter le zoom et améliorer le tactile
st.set_page_config(page_title="Expert CCN - Mobile", layout="centered")

# CSS pour empêcher le clavier de s'ouvrir sur les menus déroulants
st.markdown("""
    <style>
    div[data-baseweb="select"] input {
        caret-color: transparent !important;
        pointer-events: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📖 CCN 3239 - Français Facile")

def get_connection():
    return sqlite3.connect("CCN_3239.db")

conn = get_connection()

try:
    # 1. Menu Partie
    parties = [r[0] for r in conn.execute("SELECT DISTINCT partie FROM convention_collective WHERE partie IS NOT NULL").fetchall()]
    partie_sel = st.selectbox("1. Choisissez une Partie :", ["---"] + parties)

    if partie_sel != "---":
        # 2. Menu Socle
        socles = [r[0] for r in conn.execute("SELECT DISTINCT socle FROM convention_collective WHERE partie = ?", (partie_sel,)).fetchall()]
        socle_sel = st.selectbox("2. Choisissez un Socle :", ["---"] + socles)

        if socle_sel != "---":
            # 3. Menu Chapitres - On utilise une liste plus compacte
            chaps = [r[0] for r in conn.execute("SELECT DISTINCT chapitres FROM convention_collective WHERE partie = ? AND socle = ?", (partie_sel, socle_sel)).fetchall()]
            chap_sel = st.selectbox("3. Choisissez un Chapitre :", ["---"] + chaps)

            if chap_sel != "---":
                # 4. Articles
                articles = conn.execute("SELECT numero_article_isole, titres FROM convention_collective WHERE partie = ? AND socle = ? AND chapitres = ?", (partie_sel, socle_sel, chap_sel)).fetchall()
                dict_articles = {f"Art. {a[0]} - {a[1]}": a[0] for a in articles}
                
                art_affiche = st.selectbox("4. Sélectionnez l'Article :", ["---"] + list(dict_articles.keys()))

                if art_affiche != "---":
                    num_art = dict_articles[art_affiche]
                    res = conn.execute("SELECT texte_integral, texte_simplifie FROM convention_collective WHERE numero_article_isole = ?", (num_art,)).fetchone()
                    
                    if res:
                        officiel, simple = res
                        st.divider()
                        st.subheader(f"Article {num_art}")
                        st.info("💡 **Version Simplifiée :**")
                        st.write(simple if (simple and simple.strip()) else "_Pas encore de version simplifiée._")
                        with st.expander("📄 Voir le texte officiel"):
                            st.write(officiel)
                else:
                    # Espace vide pour forcer le menu précédent à s'ouvrir vers le bas
                    st.write(" " * 100)
                    for _ in range(15): st.write("\n")

except Exception as e:
    st.error(f"Erreur : {e}")

conn.close()
