import streamlit as st
import sqlite3
import os

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Assistant CCN 3239", layout="centered")

DB_PATH = "CCN_3239.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

# --- LA MATRICE DES RÉPONSES (L'ENTONNOIR) ---
# Cette structure fait le lien entre vos questions et les articles de la base
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
    .stButton>button { width: 100%; border-radius: 12px; height: 3.8em; font-weight: bold; margin-bottom: 10px; border: 2px solid #dcdde1; }
    .question-box { background-color: #f1f2f6; padding: 20px; border-radius: 15px; border-left: 8px solid #1e3799; margin-bottom: 25px; }
    .essentiel-box { background-color: #ecfdf5; border-left: 5px solid #27ae60; padding: 18px; border-radius: 10px; font-size: 17px; }
    .titre-art { color: #1e3799; font-weight: bold; font-size: 19px; margin-top: 15px; }
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

    # --- ÉTAPE 1 : SITUATION (DÉBUT / FIN) ---
    if st.session_state.etape == 1:
        st.markdown("<div class='question-box'><h3>1. Quelle est la situation ?</h3></div>", unsafe_allow_html=True)
        if st.button("🐣 Début de contrat (Embauche, essai...)"):
            st.session_state.choix['titre'] = "TITRE 1  Formation du contrat de travail"
            st.session_state.etape = 2
            st.rerun()
        if st.button("🏁 Fin de contrat (Rupture, préavis...)"):
            st.session_state.choix['titre'] = "TITRE 2  Rupture du contrat de travail"
            st.session_state.etape = 2
            st.rerun()

    # --- ÉTAPE 2 : LE MÉTIER ---
    elif st.session_state.etape == 2:
        st.markdown("<div class='question-box'><h3>2. Pour quel métier ?</h3></div>", unsafe_allow_html=True)
        metiers = {
            "🧸 Assistant Maternel": "SOCLE ASSISTANT MATERNEL",
            "👶 Assistant Parental (Garde d'enfants)": "SOCLE SALARIÉ DU PARTICULIER EMPLOYEUR",
            "🧹 Employé Familial": "SOCLE SALARIÉ DU PARTICULIER EMPLOYEUR",
            "👨‍🦽 Assistant de Vie (Dépendance)": "SOCLE SALARIÉ DU PARTICULIER EMPLOYEUR",
            "🛠 Autres métiers": "DISPOSITIONS COMMUNES"
        }
        for label, socle in metiers.items():
            if st.button(label):
                st.session_state.choix['socle'] = socle
                st.session_state.etape = 3
                st.rerun()
        if st.button("⬅️ Retour"):
            st.session_state.etape = 1
            st.rerun()

    # --- ÉTAPE 3 : THÈME ET QUESTION FERMÉE ---
    elif st.session_state.etape == 3:
        titre_sel = st.session_state.choix['titre']
        themes = ARBRE_DECISION.get(titre_sel, {})
        
        # Si aucun thème n'est encore choisi
        if 'theme' not in st.session_state.choix:
            st.markdown("<div class='question-box'><h3>3. Quel thème vous intéresse ?</h3></div>", unsafe_allow_html=True)
            for theme in themes.keys():
                if st.button(theme):
                    st.session_state.choix['theme'] = theme
                    st.rerun()
        else:
            # On pose la question fermée du sous-thème
            theme_sel = st.session_state.choix['theme']
            question_data = themes[theme_sel]
            st.markdown(f"<div class='question-box'><h3>{question_data['question']}</h3></div>", unsafe_allow_html=True)
            
            for rep_label, articles in question_data['reponses'].items():
                if st.button(rep_label):
                    st.session_state.choix['articles'] = articles
                    st.session_state.etape = 4
                    st.rerun()
        
        if st.button("⬅️ Retour au métier"):
            if 'theme' in st.session_state.choix:
                del st.session_state.choix['theme']
            else:
                st.session_state.etape = 2
            st.rerun()

    # --- ÉTAPE 4 : AFFICHAGE DES ARTICLES ---
    elif st.session_state.etape == 4:
        socle_sel = st.session_state.choix['socle']
        articles_a_chercher = st.session_state.choix['articles']
        
        st.info(f"📍 {st.session_state.choix.get('theme')}")

        for art_num in articles_a_chercher:
            query = "SELECT affichage_article, texte_integral, texte_simplifie FROM convention_collective WHERE numero_article_isole = ? AND socle = ?"
            res = conn.execute(query, (art_num, socle_sel)).fetchone()
            
            if res:
                titre_art, integral, simplifie = res
                st.markdown(f"<div class='titre-art'>Article {art_num} : {titre_art}</div>", unsafe_allow_html=True)
                
                # Affichage intelligent : Simplifié (A2) sinon Intégral
                contenu = simplifie if (simplifie and simplifie.strip()) else integral
                label = "💡 L'ESSENTIEL (A2)" if (simplifie and simplifie.strip()) else "⚖️ TEXTE OFFICIEL"
                
                st.markdown(f"**{label}**")
                st.markdown(f"<div class='essentiel-box'>{contenu}</div>", unsafe_allow_html=True)
                
                if simplifie and simplifie.strip():
                    with st.expander("Consulter le texte juridique complet"):
                        st.write(integral)
                st.divider()

        if st.button("🔄 Nouvelle recherche"):
            st.session_state.etape = 1
            st.session_state.choix = {}
            st.rerun()

    conn.close()
