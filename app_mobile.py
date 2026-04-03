import streamlit as st
import sqlite3

# Configuration de la page pour mobile
st.set_page_config(page_title="Consultation CCN 3239", layout="centered")

# Connexion à la base de données
def charger_donnees():
    conn = sqlite3.connect("CCN_3239.db")
    conn.row_factory = sqlite3.Row
    return conn

conn = charger_donnees()
cursor = conn.cursor()

# --- INTERFACE STREAMLIT ---
st.title("📖 Guide CCN 3239")
st.subheader("Espace Apprenants")

# 1. Barre de recherche intelligente
recherche = st.text_input("🔍 Rechercher un mot-clé ou un numéro d'article", "")

# 2. Filtre par Chapitre / Titre
cursor.execute("SELECT DISTINCT titres FROM convention_collective")
categories = [row[0] for row in cursor.fetchall() if row[0]]
categorie_choisie = st.selectbox("📂 Filtrer par thématique", ["Tous"] + categories)

# Construction de la requête SQL
query = "SELECT * FROM convention_collective WHERE 1=1"
params = []

if recherche:
    query += " AND (texte_integral LIKE ? OR affichage_article LIKE ?)"
    params.extend([f"%{recherche}%", f"%{recherche}%"])

if categorie_choisie != "Tous":
    query += " AND titres = ?"
    params.append(categorie_choisie)

# 3. Affichage des résultats
cursor.execute(query, params)
articles = cursor.fetchall()

st.write(f"**{len(articles)} article(s) trouvé(s)**")

for art in articles:
    # On crée une boîte extensible pour chaque article
    with st.expander(f"📌 {art['affichage_article']}"):
        st.info(f"**L'essentiel :**\n\n{art['texte_simplifie']}")
        
        # Bouton pour voir le texte officiel si besoin
        if st.checkbox("Voir le texte intégral", key=art['id']):
            st.caption("⚖️ Texte Officiel :")
            st.write(art['texte_integral'])
