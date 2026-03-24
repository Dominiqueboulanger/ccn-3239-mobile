import streamlit as st
import sqlite3

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(page_title="Expert CCN - Mobile", layout="centered")

def inject_style(color="#1e3799"):
    st.markdown(f"""
        <style>
        .breadcrumb {{
            background-color: #f0f2f5;
            padding: 10px;
            border-radius: 5px;
            font-size: 14px;
            color: #57606f;
            margin-bottom: 20px;
            border-left: 5px solid {color};
        }}
        .step-title {{
            color: {color};
            font-weight: bold;
            font-size: 20px;
            margin-bottom: 15px;
        }}
        .article-card {{
            background-color: {color};
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        </style>
        """, unsafe_allow_html=True)

# --- 2. GESTION DE LA NAVIGATION (SESSION STATE) ---
if 'step' not in st.session_state:
    st.session_state.step = 1
    st.session_state.choices = {"partie": None, "socle": None, "chapitre": None, "article": None}

def reset_to_step(s):
    st.session_state.step = s
    # Nettoyer les choix suivants si on revient en arrière
    keys = list(st.session_state.choices.keys())
    for i in range(s-1, len(keys)):
        st.session_state.choices[keys[i]] = None

# --- 3. CONNEXION BDD ---
def get_connection():
    return sqlite3.connect("CCN_3239.db")

conn = get_connection()

# --- 4. INTERFACE DYNAMIQUE ---
st.title("📖 Expert CCN 3239")

# Affichage du fil d'Ariane (Le chemin)
if st.session_state.step > 1:
    path = " > ".join([v for v in st.session_state.choices.values() if v])
    st.markdown(f"<div class='breadcrumb'>📍 {path}</div>", unsafe_allow_html=True)
    if st.button("⬅️ Retour à l'étape précédente"):
        reset_to_step(st.session_state.step - 1)
        st.rerun()

# --- ÉTAPE 1 : CHOIX DE LA PARTIE ---
if st.session_state.step == 1:
    inject_style()
    st.markdown("<div class='step-title'>Étape 1 : Choisissez la Partie</div>", unsafe_allow_html=True)
    options = [r[0] for r in conn.execute("SELECT DISTINCT partie FROM convention_collective WHERE partie IS NOT NULL").fetchall()]
    choice = st.radio("Sélectionnez :", options, key="radio_p")
    if st.button("Continuer ➡️"):
        st.session_state.choices["partie"] = choice
        st.session_state.step = 2
        st.rerun()

# --- ÉTAPE 2 : CHOIX DU SOCLE ---
elif st.session_state.step == 2:
    p = st.session_state.choices["partie"]
    # Définition de la couleur selon le socle
    options = [r[0] for r in conn.execute("SELECT DISTINCT socle FROM convention_collective WHERE partie = ?", (p,)).fetchall()]
    st.markdown("<div class='step-title'>Étape 2 : Qui est concerné ?</div>", unsafe_allow_html=True)
    choice = st.radio("Sélectionnez le public :", options)
    if st.button("Continuer ➡️"):
        st.session_state.choices["socle"] = choice
        st.session_state.step = 3
        st.rerun()

# --- ÉTAPE 3 : CHOIX DU CHAPITRE ---
elif st.session_state.step == 3:
    p, s = st.session_state.choices["partie"], st.session_state.choices["socle"]
    color = "#e67e22" if "MATERNEL" in s.upper() else "#2980b9"
    inject_style(color)
    
    st.markdown(f"<div class='step-title'>Étape 3 : Choisissez le Chapitre</div>", unsafe_allow_html=True)
    options = [r[0] for r in conn.execute("SELECT DISTINCT chapitres FROM convention_collective WHERE partie = ? AND socle = ?", (p, s)).fetchall()]
    choice = st.radio("Sélectionnez :", options)
    if st.button("Continuer ➡️"):
        st.session_state.choices["chapitre"] = choice
        st.session_state.step = 4
        st.rerun()

# --- ÉTAPE 4 : CHOIX DE L'ARTICLE ---
elif st.session_state.step == 4:
    p, s, c = st.session_state.choices["partie"], st.session_state.choices["socle"], st.session_state.choices["chapitre"]
    color = "#e67e22" if "MATERNEL" in s.upper() else "#2980b9"
    inject_style(color)

    st.markdown("<div class='step-title'>Étape 4 : Sélectionnez l'Article</div>", unsafe_allow_html=True)
    articles = conn.execute("SELECT affichage_article, numero_article_isole FROM convention_collective WHERE partie=? AND socle=? AND chapitres=?", (p, s, c)).fetchall()
    dict_art = {a[0]: a[1] for a in articles}
    
    choice = st.radio("Articles disponibles :", list(dict_art.keys()))
    if st.button("Afficher l'article 🔍"):
        st.session_state.choices["article"] = choice
        st.session_state.step = 5
        st.rerun()

# --- ÉTAPE 5 : AFFICHAGE FINAL ---
elif st.session_state.step == 5:
    s = st.session_state.choices["socle"]
    color = "#e67e22" if "MATERNEL" in s.upper() else "#2980b9"
    inject_style(color)
    
    art_titre = st.session_state.choices["article"]
    res = conn.execute("SELECT texte_integral, texte_simplifie FROM convention_collective WHERE affichage_article = ?", (art_titre,)).fetchone()
    
    if res:
        officiel, simple = res
        st.markdown(f"<div class='article-card'><strong>{art_titre}</strong></div>", unsafe_allow_html=True)
        
        st.subheader("💡 Version simplifiée (A2)")
        st.info(simple if (simple and simple.strip()) else "Version simplifiée en cours de rédaction.")
        
        with st.expander("📄 Texte officiel complet"):
            st.write(officiel)
    
    if st.button("🔄 Nouvelle recherche"):
        reset_to_step(1)
        st.rerun()

conn.close()
