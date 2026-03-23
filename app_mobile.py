import streamlit as st
import sqlite3

# Configuration de la page
st.set_page_config(page_title="Expert CCN - Mobile", layout="centered")

st.title("📖 CCN 3239 - Français Facile")
st.write("Niveau A2 - Simplifié pour les apprenants")

def get_connection():
    return sqlite3.connect("CCN_3239.db")

# --- SYSTÈME DE FILTRES ---

conn = get_connection()

# 1. Filtre par Partie
parties = [r[0] for r in conn.execute("SELECT DISTINCT partie FROM convention_collective WHERE partie IS NOT NULL").fetchall()]
partie_sel = st.selectbox("1. Choisissez une Partie :", ["---"] + parties)

if partie_sel != "---":
    # 2. Filtre par Socle (dépendant de la partie)
    socles = [r[0] for r in conn.execute("SELECT DISTINCT socle FROM convention_collective WHERE partie = ?", (partie_sel,)).fetchall()]
    socle_sel = st.selectbox("2. Choisissez un Socle :", ["---"] + socles)

    if socle_sel != "---":
        # 3. Filtre par Chapitre (dépendant du socle)
        chapitres = [r[0] for r in conn.execute("SELECT DISTINCT chapitre FROM convention_collective WHERE partie = ? AND socle = ?", (partie_sel, socle_sel)).fetchall()]
        chap_sel = st.selectbox("3. Choisissez un Chapitre :", ["---"] + chapitres)

        if chap_sel != "---":
            # 4. Menu déroulant des Articles
            articles = conn.execute("SELECT numero_article_isole, titre_article FROM convention_collective WHERE partie = ? AND socle = ? AND chapitre = ?", (partie_sel, socle_sel, chap_sel)).fetchall()
            
            # On crée une liste lisible pour le menu : "Article 45 - Durée du travail"
            dict_articles = {f"Article {a[0]} - {a[1]}": a[0] for a in articles}
            art_affiche = st.selectbox("4. Sélectionnez l'Article :", ["---"] + list(dict_articles.keys()))

            if art_affiche != "---":
                num_art = dict_articles[art_affiche]
                
                # --- AFFICHAGE DE L'ARTICLE ---
                res = conn.execute("SELECT texte_integral, texte_simplifie FROM convention_collective WHERE numero_article_isole = ?", (num_art,)).fetchone()
                
                if res:
                    officiel, simple = res
                    st.divider()
                    st.subheader(f"Article {num_art}")
                    
                    st.info("💡 **Version Simplifiée :**")
                    if simple:
                        st.write(simple)
                    else:
                        st.write("_Pas encore de version simplifiée pour cet article._")
                        
                    with st.expander("📄 Voir le texte officiel"):
                        st.write(officiel)

conn.close()
