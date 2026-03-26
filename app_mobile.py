import streamlit as st
import sqlite3
import os

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Assistant CCN 3239", layout="centered")

DB_PATH = "CCN_3239.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

# --- MATRICE DE L'ENTONNOIR (VOS QUESTIONS) ---
ARBRE_DECISION = {
    "TITRE 1  Formation du contrat de travail": {
        "📝 Rédaction du contrat": {
            "question": "Quel aspect de la rédaction vous intéresse ?",
            "reponses": {
                "Forme du contrat (Écrit ou oral)": ["140-1", "140-2", "140-3"],
                "Objet du contrat (Les missions)": ["140-4"],
                "Nature du contrat (CDI, CDD...)": ["140-5", "140-6", "140-7"],
                "Formalités (Immatriculation, CESU...)": ["141-1", "141-2", "141-3", "141-4"]
            }
        },
        "⏳ Période d’essai": {
            "question": "Que souhaitez-vous savoir sur l'essai ?",
            "reponses": {
                "Mise en place et durée": ["44-1-1", "44-1-2", "44-1-3"],
                "Rupture de l'essai (Délais)": ["44-1-4"]
            }
        }
    },
    "TITRE 2  Rupture du contrat de travail": {
        "🚪 Modes de rupture": {
            "question": "Quel type de départ vous intéresse ?",
            "reponses": {
                "Départ à la retraite": ["63-1-1"],
                "Démission (Salarié)": ["63-2-1"],
                "Licenciement (Employeur)": ["161", "162"],
                "Rupture conventionnelle": ["63-3-1"]
            }
        },
        "💰 Indemnités et Préavis": {
            "question": "Sur quel calcul porte votre question ?",
            "reponses": {
                "Calcul du préavis": ["162"],
                "Indemnité de licenciement": ["163"],
                "Solde de tout compte": ["164"]
            }
        },
        "🏠 Logement de fonction": {
            "question": "Que devient le logement à la fin ?",
            "reponses": {
                "Restitution du logement": ["168"]
            }
        }
    }
}

# --- STYLE CSS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; font-weight: bold; margin-bottom: 8px; border: 2px solid #dcdde1; }
    .question-box { background-color: #f1f2f6; padding: 20px; border-radius: 15px; border-left: 8px solid #1e3799; margin-bottom: 20px; }
    .essentiel-box { background-color: #ecfdf5; border-left: 5px solid #27ae60; padding: 18px; border-radius: 10px; font-size: 18px; }
    .titre-art { color: #1e3799; font-weight: bold; font-size: 20px; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Assistant CCN 3239")

if not os.path.exists(DB_PATH):
    st.error("Base de données introuvable.")
else:
    if 'etape' not in st.session_state:
        st.session_state.etape = 1
        st.session_state.choix = {}

    conn = get_connection()

    # --- ÉTAPE 1 : SITUATION (DÉBUT/FIN) ---
    if st.session_state.etape == 1:
        st.markdown("<div class='question-box'><h3>1. Quelle est la situation ?</h3></div>", unsafe_allow_html=True)
        if st.button("🐣 Début de contrat"):
            st.session_state.choix['titre'] = "TITRE 1  Formation du contrat de travail"
            st.session_state.etape = 2
            st.rerun()
        if st.button("🏁 Fin de contrat"):
            st.session_state.choix['titre'] = "TITRE 2  Rupture du contrat de travail"
            st.session_state.etape = 2
            st.rerun()

    # --- ÉTAPE 2 : MÉTIER ---
    elif st.session_state.etape == 2:
        st.markdown("<div class='question-box'><h3>2. Pour quel métier ?</h3></div>", unsafe_allow_html=True)
        metiers = {
            "🧸 Assistant Maternel": "SOCLE ASSISTANT MATERNEL",
            "👶 Assistant Parental": "SOCLE SALARIÉ DU PARTICULIER EMPLOYEUR",
            "🧹 Employé Familial": "SOCLE SALARIÉ DU PARTICULIER EMPLOYEUR",
            "👨‍🦽 Assistant de Vie": "SOCLE SALARIÉ DU PARTICULIER EMPLOYEUR"
        }
        for label, socle in metiers.items():
            if st.button(label):
                st.session_state.choix['socle'] = socle
                st.session_state.etape = 3
                st.rerun()
        if st.button("⬅️ Retour"):
            st.session_state.etape = 1
            st.rerun()

    # --- ÉTAPE 3 : ENTONNOIR (THÈME -> QUESTION) ---
    elif st.session_state.etape == 3:
        titre_sel = st.session_state.choix['titre']
        themes = ARBRE_DECISION.get(titre_sel, {})
        
        if 'theme' not in st.session_state.choix:
            st.markdown("<div class='question-box'><h3>3. Choisissez un thème :</h3></div>", unsafe_allow_html=True)
            for t in themes.keys():
                if st.button(t):
                    st.session_state.choix['theme'] = t
                    st.rerun()
        else:
            theme_sel = st.session_state.choix['theme']
            st.markdown(f"<div class='question-box'><h3>{themes[theme_sel]['question']}</h3></div>", unsafe_allow_html=True)
            for rep_label, articles in themes[theme_sel]['reponses'].items():
                if st.button(rep_label):
                    st.session_state.choix['articles_selectionnes'] = articles
                    st.session_state.etape = 4
                    st.rerun()
        
        if st.button("⬅️ Retour"):
            if 'theme' in st.session_state.choix: del st.session_state.choix['theme']
            else: st.session_state.etape = 2
            st.rerun()

    # --- ÉTAPE 4 : CHOIX DE L'ARTICLE PRÉCIS ---
    elif st.session_state.etape == 4:
        st.markdown("<div class='question-box'><h3>4. Sélectionnez l'article :</h3></div>", unsafe_allow_html=True)
        nums = st.session_state.choix['articles_selectionnes']
        socle_sel = st.session_state.choix['socle']

        for n in nums:
            # Récupérer le titre de l'article pour le bouton
            res = conn.execute("SELECT affichage_article FROM convention_collective WHERE numero_article_isole = ? AND socle = ?", (n, socle_sel)).fetchone()
            titre_art = res[0] if res else f"Article {n}"
            
            if st.button(f"📄 Art. {n} - {titre_art}"):
                st.session_state.choix['article_final'] = n
                st.session_state.etape = 5
                st.rerun()

        if st.button("⬅️ Retour"):
            st.session_state.etape = 3
            st.rerun()

   # --- ÉTAPE 5 : AFFICHAGE DE LA RÉPONSE FINALE ---
    elif st.session_state.etape == 5:
        num = st.session_state.choix['article_final']
        socle = st.session_state.choix['socle']
        
        # Récupération de l'article précis dans la base
        query = """
            SELECT affichage_article, texte_integral, texte_simplifie 
            FROM convention_collective 
            WHERE numero_article_isole = ? AND socle = ?
        """
        res = conn.execute(query, (num, socle)).fetchone()
        
        if res:
            titre, integral, simplifie = res
            
            # Entête de la fiche
            st.markdown(f"### Article {num}")
            st.markdown(f"<div class='titre-art'>{titre}</div>", unsafe_allow_html=True)
            st.divider()

            # LOGIQUE D'AFFICHAGE :
            # On vérifie si le résumé (A2) existe et n'est pas juste des espaces
            has_simplifie = simplifie and simplifie.strip()

            if has_simplifie:
                # 1. On affiche le résumé en priorité
                st.markdown("#### 💡 L'essentiel à retenir")
                st.markdown(f"<div class='essentiel-box'>{simplifie}</div>", unsafe_allow_html=True)
                
                # 2. On propose le texte intégral dans un bouton dépliant (expander)
                st.write("") # Espacement
                with st.expander("⚖️ Consulter le texte intégral officiel"):
                    st.markdown(integral)
            else:
                # 3. Si pas de résumé, on affiche le texte intégral directement
                st.markdown("#### ⚖️ Texte officiel")
                st.markdown(f"<div class='essentiel-box'>{integral}</div>", unsafe_allow_html=True)
                st.info("Note : Aucune version simplifiée n'est disponible pour cet article.")

        # Bouton de sortie pour revenir au début
        st.write("")
        if st.button("🔄 Faire une autre recherche"):
            # On réinitialise tout sauf la connexion
            for key in list(st.session_state.keys()):
                if key != 'etape': del st.session_state[key]
            st.session_state.etape = 1
            st.rerun()

    conn.close()
