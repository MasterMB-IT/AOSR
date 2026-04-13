import streamlit as st
import json
import os
import requests
import base64

# --- CONFIGURAZIONE GITHUB (Prende i dati dai Secrets di Streamlit) ---
# Se provi in locale, puoi scriverli direttamente o usare un file .streamlit/secrets.toml
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")
REPO_NAME = st.secrets.get("REPO_NAME")
FILE_PATH = "aosr_squad_db.json"
BRANCH = "main"

# --- STYLE AOSR ---
st.set_page_config(page_title="AOSR SQUAD: PERMANENT COMMAND", layout="wide")

# (Il CSS rimane lo stesso del messaggio precedente...)
st.markdown("<style>.main { background-color: #0d1117; } ... </style>", unsafe_allow_html=True)

# --- FUNZIONE PER SALVARE SU GITHUB ---
def save_to_github(data):
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # 1. Recuperiamo lo SHA del file esistente (necessario per l'update)
    r = requests.get(url, headers=headers)
    sha = r.json().get("sha") if r.status_code == 200 else None
    
    # 2. Prepariamo il contenuto
    content_base64 = base64.b64encode(json.dumps(data, indent=4).encode()).decode()
    
    payload = {
        "message": "Aggiornamento Diario AOSR Squad",
        "content": content_base64,
        "branch": BRANCH
    }
    if sha:
        payload["sha"] = sha
        
    # 3. Push su GitHub
    res = requests.put(url, headers=headers, json=payload)
    return res.status_code in [200, 201]

# --- DATABASE ENGINE ---
def load_db():
    # Iniziamo caricando dal file locale (o GitHub se preferisci)
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r") as f:
            return json.load(f)
    return {
        "config": {"titolo_display": "AOSR SQUAD", "server": "#XXX", "motto": "Elite Soldiers"},
        "stats": {"Membri": "100/100", "S1_Media": "25.0M", "Power_Rank": "#1"},
        "news": "Benvenuti AOSR!",
        "s6_meta": "", "academy": "", "drone": ""
    }

if 'db' not in st.session_state:
    st.session_state.db = load_db()

# --- FUNZIONE SALVATAGGIO DOPPIO (Locale + Remoto) ---
def final_save():
    # Salva localmente per velocità
    with open(FILE_PATH, "w") as f:
        json.dump(st.session_state.db, f, indent=4)
    
    # Salva su GitHub per permanenza
    with st.spinner("Sincronizzazione Cloud AOSR in corso..."):
        success = save_to_github(st.session_state.db)
        if success:
            st.toast("Dati salvati permanentemente su GitHub!", icon="✅")
        else:
            st.error("Errore nella sincronizzazione Cloud. Controlla il Token.")

# --- UI LOGIC (Pagine e Dashboard...) ---
# (Qui inserisci la logica delle pagine che abbiamo costruito prima...)
# L'unica cosa che cambia è che invece di 'save()' chiamerai 'final_save()'
