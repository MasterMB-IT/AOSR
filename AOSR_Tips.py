import streamlit as st
from streamlit_elements import elements, mui, html, dashboard
import json
import requests
import base64
import time

# --- CONFIGURAZIONE GITHUB ---
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO_NAME = st.secrets.get("REPO_NAME", "")
DB_FILE = "aosr_titan_db.json"
BRANCH = "main"

st.set_page_config(page_title="AOSR TITAN", layout="wide", initial_sidebar_state="collapsed")

# --- CSS CUSTOM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@500;700&display=swap');
    .stApp { background: #05070a; color: white; font-family: 'Rajdhani', sans-serif; }
    header {visibility: hidden;}
    .img-fluid { max-width: 100%; height: auto; border-radius: 10px; border: 1px solid #f39c12; }
    </style>
""", unsafe_allow_html=True)

# --- ENGINE DI SALVATAGGIO ---
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
            {"i": "meta", "x": 0, "y": 2, "w": 6, "h": 6}
        ],
        "content": {
            "news": "### 📡 TERMINALE TITAN\nUsa il tasto EDIT per configurare.",
            "meta": "### ⚔️ META ANALISI\nIncolla qui il codice immagine."
        }
    }

def save_to_github(data):
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{DB_FILE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    sha = r.json().get("sha") if r.status_code == 200 else None
    content = base64.b64encode(json.dumps(data, indent=4).encode()).decode()
    payload = {"message": "AOSR Titan Sync", "content": content, "sha": sha}
    res = requests.put(url, json=payload, headers=headers)
    if res.status_code in [200, 201]:
        st.toast("🛰️ DATI ARCHIVIATI SU GITHUB", icon="✅")
        st.session_state.db = data # Aggiorna lo stato locale
    else:
        st.error(f"Errore: {res.json().get('message')}")

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

# --- INITIALIZE STATE ---
if "db" not in st.session_state:
    st.session_state.db = load_data()

# --- INTERFACCIA DI COMANDO ---
with st.container():
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        st.markdown("<h1 style='color:#f39c12; font-family:Orbitron; margin:0;'>AOSR TITAN</h1>", unsafe_allow_html=True)
    with c2:
        if st.button("💾 SALVA DEFINITIVO", use_container_width=True):
            save_to_github(st.session_state.db)
    with c3:
        with st.popover("🖼️ CARICA FILE"):
            f = st.file_uploader("Screenshot", type=['png','jpg'])
            if f:
                link = upload_img(f)
                if link:
                    st.success("Copia questo:")
                    st.code(f"![Img]({link})")

# --- DASHBOARD LOGIC ---
with elements("titan_dashboard"):
    # Carichiamo il layout salvato. Se l'utente sposta qualcosa, aggiorniamo lo stato.
    layout = st.session_state.db["layout"]
    
    with dashboard.Grid(layout, onLayoutChange=lambda l: st.session_state.db.update({"layout": l})):
        
        for key in st.session_state.db["content"].keys():
            # Stile dinamico in base alla card
            color = "#f39c12" if key == "news" else "#3498db"
            title = key.upper()

            with mui.Card(key=key, sx={
                "display": "flex", "flexDirection": "column", 
                "bgcolor": "#0d1117", "border": f"1px solid {color}",
                "borderRadius": "12px", "overflow": "hidden"
            }):
                # HEADER CARD
                mui.CardHeader(
                    title=title, 
                    titleTypographyProps={"variant": "subtitle1", "fontFamily": "Orbitron", "color": color},
                    sx={"padding": "8px 16px", "borderBottom": f"1px solid {color}33", "bgcolor": "#161b22"}
                )
                
                # CORPO CARD
                with mui.CardContent(sx={"flex": 1, "overflow": "auto", "padding": "15px", "color": "#e6edf3"}):
                    # Se l'utente attiva l'edit per questa card specifica
                    if st.sidebar.checkbox(f"Modifica {title}", key=f"tg_{key}"):
                        st.session_state.db["content"][key] = st.text_area(
                            "Editor Markdown:", 
                            st.session_state.db["content"][key], 
                            height=300, 
                            key=f"area_{key}"
                        )
                    else:
                        # RENDERIZZAZIONE MARKDOWN (Immagini e Testo)
                        # Usiamo html.div per iniettare il markdown processato da Streamlit
                        # In alternativa usiamo direttamente il markdown di streamlit
                        st.markdown(st.session_state.db["content"][key])

st.sidebar.markdown("---")
st.sidebar.info("💡 Attiva i checkbox sopra per editare i testi delle card. Trascina i bordi per ridimensionare.")
