import streamlit as st
import sqlite3

st.set_page_config(page_title="Guide CCN 3239", layout="centered")

# --- STYLE PERSONNALISÉ POUR MOBILE ---
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        height: 60px;
        font-size: 18px;
        margin-bottom: 10px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("⚖️ Mon Assistant CCN 3239")

# --- INITIALISATION DES ÉTAPES ---
if 'etape' not in st.session_state:
    st.session_state.etape = 1
    st.session_state.socle = None

# --- ÉTAPE 1 : LE MÉTIER ---
if st.session_state.etape == 1:
    st.subheader("1️⃣ Quel est votre métier ?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🍼 Assistant Maternel"):
            st.session_state.socle = "AM" # Articles 89-126
            st.session_state.etape = 2
            st.rerun()
        if st.button("🏠 Employé Familial"):
            st.session_state.socle = "EF" # Articles 126-168
            st.session_state.etape = 2
            st.rerun()
            
    with col2:
        if st.button("👵 Assistant de Vie"):
            st.session_state.socle = "PE" # Particulier Employeur
            st.session_state.etape = 2
            st.rerun()
        if st.button("🌳 Autres (Jardinier...)"):
            st.session_state.socle = "SC" # Socle Commun
            st.session_state.etape = 2
            st.rerun()

# --- ÉTAPE 2 : LA SITUATION ---
elif st.session_state.etape == 2:
    st.subheader("2️⃣ Votre situation")
    st.info(f"Métier sélectionné : {st.session_state.socle}")
    
    if st.button("🛑 Souhaitez-vous mettre fin au contrat ?"):
        st.session_state.etape = 3 # Vers Rupture
        st.rerun()
    
    if st.button("📝 Question sur l'exécution du contrat"):
        st.session_state.etape = 10 # Vers thèmes classiques (Exécution)
        st.rerun()
    
    if st.button("⬅️ Retour"):
        st.session_state.etape = 1
        st.rerun()

# --- ÉTAPE 3 : TYPE DE CONTRAT (Si rupture) ---
elif st.session_state.etape == 3:
    st.subheader("3️⃣ Type de contrat")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 CDI"):
            st.session_state.type_contrat = "CDI"
            st.session_state.etape = 4
            st.rerun()
    with col2:
        if st.button("⏳ CDD"):
            # Ici, redirection directe vers l'article CDD (ex: 62 pour Socle Commun)
            st.session_state.target_article = 62 
            st.session_state.etape = "FINAL"
            st.rerun()

# --- ÉTAPE FINALE : AFFICHAGE ---
elif st.session_state.etape == "FINAL":
    # Logique SQL pour aller chercher l'article target_article
    st.success("Voici l'article correspondant à votre situation :")
    # Affichage de l'article...
    if st.button("🔄 Recommencer"):
        st.session_state.clear()
        st.rerun()
