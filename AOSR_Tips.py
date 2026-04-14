import streamlit as st
import json
import os
import requests
import base64
import time

# --- CONFIGURAZIONE GITHUB (Verifica sempre i permessi repo!) ---
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO_NAME = st.secrets.get("REPO_NAME", "")
FILE_PATH = "aosr_squad_db.json"
BRANCH = "main"

st.set_page_config(page_title="AOSR SQUAD HQ", layout="wide")

# --- STYLE (MANTENUTO) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .main { background-color: #0b0e14; }
    .stMetric { background-color: rgba(22, 27, 34, 0.8); border: 1px solid #f39c12; border-radius: 15px !important; padding: 20px !important;}
    .section-card { background-color: #161b22; padding: 30px; border-radius: 20px; border-left: 8px solid #f39c12; margin-top: 20px;}
    .stButton>button { background: linear-gradient(45deg, #f39c12, #e67e22); color: white !important; font-family: 'Orbitron', sans-serif; font-weight: bold;}
    h1, h2, h3, h4 { font-family: 'Orbitron', sans-serif; color: #f39c12 !important; }
    /* Style per i TAB */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #1c2128; border-radius: 5px; color: white; padding: 10px 20px; }
    .stTabs [aria-selected="true"] { background-color: #f39c12; color: black; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# --- ENGINE (MANTENUTO) ---
def get_default_data():
    return {
        "config": {"titolo": "AOSR SQUAD", "motto": "Elite Soldiers"},
        "box1": {"label": "MEMBRI", "value": "100/100"},
        "box2": {"label": "POTENZA S1", "value": "25M"},
        "box3": {"label": "RANK", "value": "#1"},
        "news": "### 📢 BENVENUTI AL COMANDO\nUtilizza i moduli per le direttive.",
        # Struttura per la sezione META a schede
        "meta": {
            "tier_list": "### 🏆 TIER LIST ATTUALE\n\n![Esempio Immagine](https://i.imgur.com/8Q4SjD0.png)\n\nScrivi qui la descrizione...",
            "sinergie": "### 🤝 SINERGIE CHIAVE\n\nSpiegazione delle combo...",
            "counter": "### 🛡️ COUNTER-META S6\n\nCome battere le squadre comuni..."
        },
        "tech": "### 🧬 TECH & GEER", "academy": "### 🎓 TRAINING"
    }

def load_db():
    if GITHUB_TOKEN and REPO_NAME:
        try:
            url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}?ref={BRANCH}&t={int(time.time())}"
            headers = {"Authorization": f"token {GITHUB_TOKEN}", "Cache-Control": "no-cache"}
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                data = json.loads(base64.b64decode(res.json()['content']).decode('utf-8'))
                # Verifica integrità chiavi
                default = get_default_data()
                for key in default:
                    if key not in data: data[key] = default[key]
                return data
        except Exception as e: st.error(f"Errore caricamento: {e}")
    return get_default_data()

def save_db(data):
    with st.spinner("Sincronizzazione Cloud in corso..."):
        try:
            url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
            headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
            r = requests.get(url, headers=headers, params={"t": int(time.time())})
            sha = r.json().get("sha") if r.status_code == 200 else None
            content = base64.b64encode(json.dumps(data, indent=4).encode()).decode()
            payload = {"message": "AOSR Update", "content": content, "branch": BRANCH}
            if sha: payload["sha"] = sha
            res = requests.put(url, headers=headers, json=payload, timeout=15)
            if res.status_code in [200, 201]:
                st.success("✅ DATI SALVATI!"); time.sleep(1); st.rerun()
                return True
            else: st.error(f"Errore GitHub {res.status_code}: {res.json().get('message')}")
        except Exception as e: st.error(f"Errore connessione: {e}")
    return False

if 'db' not in st.session_state:
    st.session_state.db = load_db()

# --- SIDEBAR ---
st.sidebar.markdown(f"# 🛡️ AOSR SQUAD")
page = st.sidebar.radio("MODULI TATTICI", ["📡 DASHBOARD", "⚔️ META & SINERGIE", "🎓 ACCADEMIA", "🤖 TECH"])

# --- DASHBOARD (MANTENUTA) ---
if page == "📡 DASHBOARD":
    st.markdown(f"<div class='main-header'><div class='main-title'>AOSR SQUAD</div></div>", unsafe_allow_html=True)
    # ... (logica dei riquadri e news, omessa per brevità ma presente nel tuo codice attuale)

# --- NUOVA SEZIONE: META & SINERGIE (A SCHEDE) ---
elif page == "⚔️ META & SINERGIE":
    st.title("⚔️ Analisi Tattica & Meta")
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    
    # Creazione dei TAB
    tab1, tab2, tab3 = st.tabs(["🏆 Tier List", "🤝 Sinergie Eroi", "🛡️ Counter S6"])
    
    meta_data = st.session_state.db.get("meta", {})
    
    # TAB 1: Tier List
    with tab1:
        c_ed, c_v = st.columns([0.2, 0.8])
        with c_ed: edit = st.toggle("EDIT", key="ed_tier")
        
        if edit:
            new_val = st.text_area("Update content (usa ![Testo](link_immagine) per foto):", value=meta_data.get("tier_list", ""), height=400, key="ta_tier")
            if st.button("💾 SALVA TIER LIST", key="bt_tier"):
                st.session_state.db["meta"]["tier_list"] = new_val
                save_db(st.session_state.db)
        else:
            st.markdown(meta_data.get("tier_list", ""))

    # TAB 2: Sinergie
    with tab2:
        c_ed2, c_v2 = st.columns([0.2, 0.8])
        with c_ed2: edit2 = st.toggle("EDIT", key="ed_sin")
        if edit2:
            new_val2 = st.text_area("Update content:", value=meta_data.get("sinergie", ""), height=400, key="ta_sin")
            if st.button("💾 SALVA SINERGIE", key="bt_sin"):
                st.session_state.db["meta"]["sinergie"] = new_val2
                save_db(st.session_state.db)
        else:
            st.markdown(meta_data.get("sinergie", ""))

    # TAB 3: Counter
    with tab3:
        c_ed3, c_v3 = st.columns([0.2, 0.8])
        with c_ed3: edit3 = st.toggle("EDIT", key="ed_cou")
        if edit3:
            new_val3 = st.text_area("Update content:", value=meta_data.get("counter", ""), height=400, key="ta_cou")
            if st.button("💾 SALVA COUNTER", key="bt_cou"):
                st.session_state.db["meta"]["counter"] = new_val3
                save_db(st.session_state.db)
        else:
            st.markdown(meta_data.get("counter", ""))
            
    st.markdown("</div>", unsafe_allow_html=True)

# --- ALTRE PAGINE (MANTENUTE) ---
else:
    key_map = {"🎓 ACCADEMIA": "academy", "🤖 TECH": "drone"}
    k = key_map[page]
    st.title(page)
    # ... (logica standard omessa per brevità)
