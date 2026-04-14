import streamlit as st
import json
import requests
import base64
import time

# --- CONFIGURAZIONE GITHUB ---
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO_NAME = st.secrets.get("REPO_NAME", "")
BRANCH = "main"
DB_FILE = "aosr_warzone_db.json"

st.set_page_config(page_title="AOSR WAR-ZONE", layout="wide", initial_sidebar_state="expanded")

# --- UI DESIGN (CSS AGGRESSIVO) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@500;700&display=swap');
    
    .stApp { background: #05070a; color: #e0e0e0; font-family: 'Rajdhani', sans-serif; }
    
    /* Sidebar Stile Bunker */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
        border-right: 3px solid #f39c12;
    }

    /* Menu di navigazione */
    .stRadio div[role="radiogroup"] label {
        background: #1c2128; border: 1px solid #30363d;
        padding: 10px 15px; border-radius: 8px; margin-bottom: 5px;
        transition: 0.3s;
    }
    .stRadio div[role="radiogroup"] label:hover { border-color: #f39c12; background: #262c36; }

    /* Intestazione Sezione */
    .war-header {
        font-family: 'Orbitron', sans-serif; color: #f39c12;
        padding: 15px; border-left: 10px solid #f39c12;
        background: rgba(243, 156, 18, 0.1); margin-bottom: 25px;
        text-transform: uppercase; letter-spacing: 3px;
    }

    /* Card Contenuto */
    .war-card {
        background: #0d1117; border: 1px solid #30363d;
        padding: 20px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    .rendered-markdown img {
        border: 2px solid #f39c12; border-radius: 10px;
        box-shadow: 0 0 20px rgba(243, 156, 18, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# --- DATABASE STRUCTURE (WAR READY) ---
def get_war_defaults():
    return {
        "sections": {
            "🛰️ HQ DASHBOARD": {"titolo": "CENTRO DI COMANDO", "tabs": [{"label": "DIRETTIVE", "content": "## 🚩 ORDINI DEL GIORNO\n1. Check-in Alleanza\n2. SVS Attivo"}]},
            "🔥 SEASON 6": {"titolo": "OPERAZIONE SEASON 6", "tabs": [{"label": "MAPPA", "content": ""}, {"label": "BOSS", "content": ""}]},
            "⚔️ SQUADRONE": {"titolo": "BUILD EROI & SQUAD", "tabs": [{"label": "SQUAD 1", "content": ""}, {"label": "CHIP & GEAR", "content": ""}]},
            "🧪 LABORATORIO": {"titolo": "RICERCA & TECH", "tabs": [{"label": "PRIORITÀ", "content": ""}, {"label": "DECORAZIONI", "content": ""}]},
            "🏰 BASE & RISORSE": {"titolo": "GESTIONE RISORSE", "tabs": [{"label": "PRODUZIONE", "content": ""}, {"label": "TIPS", "content": ""}]},
            "🛡️ DIPLOMAZIA": {"titolo": "RELAZIONI ESTERNE", "tabs": [{"label": "ALLEATI", "content": ""}, {"label": "REGOLE", "content": ""}]}
        }
    }

def load_db():
    try:
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{DB_FILE}?t={int(time.time())}"
        res = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
        if res.status_code == 200:
            data = json.loads(base64.b64decode(res.json()['content']).decode())
            # Patch per nuove sezioni se il DB è vecchio
            defaults = get_war_defaults()
            for k, v in defaults["sections"].items():
                if k not in data["sections"]: data["sections"][k] = v
            return data
    except: pass
    return get_war_defaults()

def save_db(data):
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{DB_FILE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    sha = r.json().get("sha") if r.status_code == 200 else None
    content = base64.b64encode(json.dumps(data, indent=4).encode()).decode()
    payload = {"message": "War Sync", "content": content, "sha": sha}
    if requests.put(url, json=payload, headers=headers).status_code in [200, 201]:
        st.toast("🛰️ DATI TRASMESSI AL BUNKER", icon="⚔️")
        time.sleep(0.5)
        st.rerun()

if 'db' not in st.session_state:
    st.session_state.db = load_db()

# --- SIDEBAR: MENU TATTICO ---
with st.sidebar:
    st.markdown("<h1 style='color:#f39c12; font-family:Orbitron; font-size:24px; text-align:center;'>AOSR OVERLORD</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    architetto = st.toggle("🛠️ MODALITÀ ARCHITETTO", value=False)
    
    st.markdown("### 📋 MENU OPERATIVO")
    # Menu con icone spettacolari
    menu_options = list(st.session_state.db["sections"].keys())
    selected_menu = st.radio("SELEZIONA SETTORE", menu_options, label_visibility="collapsed")
    
    st.markdown("---")
    if st.button("💾 SALVA MODIFICHE", use_container_width=True):
        save_db(st.session_state.db)
    
    with st.expander("🖼️ CARICA SCREENSHOT"):
        f = st.file_uploader("Upload Image", type=['png','jpg'])
        if f:
            path = f"img/{f.name.replace(' ', '_')}"
            b64 = base64.b64encode(f.getvalue()).decode()
            requests.put(f"https://api.github.com/repos/{REPO_NAME}/contents/{path}", 
                         json={"message":"img","content":b64}, headers={"Authorization":f"token {GITHUB_TOKEN}"})
            st.code(f"![Img](https://raw.githubusercontent.com/{REPO_NAME}/{BRANCH}/{path})")

# --- AREA DI COMANDO CENTRALE ---
sec_data = st.session_state.db["sections"][selected_menu]

if architetto:
    st.markdown("### ⚙️ SETTAGGI SETTORE")
    sec_data["titolo"] = st.text_input("Titolo Visualizzato:", sec_data["titolo"])
    if st.button("🚀 AGGIUNGI NUOVA CATEGORIA MENU"):
        st.session_state.db["sections"][f"NEW_{int(time.time())}"] = {"titolo": "NUOVO", "tabs": [{"label": "Main", "content": ""}]}
        st.rerun()
else:
    st.markdown(f"<div class='war-header'>{sec_data['titolo']}</div>", unsafe_allow_html=True)

# TABS
tabs_list = sec_data["tabs"]
tab_titles = [t["label"] for t in tabs_list]
if architetto: tab_titles.append("➕")

st_tabs = st.tabs(tab_titles)

for i, t in enumerate(tabs_list):
    with st_tabs[i]:
        if architetto:
            t["label"] = st.text_input(f"Nome Tab {i+1}", t["label"], key=f"l_{selected_menu}_{i}")
            t["content"] = st.text_area("Markdown/Immagini:", t["content"], height=400, key=f"c_{selected_menu}_{i}")
            if st.button(f"🗑️ Rimuovi {t['label']}", key=f"d_{selected_menu}_{i}"):
                sec_data["tabs"].pop(i)
                st.rerun()
        else:
            st.markdown("<div class='war-card'>", unsafe_allow_html=True)
            st.markdown(t["content"])
            st.markdown("</div>", unsafe_allow_html=True)

if architetto and len(st_tabs) > len(tabs_list):
    with st_tabs[-1]:
        if st.button("➕ AGGIUNGI SOTTO-SCHEDA"):
            sec_data["tabs"].append({"label": "Nuovo", "content": ""})
            st.rerun()
