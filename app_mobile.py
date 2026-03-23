import streamlit as st
import sqlite3

# Configuration large pour mobile
st.set_page_config(page_title="Expert CCN - Mobile", layout="centered")

st.title("📖 CCN 3239 - Français Facile")

def get_connection():
    return sqlite3.connect("CCN_3239.db")

conn = get_connection()

try:
    # 1. Menu Partie (Radio bouton = Pas de clavier)
    parties = [r[0] for r in conn.execute("SELECT DISTINCT partie FROM convention_collective WHERE partie IS NOT NULL").fetchall()]
    partie_sel = st.radio("1. Choisissez une Partie :", ["---"] + parties)

    if partie_sel != "---":
        # 2. Menu Socle
        socles = [r[0] for r in conn.execute("SELECT DISTINCT socle FROM convention_collective WHERE partie = ?", (partie_sel,)).fetchall()]
        socle_sel = st.radio("2. Choisissez un Socle :", ["---"] + socles)

        if socle_sel != "---":
            # 3. Menu Chapitres
            chaps = [r[0] for r in conn.execute("SELECT DISTINCT chapitres FROM convention_collective WHERE partie = ? AND socle = ?", (partie_sel, socle_sel)).fetchall()]
            chap_sel = st.radio("3. Choisissez un Chapitre :", ["---"] + chaps)

            if chap_sel != "---":
                # 4. Menu Articles (On garde Selectbox ici car la liste peut être longue)
                articles = conn.execute("SELECT numero_article_isole, titres FROM convention_collective WHERE partie = ? AND socle = ? AND chapitres = ?", (partie_sel, socle_sel, chap_sel)).fetchall()
                dict_articles = {f"Art. {a[0]} - {a[1]}": a[0] for a in articles}
                
                # Astuce : On utilise une clé unique pour éviter les conflits
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

except Exception as e:
    st.error(f"Erreur : {e}")

conn.close()
