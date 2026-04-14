import streamlit as st
from streamlit_elements import elements, mui, html, dashboard
import json
import requests
import base64
import time

# --- CONFIGURAZIONE GITHUB ---
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO_NAME = st.secrets.get("REPO_NAME", "")
DB_FILE = "aosr_layout_db.json"

st.set_page_config(page_title="AOSR CUSTOM BUILDER", layout="wide")

# --- DATABASE LOGIC ---
def load_layout():
    try:
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{DB_FILE}?t={int(time.time())}"
        res = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
        if res.status_code == 200:
            return json.loads(base64.b64decode(res.json()['content']).decode())
    except: pass
    # Layout di default se il file non esiste
    return [
        {"i": "meta", "x": 0, "y": 0, "w": 6, "h": 4},
        {"i": "tech", "x": 6, "y": 0, "w": 6, "h": 4},
        {"i": "routine", "x": 0, "y": 4, "w": 12, "h": 3},
    ]

def save_layout(layout):
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{DB_FILE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    sha = r.json().get("sha") if r.status_code == 200 else None
    content = base64.b64encode(json.dumps(layout).encode()).decode()
    payload = {"message": "Save Layout", "content": content, "sha": sha}
    requests.put(url, json=payload, headers=headers)
    st.toast("📐 Layout salvato nel Cloud!")

# --- UI ---
st.title("🛡️ AOSR ESTRATEGIC BUILDER")
st.caption("Trascina l'angolo in basso a destra per ridimensionare o sposta le card col mouse.")

if "layout" not in st.session_state:
    st.session_state.layout = load_layout()

# Bottone per salvare la posizione attuale
if st.button("💾 BLOCCA POSIZIONI E SALVA SCHEMA"):
    save_layout(st.session_state.layout)

# --- AREA DRAG & DROP ---
with elements("dashboard"):
    # Configurazione della griglia (12 colonne totali)
    with dashboard.Grid(st.session_state.layout, onLayoutChange=lambda l: st.session_state.update({"layout": l})):
        
        # CARD: META
        with mui.Card(key="meta", sx={"display": "flex", "flexDirection": "column", "bgcolor": "#161b22", "border": "1px solid #f39c12"}):
            mui.CardHeader(title="⚔️ META SQUAD", sx={"color": "#f39c12"})
            with mui.CardContent(sx={"flex": 1, "overflow": "auto", "color": "white"}):
                html.div("Qui puoi inserire le tue sinergie. Sposta questa card dove preferisci.")

        # CARD: TECH
        with mui.Card(key="tech", sx={"display": "flex", "flexDirection": "column", "bgcolor": "#161b22", "border": "1px solid #f39c12"}):
            mui.CardHeader(title="🧬 TECNOLOGIE", sx={"color": "#f39c12"})
            with mui.CardContent(sx={"flex": 1, "overflow": "auto", "color": "white"}):
                html.div("Pianificazione ricerche. Ridimensionami per vedere più dettagli.")

        # CARD: ROUTINE
        with mui.Card(key="routine", sx={"display": "flex", "flexDirection": "column", "bgcolor": "#161b22", "border": "1px solid #f39c12"}):
            mui.CardHeader(title="📋 ROUTINE QUOTIDIANA", sx={"color": "#f39c12"})
            with mui.CardContent(sx={"flex": 1, "overflow": "auto", "color": "white"}):
                html.div("Checklist mattutina e obiettivi.")
