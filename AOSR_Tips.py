import streamlit as st
from streamlit_elements import elements, mui, html, dashboard
import json
import requests
import base64
import time

# --- CONFIGURAZIONE GITHUB ---
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO_NAME = st.secrets.get("REPO_NAME", "")
DB_FILE = "aosr_overlord_db.json"
BRANCH = "main"

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="AOSR ARCHITECT", layout="wide", initial_sidebar_state="collapsed")

# --- UI CSS CUSTOM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@500;700&display=swap');
    .main { background: #05070a; font-family: 'Rajdhani', sans-serif; }
    .stApp { background: #05070a; }
    /* Nascondi header standard per più spazio */
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- CORE ENGINE ---
def load_data():
    try:
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{DB_FILE}?t={int(time.time())}"
        res = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
        if res.status_code == 200:
            return json.loads(base64.b64decode(res.json()['content']).decode())
    except: pass
    return {
        "layout": [
            {"i": "news", "x": 0, "y": 0, "w": 12, "h": 2},
            {"i": "meta", "x": 0, "y": 2, "w": 6, "h": 4},
            {"i": "tech", "x": 6, "y": 2, "w": 6, "h": 4},
            {"i": "routine", "x": 0, "y": 6, "w": 12, "h": 3}
        ],
        "content": {
            "news": "### 📡 TERMINALE ATTIVO\nBenvenuto Comandante. Trascina le card per configurare la dashboard.",
            "meta": "### ⚔️ META SQUAD\nIncolla qui le tue sinergie.",
            "tech": "### 🧬 TECNOLOGIE\nPianificazione ricerche.",
            "routine": "### 📋 ROUTINE\nChecklist giornaliera."
        }
    }

def save_all(data):
    try:
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{DB_FILE}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        r = requests.get(url, headers=headers)
        sha = r.json().get("sha") if r.status_code == 200 else None
        content = base64.b64encode(json.dumps(data, indent=4).encode()).decode()
        payload = {"message": "AOSR Architect Layout Update", "content": content, "sha": sha}
        requests.put(url, json=payload, headers=headers)
        st.toast("🛰️ CONFIGURAZIONE SALVATA NEL CLOUD", icon="✅")
    except: st.error("Errore salvataggio")

def upload_img(file):
    path = f"img/{file.name.replace(' ', '_')}"
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    res = requests.get(url, headers=headers)
    sha = res.json().get("sha") if res.status_code == 200 else None
    content = base64.b64encode(file.getvalue()).decode()
    payload = {"message": "Upload Img", "content": content, "sha": sha}
    r = requests.put(url, json=payload, headers=headers)
    if r.status_code in [200, 201]:
        return f"https://raw.githubusercontent.com/{REPO_NAME}/{BRANCH}/{path}"
    return None

# --- STATE ---
if "db" not in st.session_state:
    st.session_state.db = load_data()

# --- HEADER SUPERIORE ---
with st.container():
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        st.markdown("<h1 style='color:#f39c12; font-family:Orbitron; margin:0;'>AOSR OVERLORD <span style='font-size:15px; color:white;'>ARCHITECT v3</span></h1>", unsafe_allow_html=True)
    with c2:
        if st.button("💾 SALVA LAYOUT E CONTENUTI", use_container_width=True):
            save_all(st.session_state.db)
    with c3:
        with st.popover("📤 CARICA IMMAGINE"):
            f = st.file_uploader("Screenshot", type=['png','jpg'])
            if f:
                link = upload_img(f)
                if link: st.code(f"![Img]({link})")

# --- DASHBOARD DINAMICA ---
with elements("dashboard"):
    # Layout dinamico: onLayoutChange aggiorna lo stato ma non salva su GitHub (serve il tasto Save)
    with dashboard.Grid(st.session_state.db["layout"], onLayoutChange=lambda l: st.session_state.db.update({"layout": l})):
        
        # DEFINIZIONE DELLE CARD
        cards = [
            ("news", "📡 COMANDI RAPIDI", "#f39c12"),
            ("meta", "⚔️ ANALISI META", "#e74c3c"),
            ("tech", "🧬 RAMO TECNOLOGICO", "#3498db"),
            ("routine", "📋 ROUTINE CRESCITA", "#2ecc71")
        ]

        for key, title, color in cards:
            with mui.Card(key=key, sx={
                "display": "flex", "flexDirection": "column", 
                "bgcolor": "#161b22", "border": f"1px solid {color}",
                "borderRadius": "15px", "boxShadow": f"0 0 15px {color}33"
            }):
                mui.CardHeader(
                    title=title, 
                    titleTypographyProps={"variant": "h6", "fontFamily": "Orbitron", "color": color},
                    sx={"padding": "10px 20px", "borderBottom": f"1px solid {color}33"}
                )
                
                with mui.CardContent(sx={"flex": 1, "overflow": "auto", "padding": "20px"}):
                    # Area di Editing dentro la card
                    if st.toggle(f"EDIT", key=f"tg_{key}"):
                        new_txt = st.text_area("Markdown:", st.session_state.db["content"][key], height=250, key=f"area_{key}")
                        st.session_state.db["content"][key] = new_txt
                    else:
                        st.markdown(st.session_state.db["content"][key])

st.caption("💡 Trascina i bordi delle card per ridimensionarle. Clicca sul titolo per spostarle.")
