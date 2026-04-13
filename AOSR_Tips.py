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

# --- STYLE AOSR ULTIMATE ---
st.set_page_config(page_title="AOSR SQUAD HQ", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    .main { background-color: #0b0e14; }
    
    /* Titolo Principale */
    .main-header {
        background: linear-gradient(90deg, #161b22 0%, #30363d 50%, #161b22 100%);
        padding: 20px;
        border-radius: 10px;
        border-bottom: 4px solid #f39c12;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0px 10px 20px rgba(0,0,0,0.5);
    }
    .main-title {
        font-family: 'Orbitron', sans-serif;
        color: #f39c12;
        font-size: 50px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 5px;
        margin: 0;
    }
    
    /* Cards Statistiche */
    .stMetric {
        background: rgba(22, 27, 34, 0.8);
        border: 1px solid #f39c12;
        border-radius: 15px !important;
        padding: 20px !important;
        box-shadow: 0 0 15px rgba(243, 156, 18, 0.2);
        transition: transform 0.3s;
    }
    .stMetric:hover { transform: translateY(-5px); border-color: #ffffff; }

    /* Sezioni */
    .section-card {
        background-color: #161b22;
        padding: 30px;
        border-radius: 20px;
        border-left: 8px solid #f39c12;
        margin-top: 20px;
        box-shadow: 5px 5px 20px rgba(0,0,0,0.4);
    }
    
    /* Bottoni e Toggle */
    .stButton>button {
        background: linear-gradient(45deg, #f39c12, #e67e22);
        color: white !important;
        font-family: 'Orbitron', sans-serif;
        border: none;
        font-weight: bold;
    }
    
    h1, h2, h3 { font-family: 'Orbitron', sans-serif; color: #f39c12 !important; }
    </style>
""", unsafe_allow_html=True)

# --- ENGINE ---
def get_default_data():
    return {
        "config": {"titolo": "AOSR SQUAD", "server": "#000", "motto": "HONOR AND STRENGTH"},
        "stats": {"Membri": "100/100", "S1_Media": "25M", "Power_Rank": "#1"},
        "news": "### 🚩 ORDINI DEL GIORNO\nIn attesa di direttive dal Comando.",
        "s6": "### ⚔️ SEASON 6\nAnalisi tattica in corso.",
        "academy": "### 🎓 TRAINING",
        "drone": "### 🤖 TECH"
    }

def load_db():
    default = get_default_data()
    if GITHUB_TOKEN and REPO_NAME:
        try:
            url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}?ref={BRANCH}"
            headers = {"Authorization": f"token {GITHUB_TOKEN}"}
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                data = json.loads(base64.b64decode(res.json()['content']).decode('utf-8'))
                # Fix "NONE" o chiavi mancanti
                if not data.get("config"): data["config"] = default["config"]
                for k in default:
                    if k not in data: data[k] = default[k]
                return data
        except: pass
    return default

def save_db(data):
    try:
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
        r = requests.get(url, headers=headers)
        sha = r.json().get("sha") if r.status_code == 200 else None
        content = base64.b64encode(json.dumps(data, indent=4).encode()).decode()
        payload = {"message": "AOSR Update", "content": content, "branch": BRANCH}
        if sha: payload["sha"] = sha
        requests.put(url, headers=headers, json=payload, timeout=10)
    except: st.error("Sync Error")

if 'db' not in st.session_state:
    st.session_state.db = load_db()

# --- SIDEBAR ---
st.sidebar.image("https://img.icons8.com/isometric/100/shield.png", width=80)
st.sidebar.markdown(f"## {st.session_state.db['config'].get('titolo', 'AOSR SQUAD')}")
page = st.sidebar.radio("MODULI TATTICI", ["📡 DASHBOARD", "⚔️ SEASON 6", "🎓 ACCADEMIA", "🤖 TECH"])

# --- RENDER ---
if page == "📡 DASHBOARD":
    st.markdown(f"""
        <div class='main-header'>
            <div class='main-title'>{st.session_state.db['config'].get('titolo', 'AOSR SQUAD')}</div>
            <div style='color: white; letter-spacing: 3px;'>{st.session_state.db['config'].get('motto')}</div>
        </div>
    """, unsafe_allow_html=True)

    # Metriche
    s = st.session_state.db.get("stats", {})
    col1, col2, col3 = st.columns(3)
    col1.metric("MEMBRI", s.get("Membri", "100/100"))
    col2.metric("POTENZA S1", s.get("S1_Media", "25M"))
    col3.metric("RANK", s.get("Power_Rank", "#1"))

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Sezione News Editabile
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    c_t, c_e = st.columns([0.8, 0.2])
    with c_t: st.subheader("📢 DIRETTIVE DI GUERRA")
    with c_e: edit = st.toggle("MODIFICA", key="edit_news")
    
    if edit:
        val = st.text_area("Update", value=st.session_state.db.get("news", ""), height=200)
        if st.button("PUBBLICA ORDINI"):
            st.session_state.db["news"] = val
            save_db(st.session_state.db)
            st.rerun()
    else:
        st.markdown(st.session_state.db.get("news"))
    st.markdown("</div>", unsafe_allow_html=True)

    # Pannello Configurazione (Per cambiare Titolo, Motto, etc)
    with st.expander("🛠️ IMPOSTAZIONI AVANZATE SQUADRA"):
        c1, c2 = st.columns(2)
        new_title = c1.text_input("Nome Squadra", st.session_state.db['config'].get('titolo'))
        new_motto = c2.text_input("Motto", st.session_state.db['config'].get('motto'))
        c3, c4, c5 = st.columns(3)
        nm = c3.text_input("Membri", s.get("Membri"))
        np = c4.text_input("Potenza", s.get("S1_Media"))
        nr = c5.text_input("Rank", s.get("Power_Rank"))
        
        if st.button("SALVA CONFIGURAZIONE GLOBALE"):
            st.session_state.db["config"] = {"titolo": new_title, "motto": new_motto}
            st.session_state.db["stats"] = {"Membri": nm, "S1_Media": np, "Power_Rank": nr}
            save_db(st.session_state.db)
            st.rerun()

else:
    # Struttura semplificata per le altre pagine
    key_map = {"⚔️ SEASON 6": "s6", "🎓 ACCADEMIA": "academy", "🤖 TECH": "drone"}
    k = key_map[page]
    st.title(page)
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    edit = st.toggle("EDIT")
    if edit:
        val = st.text_area("Update content", value=st.session_state.db.get(k, ""), height=400)
        if st.button("SALVA"):
            st.session_state.db[k] = val
            save_db(st.session_state.db)
            st.rerun()
    else:
        st.markdown(st.session_state.db.get(k))
    st.markdown("</div>", unsafe_allow_html=True)
