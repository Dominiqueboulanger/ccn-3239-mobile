import streamlit as st
import sqlite3

st.title("🔍 Diagnostic des Colonnes")

try:
    conn = sqlite3.connect("CCN_3239.db")
    # On demande les noms de toutes les colonnes de la table
    cursor = conn.execute("SELECT * FROM convention_collective LIMIT 1")
    colonnes = [description[0] for description in cursor.description]
    conn.close()

    st.success("Table 'convention_collective' analysée !")
    st.write("Voici les noms exacts de vos colonnes :")
    for col in colonnes:
        st.code(col)
        
except Exception as e:
    st.error(f"Erreur : {e}")
