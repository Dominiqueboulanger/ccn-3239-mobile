import streamlit as st
import sqlite3

# Config mobile
st.set_page_config(page_title="Expert CCN - Mobile", layout="centered")

st.title("📖 CCN 3239 - Français Facile")
st.write("Niveau A2 - Simplifié pour les apprenants")

def get_data(num):
    conn = sqlite3.connect("CCN_3239.db")
    cur = conn.cursor()
    cur.execute("SELECT numero_article_isole, texte_integral, texte_simplifie FROM convention_collective WHERE numero_article_isole = ?", (num,))
    res = cur.fetchone()
    conn.close()
    return res

num = st.text_input("Tapez un numéro d'article :", placeholder="Ex: 41")

if num:
    article = get_data(num.strip())
    if article:
        n, officiel, simple = article
        st.subheader(f"Article {n}")
        
        st.info("💡 **Version Simplifiée :**")
        if simple:
            st.write(simple)
        else:
            st.write("_Pas encore de version simplifiée pour cet article._")
            
        with st.expander("📄 Voir le texte officiel"):
            st.write(officiel)
    else:
        st.error("Article non trouvé.")
