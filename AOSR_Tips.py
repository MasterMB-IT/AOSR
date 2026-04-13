import streamlit as st
import json
import os
import requests
import base64

# --- CONFIGURAZIONE GITHUB ---
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO_NAME = st.secrets.get("REPO_NAME", "")
FILE_PATH = "aosr_squad_db.json"
BRANCH = "main"

st.set_page_config(page_title="AOSR SQUAD: RECOVERY", layout="wide")

# --- DATABASE DI EMERGENZA (Se GitHub fallisce, usa questo) ---
def get_default_data():
    return {
        "config": {"titolo_display": "AOSR SQUAD", "server": "#XXX", "motto": "Elite Soldiers"},
        "stats": {"Membri": "0", "S1_Media": "0", "Power_Rank": "#0"},
        "news": "Dati resettati. Clicca EDIT per scrivere.",
        "s6_meta": "", "academy": "", "drone": ""
    }

# --- FUNZIONE DI CARICAMENTO SICURA AL 100% ---
def load_db():
    # Prova GitHub
    if GITHUB_TOKEN and REPO_NAME:
        try:
            url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}?ref={BRANCH}"
            headers = {"Authorization": f"token {GITHUB_TOKEN}"}
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                content = base64.b64decode(res.json()['content']).decode('utf-8')
                return json.loads(content)
        except:
            pass
    return get_default_data()

# --- FUNZIONE DI SALVATAGGIO ---
def save_db(data):
    # Salva su GitHub
    if GITHUB_TOKEN and REPO_NAME:
        try:
            url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
            headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
            r = requests.get(url, headers=headers)
            sha = r.json().get("sha") if r.status_code == 200 else None
            content_b64 = base64.b64encode(json.dumps(data, indent=4).encode()).decode()
            payload = {"message": "Recovery Update", "content": content_b64, "branch": BRANCH}
            if sha: payload["sha"] = sha
            requests.put(url, headers=headers, json=payload, timeout=10)
        except:
            st.error("Errore critico durante il salvataggio su GitHub.")

# Inizializza sessione
if 'db' not in st.session_state:
    st.session_state.db = load_db()

# --- INTERFACCIA ---
st.sidebar.title("🛡️ AOSR COMMAND")
page = st.sidebar.selectbox("MODULO TATTICO", ["📡 DASHBOARD", "⚔️ SEASON 6", "🎓 ACCADEMIA"])

if page == "📡 DASHBOARD":
    st.title("AOSR SQUAD - DASHBOARD")
    
    # Sezione Statistiche Editabile
    with st.expander("⚙️ MODIFICA STATISTICHE (Sblocca schermata)"):
        c1, c2, c3 = st.columns(3)
        # Usiamo .get() per evitare il KeyError che vedi nelle tue foto
        stats = st.session_state.db.get("stats", {})
        m = c1.text_input("Membri", stats.get("Membri", "100"))
        p = c2.text_input("Potenza", stats.get("S1_Media", "20M"))
        r = c3.text_input("Rank", stats.get("Power_Rank", "#1"))
        
        if st.button("SALVA STATISTICHE"):
            st.session_state.db["stats"] = {"Membri": m, "S1_Media": p, "Power_Rank": r}
            save_db(st.session_state.db)
            st.rerun()

    # Visualizzazione
    stats = st.session_state.db.get("stats", {})
    col1, col2, col3 = st.columns(3)
    col1.metric("Membri", stats.get("Membri", "N/A"))
    col2.metric("Potenza", stats.get("S1_Media", "N/A"))
    col3.metric("Rank", stats.get("Power_Rank", "N/A"))

    # Sezione News
    st.divider()
    edit_news = st.toggle("EDIT NEWS")
    if edit_news:
        new_news = st.text_area("Testo:", st.session_state.db.get("news", ""))
        if st.button("SALVA NEWS"):
            st.session_state.db["news"] = new_news
            save_db(st.session_state.db)
            st.rerun()
    else:
        st.markdown(st.session_state.db.get("news", "Nessuna direttiva."))
