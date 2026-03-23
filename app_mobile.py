import streamlit as st
import sqlite3

st.title("Diagnostic de la Base de Données")

try:
    conn = sqlite3.connect("CCN_3239.db")
    # Cette ligne liste les tables réellement présentes dans votre fichier
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    conn.close()

    if tables:
        st.success(f"Fichier trouvé ! Voici les tables disponibles :")
        for t in tables:
            st.code(t[0])
        st.info("Copiez le nom qui s'affiche ci-dessus et donnez-le moi.")
    else:
        st.error("Le fichier est vide ou ne contient aucune table.")
except Exception as e:
    st.error(f"Erreur : {e}")
