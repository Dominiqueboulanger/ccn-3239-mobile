import streamlit as st
import sqlite3

# Configuration pour un affichage mobile optimal
st.set_page_config(page_title="Guide CCN 3239", layout="centered")

def get_connection():
    conn = sqlite3.connect("CCN_3239.db")
    conn.row_factory = sqlite3.Row
    return conn

st.title("📖 Mon Assistant CCN 3239")
st.write("Trouvez une réponse simple à vos questions sur la convention collective.")

conn = get_connection()
cursor = conn.cursor()

# --- ÉTAPE 1 : CHOIX DU THÈME ---
# On récupère la liste des thèmes uniques de la table questions_app
cursor.execute("SELECT DISTINCT theme FROM questions_app ORDER BY theme")
themes = [row['theme'] for row in cursor.fetchall()]

theme_choisi = st.selectbox("📂 Choisissez un thème :", ["--- Sélectionner ---"] + themes)

if theme_choisi != "--- Sélectionner ---":
    
    # --- ÉTAPE 2 : CHOIX DE LA QUESTION ---
    # On filtre les questions selon le thème choisi
    cursor.execute("SELECT id, question_claire, article_id FROM questions_app WHERE theme = ?", (theme_choisi,))
    questions = cursor.fetchall()
    
    # Affichage sous forme de boutons ou de liste
    st.subheader("❓ Quelle est votre question ?")
    
    # On crée un dictionnaire pour lier le texte de la question à l'ID de l'article
    dict_questions = {q['question_claire']: q['article_id'] for q in questions}
    
    question_selectionnee = st.radio(
        "Sélectionnez la question qui vous intéresse :",
        options=list(dict_questions.keys())
    )

    if question_selectionnee:
        art_id = dict_questions[question_selectionnee]
        
        # --- ÉTAPE 3 : AFFICHAGE DE L'ARTICLE ---
        # On va chercher les détails dans la table principale convention_collective
        cursor.execute("SELECT * FROM convention_collective WHERE id = ?", (art_id,))
        article = cursor.fetchone()
        
        if article:
            st.divider()
            st.success(f"### ✅ Réponse : {article['affichage_article']}")
            
            # Affichage de la version simplifiée en priorité
            st.markdown("#### 💡 Ce qu'il faut retenir :")
            st.info(article['texte_simplifie'])
            
            # Texte officiel caché par défaut (pour ne pas surcharger l'écran)
            with st.expander("⚖️ Voir le texte officiel (Loi)"):
                st.write(article['texte_integral'])
        else:
            st.error("Désolé, les détails de cet article ne sont pas encore disponibles.")

conn.close()

# --- PIED DE PAGE ---
st.caption("Application pédagogique pour les apprenants du secteur des particuliers employeurs.")
