import streamlit as st
import sqlite3
from pathlib import Path
from fpdf import FPDF

# --- CONFIGURATION ---
st.set_page_config(page_title="Assistant CCN 3239", layout="centered", page_icon="🛡️")

BASE_DIR = Path(__file__).parent
DB_PATH = (BASE_DIR / "CCN_3239.db").resolve()

def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row 
    return conn

# --- FONCTION EXPORT PDF ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Fiche Pratique - Convention Collective 3239', 0, 1, 'C')
        self.ln(5)

def generer_pdf(titre, essentiel, texte_loi):
    pdf = PDF()
    pdf.add_page()
    
    # Titre de l'article
    pdf.set_font("Arial", 'B', 14)
    pdf.multi_cell(0, 10, titre.encode('latin-1', 'replace').decode('latin-1'))
    pdf.ln(5)
    
    # Section Essentiel
    pdf.set_fill_color(236, 253, 245) # Vert clair
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, " L'ESSENTIEL :", 0, 1, 'L', fill=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 8, essentiel.encode('latin-1', 'replace').decode('latin-1'))
    pdf.ln(10)
    
    # Section Texte de loi
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, " TEXTE OFFICIEL :", 0, 1, 'L')
    pdf.set_font("Arial", '', 9)
    pdf.multi_cell(0, 6, texte_loi.encode('latin-1', 'replace').decode('latin-1'))
    
    return pdf.output(dest='S')

# --- STYLE CSS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; min-height: 3.8em; font-weight: bold; margin-bottom: 10px; border: 2px solid #1e3799; background-color: white; color: #1e3799; }
    .stButton>button:hover { background-color: #1e3799; color: white; }
    .question-box { background-color: #f8f9fa; padding: 20px; border-radius: 15px; border-left: 8px solid #1e3799; margin-bottom: 20px; }
    .essentiel-box { background-color: #ecfdf5; border-left: 5px solid #27ae60; padding: 15px; border-radius: 10px; color: #065f46; margin-bottom: 10px; }
    .racine-box { background-color: #fff5f5; border-left: 5px solid #c0392b; padding: 15px; border-radius: 10px; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- GESTION DE LA NAVIGATION ---
if 'etape' not in st.session_state:
    st.session_state.etape = 1
    st.session_state.choix = {}

st.title("🛡️ Assistant CCN 3239")

# --- ÉTAPE 1 : CHOIX DU MÉTIER ---
if st.session_state.etape == 1:
    st.markdown("<div class='question-box'><h3>1. Quel est votre métier ?</h3></div>", unsafe_allow_html=True)
    metiers = {
        "Assistant Maternel": "SOCLE ASSISTANT MATERNEL",
        "Garde d'enfants / Assistant Parental": "SOCLE SALARiÉ DU PARTICULIER EMPLOYEUR",
        "Assistant De Vie / Employé Familial": "SOCLE SALARiÉ DU PARTICULIER EMPLOYEUR",
        "Autres / Entreprise": "SOCLE COMMUN"
    }
    for label, socle_val in metiers.items():
        if st.button(label):
            st.session_state.choix['socle'] = socle_val
            st.session_state.etape = 2
            st.rerun()

# --- ÉTAPE 2 : FILTRE PAR TITRE ---
elif st.session_state.etape == 2:
    st.markdown("<div class='question-box'><h3>2. Votre situation</h3><p>Le sujet concerne-t-il la fin de votre contrat ?</p></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Non (Vie du contrat)"):
            st.session_state.choix['titre_filtre'] = "TITRE 1"
            st.session_state.etape = 3
            st.rerun()
    with col2:
        if st.button("Oui (Rupture)"):
            st.session_state.choix['titre_filtre'] = "TITRE 2"
            st.session_state.etape = 3
            st.rerun()
    if st.button("⬅️ Retour"):
        st.session_state.etape = 1
        st.rerun()

# --- ÉTAPE 3 : CHOIX DE LA QUESTION ---
elif st.session_state.etape == 3:
    st.markdown("<div class='question-box'><h3>3. Quel sujet vous questionne ?</h3></div>", unsafe_allow_html=True)
    conn = get_connection()
    try:
        query = """
            SELECT q.id, q.question_texte, c.numero_article_isole 
            FROM questions_app q 
            INNER JOIN convention_collective c ON q.id = c.id 
            WHERE c.socle = ? AND c.titres LIKE ?
        """
        questions = conn.execute(query, (st.session_state.choix['socle'], f"{st.session_state.choix['titre_filtre']}%")).fetchall()
        
        if not questions:
            st.warning("Aucune question pré-enregistrée pour cette section.")
            if st.button("Poser une question libre"):
                st.session_state.etape = 4
                st.session_state.choix['article_source'] = "LIBRE"
                st.rerun()
        else:
            for q in questions:
                if st.button(q['question_texte'], key=f"q_{q['id']}"):
                    st.session_state.choix['article_source'] = q['numero_article_isole']
                    st.session_state.etape = 4
                    st.rerun()
    finally:
        conn.close()
    
    if st.button("⬅️ Retour"):
        st.session_state.etape = 2
        st.rerun()

# --- ÉTAPE 4 : AFFICHAGE DES RÉSULTATS & MAPPING ---
elif st.session_state.etape == 4:
    art_source = st.session_state.choix['article_source']
    socle = st.session_state.choix['socle']
    
    if art_source == "LIBRE":
        st.info("Module IA en cours de déploiement...")
    else:
        conn = get_connection()
        # 1. On récupère l'article métier principal
        res = conn.execute("SELECT * FROM convention_collective WHERE numero_article_isole = ? AND socle = ?", (str(art_source), socle)).fetchone()
        
        if res:
            st.markdown(f"### 📄 {res['affichage_article']}")
            
            # Affichage de l'essentiel (texte simplifié)
            if res['texte_simplifie']:
                st.markdown(f"<div class='essentiel-box'><b>💡 L'ESSENTIEL :</b><br>{res['texte_simplifie']}</div>", unsafe_allow_html=True)
            
            # 2. RECHERCHE DU MAPPING (Lien vers la règle racine)
            mapping = conn.execute("""
                SELECT c.texte_integral, c.numero_article_isole, c.affichage_article
                FROM mapping_articles m
                JOIN convention_collective c ON m.article_commun = c.numero_article_isole
                WHERE m.article_source = ? AND m.socle_source = ? AND c.socle = 'SOCLE COMMUN'
            """, (str(art_source), socle)).fetchone()

            if mapping:
                with st.expander(f"🔗 Voir la règle générale (Art. {mapping['numero_article_isole']})"):
                    st.markdown(f"<div class='racine-box'><b>Rappel du socle commun :</b><br><br>{mapping['texte_integral']}</div>", unsafe_allow_html=True)

            # 3. Texte intégral métier
            with st.expander("⚖️ Voir le texte officiel complet"):
                st.write(res['texte_integral'])

            # --- BOUTON EXPORT PDF ---
            st.write("---")
            pdf_bytes = generer_pdf(res['affichage_article'], res['texte_simplifie'] or "Consultez le texte intégral.", res['texte_integral'])
            st.download_button(
                label="📥 Télécharger ce mémo en PDF",
                data=pdf_bytes,
                file_name=f"Memo_Art_{art_source}.pdf",
                mime="application/pdf"
            )
            
        else:
            st.error("Détails de l'article introuvables dans la base.")
        conn.close()

    if st.button("🔄 Nouvelle recherche"):
        st.session_state.etape = 1
        st.rerun()
