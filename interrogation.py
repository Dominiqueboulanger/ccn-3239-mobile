import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# --- CONFIGURATION ---
DB_PATH = "CCN_3239.db"

class NavigateurConvention:
    def __init__(self, root):
        self.root = root
        self.root.title("Expert CCN 3239 - Navigation Optimisée")
        self.root.geometry("1400x950")
        self.root.configure(bg="#f0f2f5")

        # --- BARRE DE RECHERCHE ---
        self.search_bar = tk.Frame(root, bg="#1e3799", pady=15)
        self.search_bar.pack(fill="x")

        tk.Label(self.search_bar, text="ACCÈS DIRECT N° :", fg="white", bg="#1e3799", font=("Arial", 14, "bold")).pack(side="left", padx=(20, 5))
        self.ent_num = tk.Entry(self.search_bar, width=10, font=("Arial", 16))
        self.ent_num.pack(side="left", padx=5)
        self.ent_num.bind("<Return>", lambda e: self.recherche_directe())

        # Bouton Quitter
        self.btn_quit = tk.Label(self.search_bar, text="✖ QUITTER", bg="#c0392b", fg="white", 
                                 font=("Arial", 12, "bold"), padx=15, pady=8, cursor="hand2", relief="raised")
        self.btn_quit.pack(side="right", padx=20)
        self.btn_quit.bind("<Button-1>", lambda e: self.quitter_proprement())

        # --- NAVIGATION (CASCADE) ---
        self.header = tk.Frame(root, bg="#ffffff", pady=15, bd=1, relief="groove")
        self.header.pack(fill="x", padx=10, pady=10)

        self.combos = {}
        structure = [
            ("PARTIE (I-V)", "partie"), 
            ("SOCLE", "socle"), 
            ("CHAPITRE", "chapitres"), 
            ("ARTICLE", "article")
        ]
        
        for label, key in structure:
            f = tk.Frame(self.header, bg="#ffffff")
            f.pack(fill="x", pady=5)
            tk.Label(f, text=f"{label} :", width=15, anchor="w", bg="#ffffff", font=("Arial", 12, "bold")).pack(side="left", padx=10)
            cb = ttk.Combobox(f, state="readonly", font=("Arial", 12))
            cb.pack(side="left", expand=True, fill="x", padx=(0, 20))
            self.combos[key] = cb

        # Liaisons
        self.combos["partie"].bind("<<ComboboxSelected>>", lambda e: self.maj_cascade("socle"))
        self.combos["socle"].bind("<<ComboboxSelected>>", lambda e: self.maj_cascade("chapitres"))
        self.combos["chapitres"].bind("<<ComboboxSelected>>", lambda e: self.maj_cascade("article"))
        self.combos["article"].bind("<<ComboboxSelected>>", self.afficher_selection)

        # --- ZONE D'AFFICHAGE ---
        self.text_frame = tk.Frame(root, bg="white")
        self.text_frame.pack(expand=True, fill="both", padx=10, pady=5)
        self.text_area = tk.Text(self.text_frame, wrap="word", font=("Georgia", 16), padx=40, pady=30, bd=0)
        self.text_area.pack(side="left", expand=True, fill="both")
        
        scroll = tk.Scrollbar(self.text_frame, command=self.text_area.yview)
        scroll.pack(side="right", fill="y")
        self.text_area.config(yscrollcommand=scroll.set)

        self.text_area.tag_configure("TITRE", font=("Arial", 22, "bold"), foreground="#1e3799")

        self.init_data()

    def quitter_proprement(self):
        """ Arrête proprement l'application sur Mac et PC """
        self.root.quit()
        self.root.destroy()
        sys.exit()

    def maj_cascade(self, cible):
        hierarchie = ["partie", "socle", "chapitres", "article"]
        idx = hierarchie.index(cible)
        
        for i in range(idx, len(hierarchie)):
            self.combos[hierarchie[i]].set('')
            self.combos[hierarchie[i]]['values'] = []
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            
            conds, params = [], []
            for i in range(idx):
                p_key = hierarchie[i]
                val = self.combos[p_key].get()
                if val:
                    # Pour l'article, on n'utilise que le numéro pour filtrer
                    if p_key == "article": val = val.split(" - ")[0]
                    conds.append(f"{p_key} = ?")
                    params.append(val)
            
            where = " WHERE " + " AND ".join(conds) if conds else ""
            
            if cible == "article":
                # Affiche le numéro + les 60 premiers caractères du texte
                sql = f"SELECT numero_article_isole || ' - ' || SUBSTR(texte_integral, 1, 60) FROM convention_collective {where} ORDER BY id"
            else:
                sql = f"SELECT DISTINCT {cible} FROM convention_collective {where} ORDER BY id"
            
            cur.execute(sql, tuple(params))
            self.combos[cible]['values'] = [str(r[0]) for r in cur.fetchall()]
            conn.close()
        except Exception as e:
            print(f"Erreur SQL: {e}")

    def afficher_selection(self, e):
        selection = self.combos["article"].get()
        if selection:
            num = selection.split(" - ")[0]
            self.charger_article(num)

    def recherche_directe(self):
        num = self.ent_num.get().strip()
        if num: self.charger_article(num)

    def charger_article(self, num):
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT numero_article_isole, texte_integral FROM convention_collective WHERE numero_article_isole = ?", (num,))
            res = cur.fetchone()
            conn.close()

            self.text_area.delete("1.0", tk.END)
            if res:
                self.text_area.insert(tk.END, f"ARTICLE {res[0]}\n", "TITRE")
                self.text_area.insert(tk.END, "\n" + res[1])
                self.text_area.see("1.0")
            else:
                self.text_area.insert(tk.END, "⚠️ Article non trouvé.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def init_data(self):
        if not os.path.exists(DB_PATH): return
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT partie FROM convention_collective ORDER BY id")
            self.combos["partie"]['values'] = [str(r[0]) for r in cur.fetchall()]
            conn.close()
        except Exception as e:
            print(f"Erreur initialisation: {e}")

# --- LANCEMENT SÉCURISÉ ---
if __name__ == "__main__":
    root = tk.Tk()
    
    # Création de l'application avec le bon nom de classe
    app = NavigateurConvention(root)
    
    # Gestion de la fermeture par la croix rouge (Mac & PC)
    def on_closing():
        app.quitter_proprement()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
