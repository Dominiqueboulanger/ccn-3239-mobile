import streamlit as st
import sqlite3
import re
from pathlib import Path
from fpdf import FPDF

# --- CONFIGURATION ---
st.set_page_config(page_title="Navigation CCN 3239", layout="centered")

BASE_DIR = Path(__file__).parent
DB_PATH = (BASE_DIR / "CCN_3239.db").resolve()

def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row 
    return conn

# --- FONCTION GÉNÉRATION PDF OPTIMISÉE MOBILE ---
def export_pdf(article_num, titre, essentiel, integral):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"Article {article_num}", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.multi_cell(0, 10, titre.encode('latin-1', 'replace').decode('latin-1'))
    pdf.ln(5)
    
    if essentiel:
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 10, "L'ESSENTIEL :", ln=True, fill=True)
        pdf.set_font("Helvetica", "", 10)
        clean_essentiel = essentiel.replace("<b>", "").replace("</b>", "").replace("<br>", "\n")
        pdf.multi_cell(0, 7, clean_essentiel.encode('latin-1', 'replace').decode('latin-1'), fill=True)
        pdf.ln(10)
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 10, "TEXTE OFFICIEL :", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 7, integral.encode('latin-1', 'replace').decode('latin-1'))
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- STYLE CSS ADAPTÉ SMARTPHONE ---
st.markdown("""
    <style>
    .stButton>button { 
        width: 100%; 
        border-radius: 15px; 
        min-height: 4em; 
        font-size: 16px !important; 
        font-weight: bold; 
        margin-bottom: 12px; 
        border: 2px solid #1e3799; 
        background-color: white;
        white-space: normal !important; 
        text-align: left !important;   
        padding: 10px 20px !important;
    }
    .question-box { background-color: #f8f9fa; padding: 15px; border-radius: 15px; border-left: 8px solid #1e3799; margin-bottom: 20px; }
    .essentiel-box { background-color: #ecfdf5; border-left: 5px solid #27ae60; padding: 15px; border-radius: 10px; color: #065f46; margin-bottom: 10px; }
    .renvoi-box { background-color: #fff9db; border: 2px dashed #f59f00; padding: 15px; border-radius: 10px; margin-top: 10px; margin-bottom: 10px; text-align: center; }
    .stDownloadButton>button { background-color: #d63031 !important; color: white !important; border: none !important; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); text-align: center !important; }
    </style>
    """, unsafe_allow_html=True)

if 'etape' not in st.session_state:
    st.session_state.etape = 1
    st.session_state.choix = {}

st.title("La CCN 3239 ")

# --- LOGIQUE ÉTAPES 1 À 4 ---
if st.session_state.etape == 1:
    st.markdown("<div class='question-box'><h3>1. Votre métier ?</h3></div>", unsafe_allow_html=True)
    metiers = {"Assistant Maternel": "SOCLE ASSISTANT MATERNEL", "Garde d'enfants": "SOCLE SALARiÉ DU PARTICULIER EMPLOYEUR", "Assistant De Vie": "SOCLE SALARiÉ DU PARTICULIER EMPLOYEUR", "Employé Familial": "SOCLE SALARiÉ DU PARTICULIER EMPLOYEUR", "Autres": "SOCLE COMMUN"}
    for i, (label, socle_val) in enumerate(metiers.items()):
        if st.button(label, key=f"m_{i}"):
            st.session_state.choix['socle'] = socle_val; st.session_state.etape = 2; st.rerun()

elif st.session_state.etape == 2:
    st.markdown("<div class='question-box'><h3>2. Votre situation</h3></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Vie du contrat", key="v_c"): st.session_state.choix['titre_filtre'] = "TITRE 1"; st.session_state.etape = 3; st.rerun()
    with c2:
        if st.button("Fin du contrat", key="f_c"): st.session_state.choix['titre_filtre'] = "TITRE 2"; st.session_state.etape = 3; st.rerun()
    if st.button("⬅️ Retour", key="r_2"): st.session_state.etape = 1; st.rerun()

elif st.session_state.etape == 3:
    st.markdown("### 📑 Chapitres")
    conn = get_connection()
    chaps = conn.execute("SELECT DISTINCT chapitres FROM convention_collective WHERE socle = ? AND titres LIKE ?", (st.session_state.choix['socle'], f"{st.session_state.choix['titre_filtre']}%")).fetchall()
    for i, c in enumerate(chaps):
        if st.button(c['chapitres'], key=f"c_{i}"): st.session_state.choix['chapitre'] = c['chapitres']; st.session_state.etape = 4; st.rerun()
    conn.close()
    if st.button("⬅️ Retour", key="r_3"): st.session_state.etape = 2; st.rerun()

elif st.session_state.etape == 4:
    st.markdown("### 📄 Articles")
    conn = get_connection()
    arts = conn.execute("SELECT numero_article_isole, affichage_article FROM convention_collective WHERE socle = ? AND chapitres = ? ORDER BY numero_article_isole ASC", (st.session_state.choix['socle'], st.session_state.choix['chapitre'])).fetchall()
    for i, a in enumerate(arts):
        if st.button(a['affichage_article'], key=f"a_{i}"): 
            st.session_state.choix['article_id'] = a['numero_article_isole']
            st.session_state.etape = 5
            st.rerun()
    conn.close()
    if st.button("⬅️ Retour", key="r_4"): st.session_state.etape = 3; st.rerun()

# --- ÉTAPE 5 : AFFICHAGE + PDF + RECHERCHE ---
elif st.session_state.etape == 5:
    art_id = st.session_state.choix['article_id']
    socle = st.session_state.choix['socle']
    conn = get_connection()
    article = conn.execute("SELECT * FROM convention_collective WHERE numero_article_isole = ? AND socle = ?", (art_id, socle)).fetchone()
    conn.close()

    if article:
        st.markdown(f"### Article {article['numero_article_isole']}")
        st.info(article['affichage_article'])
        
        if article['texte_simplifie']:
            # Correction ici : Ajout des guillemets manquants
            st.markdown(f"<div class='essentiel-box'><b>💡 L'ESSENTIEL :</b><br>{article['texte_simplifie']}</div>", unsafe_allow_html=True)
        
        st.write(article['texte_integral'])

        pdf_bytes = export_pdf(article['numero_article_isole'], article['affichage_article'], article['texte_simplifie'], article['texte_integral'])
        st.download_button(label="📥 Télécharger en PDF", data=pdf_bytes, file_name=f"Art_{article['numero_article_isole']}.pdf", mime="application/pdf")

        mention = re.search(r"article\s+(\d+)", article['texte_integral'], re.IGNORECASE)
        if mention and mention.group(1) != str(art_id):
            num = mention.group(1)
            st.markdown(f"<div class='renvoi-box'>🔗 Renvoi vers l'<b>Article {num}</b></div>", unsafe_allow_html=True)
            if st.button(f"👉 Aller à l'Article {num}", key="r_auto"):
                st.session_state.choix['article_id'] = num; st.session_state.choix['socle'] = "SOCLE COMMUN"; st.rerun()

    st.markdown("---")
    with st.form("nav"):
        st.markdown("**🔍 Accès direct :**")
        col1, col2 = st.columns([3, 1])
        with col1:
            n_id = st.text_input("N° Article", placeholder="Ex: 47", label_visibility="collapsed")
        with col2:
            if st.form_submit_button("Go"):
                st.session_state.choix['article_id'] = n_id; st.session_state.choix['socle'] = "SOCLE COMMUN"; st.rerun()
    
    if st.button("🔄 Nouvelle recherche", key="reset"): st.session_state.etape = 1; st.rerun()
