import streamlit as st
import sqlite3

# --- 1. CONFIGURATION ET STYLE ---
st.set_page_config(page_title="Expert CCN - Mobile", layout="centered")

def inject_custom_css(color_theme):
    st.markdown(f"""
        <style>
        .main-title {{
            color: #1e3799;
            text-align: center;
            font-size: 28px;
            font-weight: 800;
            margin-bottom: 5px;
        }}
        .article-card {{
            background-color: {color_theme};
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .simple-box {{
            background-color: #f8f9fa;
            border-left: 5px solid {color_theme};
            padding: 15px;
            border-radius: 5px;
            font-size: 17px;
        }}
        </style>
        """, unsafe_allow_html=True)

# --- 2. FONCTIONS DE MAINTENANCE ET CONNEXION ---
def maintenance_mobile():
    """Vérifie que la colonne affichage_article existe, sinon la crée"""
    conn = sqlite3.connect("CCN_3239.db")
    cur = conn.cursor()
    try:
        cur.execute("SELECT affichage_article FROM convention_collective LIMIT 1")
    except sqlite3.OperationalError:
        # La colonne manque : on la crée et on extrait les titres
        cur.execute("ALTER TABLE convention_collective ADD COLUMN affichage_article TEXT")
        cur.execute("SELECT id, texte_integral FROM convention_collective")
        rows = cur.fetchall()
        for row_id, texte in rows:
            if texte:
                # On prend la première ligne du texte comme titre
                titre = texte.split('\n')[0].strip()
                cur.execute("UPDATE convention_collective SET affichage_article = ? WHERE id = ?", (titre, row_id))
        conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect("CCN_3239.db")

# --- 3. LOGIQUE PRINCIPALE ---
maintenance_mobile()
st.markdown("<div class='main-title'>📖 CCN 3239</div>", unsafe_allow_html=True)
st.caption("✨ Version pédagogique pour apprenants FLE/A2")

conn = get_connection()

try:
    # Étape 1 : Choix de la Partie
    parties = [r[0] for r in conn.execute("SELECT DISTINCT partie FROM convention_collective WHERE partie IS NOT NULL").fetchall()]
    partie_sel = st.selectbox("📁 Étape 1 : Choisir la Partie", ["---"] + parties)

    if partie_sel != "---":
        # Étape 2 : Choix du Socle (Radio pour éviter le clavier mobile)
        socles = [r[0] for r in conn.execute("SELECT DISTINCT socle FROM convention_collective WHERE partie = ?", (partie_sel,)).fetchall()]
        socle_sel = st.radio("👤 Étape 2 : Qui est concerné ?", socles)

        # Définition du thème visuel
        if "MATERNEL" in socle_sel.upper():
            theme_color = "#e67e22"  # Orange
            icon, label = "👶", "Assistant Maternel"
        elif "PARTICULIER EMPLOYEUR" in socle_sel.upper():
            theme_color = "#2980b9"  # Bleu
            icon, label = "🏠", "Salarié du Particulier"
        else:
            theme_color = "#1e3799"  # Marine
            icon, label = "⚖️", "Socle Commun"

        inject_custom_css(theme_color)
        st.success(f"Mode : {icon} **{label}**")

        # Étape 3 : Choix du Chapitre
        chaps = [r[0] for r in conn.execute("SELECT DISTINCT chapitres FROM convention_collective WHERE partie = ? AND socle = ?", (partie_sel, socle_sel)).fetchall()]
        chap_sel = st.selectbox("📑 Étape 3 : Choisir le Chapitre", ["---"] + chaps)

        if chap_sel != "---":
            # Étape 4 : Choix de l'Article
            articles = conn.execute("""
                SELECT affichage_article, numero_article_isole 
                FROM convention_collective 
                WHERE partie = ? AND socle = ? AND chapitres = ?
            """, (partie_sel, socle_sel, chap_sel)).fetchall()
            
            dict_articles = {a[0]: a[1] for a in articles}
            art_affiche = st.selectbox("🔍 Étape 4 : Quel article ?", ["---"] + list(dict_articles.keys()))

            if art_affiche != "---":
                num_art = dict_articles[art_affiche]
                # On récupère texte_integral (officiel) et texte_simplifie
                res = conn.execute("SELECT texte_integral, texte_simplifie FROM convention_collective WHERE numero_article_isole = ?", (num_art,)).fetchone()
                
                if res:
                    officiel, simple = res
                    st.markdown("---")
                    
                    # Carte de titre (colonne affichage_article)
                    st.markdown(f"""
                        <div class='article-card'>
                            <small>{icon} {label}</small><br>
                            <strong>{art_affiche}</strong>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Section Français Facile
                    st.markdown("### 💡 En français facile")
                    if simple and simple.strip():
                        st.markdown(f"<div class='simple-box'>{simple}</div>", unsafe_allow_html=True)
                    else:
                        st.info("🚧 La version simplifiée arrive bientôt pour cet article.")
                    
                    # Section Texte Officiel (Affiche le texte complet)
                    with st.expander("📄 Voir le texte juridique officiel"):
                        st.write(officiel)

except Exception as e:
    st.error(f"Erreur : {e}")
finally:
    conn.close()
