import streamlit as st
import sqlite3

# Configuration de la page
st.set_page_config(page_title="Expert CCN - Mobile", layout="centered")

# Style CSS pour rendre l'affichage plus propre
st.markdown("""
    <style>
    .stRadio [data-testid="stMarkdownContainer"] p {
        font-size: 18px;
        font-weight: bold;
    }
    .article-header {
        color: #1e3799;
        border-bottom: 2px solid #1e3799;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📖 CCN 3239 - Français Facile")
st.write("Niveau A2 - Simplifié pour les apprenants")

def get_connection():
    return sqlite3.connect("CCN_3239.db")

conn = get_connection()

try:
    # 1. Menu Partie (Radio)
    parties = [r[0] for r in conn.execute("SELECT DISTINCT partie FROM convention_collective WHERE partie IS NOT NULL").fetchall()]
    partie_sel = st.radio("1. Choisissez une Partie :", ["---"] + parties)

    if partie_sel != "---":
        # 2. Menu Socle (Radio)
        socles = [r[0] for r in conn.execute("SELECT DISTINCT socle FROM convention_collective WHERE partie = ?", (partie_sel,)).fetchall()]
        socle_sel = st.radio("2. Choisissez un Socle :", ["---"] + socles)

        if socle_sel != "---":
            # 3. Menu Chapitres (Radio)
            chaps = [r[0] for r in conn.execute("SELECT DISTINCT chapitres FROM convention_collective WHERE partie = ? AND socle = ?", (partie_sel, socle_sel)).fetchall()]
            chap_sel = st.radio("3. Choisissez un Chapitre :", ["---"] + chaps)

            if chap_sel != "---":
                # 4. Menu Articles (On utilise la nouvelle colonne 'affichage_article')
                articles = conn.execute("""
                    SELECT affichage_article, numero_article_isole 
                    FROM convention_collective 
                    WHERE partie = ? AND socle = ? AND chapitres = ?
                """, (partie_sel, socle_sel, chap_sel)).fetchall()
                
                # On crée un dictionnaire pour retrouver le numéro d'article à partir du titre choisi
                dict_articles = {a[0]: a[1] for a in articles}
                
                # Selectbox pour les articles (plus pratique si la liste est longue)
                art_affiche = st.selectbox("4. Sélectionnez l'Article :", ["---"] + list(dict_articles.keys()))

                if art_affiche != "---":
                    num_art = dict_articles[art_affiche]
                    res = conn.execute("SELECT texte_integral, texte_simplifie FROM convention_collective WHERE numero_article_isole = ?", (num_art,)).fetchone()
                    
                    if res:
                        officiel, simple = res
                        st.divider()
                        # Affichage du titre propre extrait de la base
                        st.markdown(f"<h2 class='article-header'>{art_affiche}</h2>", unsafe_allow_html=True)
                        
                        st.info("💡 **Version Simplifiée :**")
                        if simple and simple.strip():
                            st.write(simple)
                        else:
                            st.write("_Pas encore de version simplifiée pour cet article._")
                        
                        with st.expander("📄 Voir le texte officiel"):
                            st.write(officiel)

except Exception as e:
    st.error(f"Erreur d'accès aux données : {e}")

finally:
    conn.close()
