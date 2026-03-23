import streamlit as st
import sqlite3

# Configuration de la page mobile
st.set_page_config(page_title="Expert CCN - Mobile", layout="centered")
st.title("📖 CCN 3239 - Français Facile")

def get_connection():
    # Connexion au FICHIER
    return sqlite3.connect("CCN_3239.db")

conn = get_connection()

try:
    # On interroge la TABLE 'ccn_3239'
    parties = [r[0] for r in conn.execute("SELECT DISTINCT partie FROM ccn_3239 WHERE partie IS NOT NULL").fetchall()]
    partie_sel = st.selectbox("1. Choisissez une Partie :", ["---"] + parties)

    if partie_sel != "---":
        socles = [r[0] for r in conn.execute("SELECT DISTINCT socle FROM ccn_3239 WHERE partie = ?", (partie_sel,)).fetchall()]
        socle_sel = st.selectbox("2. Choisissez un Socle :", ["---"] + socles)

        if socle_sel != "---":
            chapitres = [r[0] for r in conn.execute("SELECT DISTINCT chapitre FROM ccn_3239 WHERE partie = ? AND socle = ?", (partie_sel, socle_sel)).fetchall()]
            chap_sel = st.selectbox("3. Choisissez un Chapitre :", ["---"] + chapitres)

            if chap_sel != "---":
                articles = conn.execute("SELECT numero_article_isole, titre_article FROM ccn_3239 WHERE partie = ? AND socle = ? AND chapitre = ?", (partie_sel, socle_sel, chap_sel)).fetchall()
                
                # Création de la liste pour le menu
                dict_articles = {f"Article {a[0]} - {a[1]}": a[0] for a in articles}
                art_affiche = st.selectbox("4. Sélectionnez l'Article :", ["---"] + list(dict_articles.keys()))

                if art_affiche != "---":
                    num_art = dict_articles[art_affiche]
                    res = conn.execute("SELECT texte_integral, texte_simplifie FROM ccn_3239 WHERE numero_article_isole = ?", (num_art,)).fetchone()
                    
                    if res:
                        officiel, simple = res
                        st.divider()
                        st.subheader(f"Article {num_art}")
                        
                        st.info("💡 **Version Simplifiée (A2) :**")
                        st.write(simple if simple else "_Pas encore de version simplifiée pour cet article._")
                        
                        with st.expander("📄 Voir le texte officiel"):
                            st.write(officiel)

except Exception as e:
    st.error(f"Erreur d'accès aux données : {e}")
    st.warning("Vérifiez que le fichier CCN_3239.db est bien présent sur GitHub.")

conn.close()
