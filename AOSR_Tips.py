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

# --- STYLE AOSR (Invariato) ---
st.set_page_config(page_title="AOSR SQUAD: COMMAND CENTER", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; border-top: 3px solid #f39c12; }
    .section-card { padding: 25px; border-radius: 15px; border-left: 5px solid #f39c12; background-color: #1c2128; margin-bottom: 20px; }
    .main-title { color: #f39c12; font-size: 40px; font-weight: bold; text-align: center; text-transform: uppercase; }
    h1, h2, h3 { color: #f39c12 !important; }
    </style>
""", unsafe_allow_html=True)

# --- VALORI DI DEFAULT (IL PARACADUTE) ---
def get_emergency_defaults():
    return {
        "config": {"titolo_display": "AOSR SQUAD", "server": "#XXX", "motto": "Sincronizzazione in corso..."},
        "stats": {"Membri": "N/D", "S1_Media": "N/D", "Power_Rank": "N/D"},
        "news": "⚠️ L'app è in modalità emergenza. Controlla la connessione GitHub.",
        "s6_meta": "", "academy": "", "drone": ""
    }

# --- LOGICA DI CARICAMENTO INTEGRATA ---
def load_db():
    defaults = get_emergency_defaults()
    
    # 1. Prova a scaricare l'ultima versione da GitHub per essere sempre aggiornati
    if GITHUB_TOKEN and REPO_NAME:
        try:
            url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}?ref={BRANCH}"
            headers = {"Authorization": f"token {GITHUB_TOKEN}"}
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                content = base64.b64decode(response.json()['content']).decode('utf-8')
                data = json.loads(content)
                # Assicura che le chiavi essenziali esistano
                for k, v in defaults.items():
                    if k not in data: data[k] = v
                return data
        except Exception as e:
            st.warning(f"Sincronizzazione Cloud fallita. Caricamento dati locali. (Errore: {e})")

    # 2. Se GitHub fallisce, prova a leggere il file locale
    if os.path.exists(FILE_PATH):
        try:
            with open(FILE_PATH, "r") as f:
                return json.load(f)
        except:
            return defaults
            
    return defaults

# --- FUNZIONE SALVATAGGIO REMOTO ---
def save_to_github(data):
    if not GITHUB_TOKEN or not REPO_NAME:
        return False
    
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    try:
        r = requests.get(url, headers=headers, timeout=5)
        sha = r.json().get("sha") if r.status_code == 200 else None
        content_base64 = base64.b64encode(json.dumps(data, indent=4).encode()).decode()
        
        payload = {"message": "Update AOSR Database", "content": content_base64, "branch": BRANCH}
        if sha: payload["sha"] = sha
        
        res = requests.put(url, headers=headers, json=payload, timeout=10)
        return res.status_code in [200, 201]
    except:
        return False

# --- GESTIONE SESSIONE ---
if 'db' not in st.session_state:
    st.session_state.db = load_db()

def trigger_save():
    # Salva locale
    with open(FILE_PATH, "w") as f:
        json.dump(st.session_state.db, f, indent=4)
    # Salva remoto
    if save_to_github(st.session_state.db):
        st.success("✅ Dati salvati su GitHub!")
    else:
        st.error("❌ Errore nel salvataggio remoto. I dati sono solo locali.")

# --- INTERFACCIA ---
page = st.sidebar.selectbox("MODULO TATTICO", ["📡 DASHBOARD", "⚔️ SEASON 6", "🎓 ACCADEMIA", "🤖 DRONE & GEAR"])

def render_section(key, title):
    st.markdown(f"<div class='section-card'>", unsafe_allow_html=True)
    col_t, col_e = st.columns([0.8, 0.2])
    with col_t: st.subheader(title)
    with col_e: edit = st.toggle("EDIT", key="t_"+key)
    
    if edit:
        new_content = st.text_area("Update", value=st.session_state.db.get(key, ""), height=250, key="a_"+key)
        if st.button("SALVA", key="b_"+key):
            st.session_state.db[key] = new_content
            trigger_save()
            st.rerun()
    else:
        st.markdown(st.session_state.db.get(key, ""))
    st.markdown("</div>", unsafe_allow_html=True)

# (Seguono le pagine DASHBOARD, SEASON 6, ecc. usando render_section)
# ... [Inserisci qui la logica delle pagine che avevamo già fatto]
