import streamlit as st
import sqlite3
import os

# Configuration de la page mobile
st.set_page_config(page_title="CCN 3239 - Contrat de Travail", layout="centered")

DB_PATH = "CCN_3239.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

# --- STYLE PERSONNALISÉ ---
st.markdown("""
    <style>
    .titre-article { color: #1e3799; font-size: 20px; font-weight: bold; }
    .label-essentiel { background-color: #ecfdf5; border-left: 5px solid #27ae60; padding: 15px; margin-bottom: 20px; }
    .label-integral { background-color: #f8f9fa; border-left: 5px solid #7f8c8d; padding: 10px; font-size: 14px; color: #333; }
    </style>
    """, unsafe_allow_html=True)

st.title("📱 CCN 3239 : Partie IV")
st.subheader("Le Contrat de Travail")

if not os.path.exists(DB_PATH):
    st.error("Base de données introuvable. Veuillez placer CCN_3239.db dans le dossier.")
else:
    conn = get_connection()
    
    # 1. Sélection du SOCLE (uniquement pour la Partie IV)
    socles = [r[0] for r in conn.execute("SELECT DISTINCT socle FROM convention_collective WHERE partie LIKE '%PARTIE IV%' ORDER BY id").fetchall()]
    selected_socle = st.selectbox("📌 Choisissez votre Socle :", socles)

    if selected_socle:
        # 2. Sélection du TITRE
        titres = [r[0] for r in conn.execute("SELECT DISTINCT titres FROM convention_collective WHERE socle = ? AND partie LIKE '%PARTIE IV%' ORDER BY id", (selected_socle,)).fetchall()]
        selected_titre = st.selectbox("📁 Titre :", titres)

        if selected_titre:
            # 3. Sélection du CHAPITRE
            chapitres = [r[0] for r in conn.execute("SELECT DISTINCT chapitres FROM convention_collective WHERE titres = ? AND socle = ? AND partie LIKE '%PARTIE IV%' ORDER BY id", (selected_titre, selected_socle)).fetchall()]
            selected_chap = st.selectbox("📖 Chapitre :", chapitres)

            if selected_chap:
                # 4. Sélection de l'ARTICLE
                articles = conn.execute("SELECT numero_article_isole, affichage_article FROM convention_collective WHERE chapitres = ? AND titres = ? AND socle = ? ORDER BY id", (selected_chap, selected_titre, selected_socle)).fetchall()
                
                article_labels = {f"Art. {r[0]} - {r[1]}": r[0] for r in articles}
                selected_art_label = st.selectbox("📄 Article :", list(article_labels.keys()))
                
                if selected_art_label:
                    art_num = article_labels[selected_art_label]
                    
                    # AFFICHAGE FINAL
                    data = conn.execute("SELECT texte_integral, texte_simplifie, mots_cles FROM convention_collective WHERE numero_article_isole = ?", (art_num,)).fetchone()
                    
                    if data:
                        integral, simplifie, mots = data
                        
                        st.divider()
                        st.markdown(f"<div class='titre-article'>{selected_art_label}</div>", unsafe_allow_html=True)
                        
                        if mots:
                            st.caption(f"🔍 Mots-clés : {mots}")

                        # Bloc ESSENTIEL (Votre résumé A2)
                        if simplifie:
                            st.markdown("### 💡 L'ESSENTIEL (Niveau A2)")
                            st.markdown(f"<div class='label-essentiel'>{simplifie}</div>", unsafe_allow_html=True)
                        
                        # Bloc TEXTE INTÉGRAL (Détails juridiques)
                        with st.expander("⚖️ Voir le texte intégral officiel"):
                            st.markdown(f"<div class='label-integral'>{integral}</div>", unsafe_allow_html=True)

    conn.close()

# --- BARRE DE RECHERCHE RAPIDE ---
st.sidebar.header("Recherche Rapide")
search_query = st.sidebar.text_input("Mots-clés (ex: licenciement)")
if search_query:
    conn = get_connection()
    results = conn.execute("SELECT numero_article_isole, affichage_article FROM convention_collective WHERE (texte_integral LIKE ? OR mots_cles LIKE ?) AND partie LIKE '%PARTIE IV%' LIMIT 10", (f'%{search_query}%', f'%{search_query}%')).fetchall()
    conn.close()
    
    if results:
        st.sidebar.write("Résultats :")
        for r in results:
            st.sidebar.info(f"Art. {r[0]} : {r[1]}")
    else:
        st.sidebar.warning("Aucun résultat en Partie IV.")
