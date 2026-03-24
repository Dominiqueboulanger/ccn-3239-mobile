import streamlit as st
import sqlite3

# --- CONFIGURATION ET STYLE ---
st.set_page_config(page_title="Expert CCN - Mobile", layout="centered")

def inject_custom_css(color_theme):
    st.markdown(f"""
        <style>
        /* Titre principal */
        .main-title {{
            color: #1e3799;
            text-align: center;
            font-size: 28px;
            font-weight: 800;
            margin-bottom: 5px;
        }}
        /* Bandeau de couleur dynamique pour le titre de l'article */
        .article-card {{
            background-color: {color_theme};
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        /* Style pour la version simplifiée */
        .simple-box {{
            background-color: #f8f9fa;
            border-left: 5px solid {color_theme};
            padding: 15px;
            border-radius: 5px;
            font-size: 17px;
        }}
        </style>
        """, unsafe_allow_html=True)

# --- FONCTIONS TECHNIQUES ---
def get_connection():
    return sqlite3.connect("CCN_3239.db")

# --- INTERFACE ---
st.markdown("<div class='main-title'>📖 CCN 3239</div>", unsafe_allow_html=True)
st.caption("✨ Version pédagogique pour apprenants FLE/A2")

conn = get_connection()

try:
    # 1. Menu Partie
    parties = [r[0] for r in conn.execute("SELECT DISTINCT partie FROM convention_collective WHERE partie IS NOT NULL").fetchall()]
    partie_sel = st.selectbox("📁 Étape 1 : Choisir la Partie", ["---"] + parties)

    if partie_sel != "---":
        # 2. Menu Socle
        socles = [r[0] for r in conn.execute("SELECT DISTINCT socle FROM convention_collective WHERE partie = ?", (partie_sel,)).fetchall()]
        socle_sel = st.radio("👤 Étape 2 : Qui est concerné ?", socles)

        # --- LOGIQUE DE DESIGN DYNAMIQUE ---
        # On définit une icône et une couleur selon le public
        if "MATERNEL" in socle_sel.upper():
            theme_color = "#e67e22"  # Orange pour les Assmat
            icon = "👶"
            label = "Assistant Maternel"
        elif "PARTICULIER EMPLOYEUR" in socle_sel.upper():
            theme_color = "#2980b9"  # Bleu pour les Salariés du particulier
            icon = "🏠"
            label = "Salarié du Particulier"
        else:
            theme_color = "#1e3799"  # Bleu marine par défaut (Socle commun)
            icon = "⚖️"
            label = "Socle Commun"

        inject_custom_css(theme_color)
        st.success(f"Mode : {icon} **{label}**")

        # 3. Chapitres
        chaps = [r[0] for r in conn.execute("SELECT DISTINCT chapitres FROM convention_collective WHERE partie = ? AND socle = ?", (partie_sel, socle_sel)).fetchall()]
        chap_sel = st.selectbox("📑 Étape 3 : Choisir le Chapitre", ["---"] + chaps)

        if chap_sel != "---":
            # 4. Articles
            articles = conn.execute("""
                SELECT affichage_article, numero_article_isole 
                FROM convention_collective 
                WHERE partie = ? AND socle = ? AND chapitres = ?
            """, (partie_sel, socle_sel, chap_sel)).fetchall()
            
            dict_articles = {a[0]: a[1] for a in articles}
            art_affiche = st.selectbox("🔍 Étape 4 : Quel article ?", ["---"] + list(dict_articles.keys()))

            if art_affiche != "---":
                num_art = dict_articles[art_affiche]
                res = conn.execute("SELECT texte_integral, texte_simplifie FROM convention_collective WHERE numero_article_isole = ?", (num_art,)).fetchone()
                
                if res:
                    officiel, simple = res
                    st.markdown("---")
                    
                    # Titre stylisé avec la couleur du thème
                    st.markdown(f"""
                        <div class='article-card'>
                            <small>{icon} {label}</small><br>
                            <strong>{art_affiche}</strong>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("### 💡 En français facile")
                    if simple and simple.strip():
                        st.markdown(f"<div class='simple-box'>{simple}</div>", unsafe_allow_html=True)
                    else:
                        st.info("🚧 La version simplifiée arrive bientôt pour cet article.")
                    
                    with st.expander("📄 Voir le texte juridique officiel"):
                        st.write(officiel)

except Exception as e:
    st.error(f"Erreur : {e}")
finally:
    conn.close()
