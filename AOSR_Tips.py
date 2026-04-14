import streamlit as st
import json
import requests
import base64
import time

# --- CONFIGURAZIONE GITHUB ---
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO_NAME = st.secrets.get("REPO_NAME", "")
BRANCH = "main"
DB_FILE = "aosr_master_db.json"

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="AOSR COMMAND CENTER", layout="wide", initial_sidebar_state="expanded")

# --- UI DESIGN (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@500;700&display=swap');
    
    .stApp { background: #05070a; color: white; font-family: 'Rajdhani', sans-serif; }
    
    /* Stile Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 2px solid #f39c12;
    }
    
    /* Titoli Sezioni nel corpo */
    .section-header {
        font-family: 'Orbitron', sans-serif;
        color: #f39c12;
        padding: 10px;
        border-bottom: 2px solid #f39c12;
        margin-bottom: 20px;
        text-shadow: 0 0 10px #f39c12;
    }

    .section-card {
        background: rgba(22, 27, 34, 0.8); 
        padding: 25px; 
        border-radius: 15px;
        border: 1px solid #30363d;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    
    /* Bottoni Sidebar */
    .stRadio [data-testid="stWidgetLabel"] { display: none; }
    div[role="radiogroup"] { gap: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- CORE ENGINE ---
def load_db():
    try:
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{DB_FILE}?t={int(time.time())}"
        res = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
        if res.status_code == 200:
            return json.loads(base64.b64decode(res.json()['content']).decode())
    except: pass
    return {
        "sections": {
            "DASHBOARD": {"titolo": "📡 DASHBOARD OPERATIVA", "tabs": [{"label": "Status", "content": "Sistema Attivo."}]},
            "META": {"titolo": "⚔️ ANALISI TATTICA", "tabs": [{"label": "Sinergie", "content": ""}]}
        }
    }

def save_db(data):
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{DB_FILE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    sha = r.json().get("sha") if r.status_code == 200 else None
    content = base64.b64encode(json.dumps(data, indent=4).encode()).decode()
    payload = {"message": "Update Layout", "content": content, "sha": sha}
    if requests.put(url, json=payload, headers=headers).status_code in [200, 201]:
        st.toast("✅ ARCHIVIO AGGIORNATO", icon="🛰️")
        time.sleep(0.5)
        st.rerun()

if 'db' not in st.session_state:
    st.session_state.db = load_db()

# --- SIDEBAR: MENU TATTICO ---
with st.sidebar:
    st.markdown(f"<h1 style='color:#f39c12; font-family:Orbitron; font-size:22px;'>AOSR COMMAND</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Switch Architetto
    mode = st.toggle("🛠️ ARCHITETTO", value=False)
    
    st.markdown("### ⚡ NAVIGAZIONE RAPIDA")
    # Generiamo dinamicamente le opzioni del menu dalle sezioni del DB
    options = list(st.session_state.db["sections"].keys())
    # Se siamo in modalità architetto, aggiungiamo una voce per gestire le sezioni
    selected_sec = st.radio("Scegli Settore:", options)
    
    st.markdown("---")
    if st.button("💾 SALVA MODIFICHE", use_container_width=True):
        save_db(st.session_state.db)
    
    # Media Manager integrato in basso
    with st.expander("🖼️ MEDIA MANAGER"):
        img = st.file_uploader("Upload", type=['png','jpg'])
        if img:
            path = f"img/{img.name}"
            b64 = base64.b64encode(img.getvalue()).decode()
            requests.put(f"https://api.github.com/repos/{REPO_NAME}/contents/{path}", 
                         json={"message":"img","content":b64}, headers={"Authorization":f"token {GITHUB_TOKEN}"})
            st.code(f"![Img](https://raw.githubusercontent.com/{REPO_NAME}/{BRANCH}/{path})")

# --- AREA DI LAVORO CENTRALE ---
sec_data = st.session_state.db["sections"][selected_sec]

# Titolo Sezione con possibilità di rinomina se in modalità ARCHITETTO
if mode:
    new_title = st.text_input("Rinomina questa Sezione:", sec_data["titolo"])
    sec_data["titolo"] = new_title
    if st.button("🚀 AGGIUNGI NUOVA SEZIONE PRINCIPALE"):
        new_id = f"NEW_{int(time.time())}"
        st.session_state.db["sections"][new_id] = {"titolo": "NUOVO SETTORE", "tabs": [{"label": "Main", "content": ""}]}
        st.rerun()
    if st.button("🗑️ ELIMINA QUESTA INTERA SEZIONE"):
        if len(st.session_state.db["sections"]) > 1:
            del st.session_state.db["sections"][selected_sec]
            st.rerun()
else:
    st.markdown(f"<div class='section-header'>{sec_data['titolo']}</div>", unsafe_allow_html=True)

# Gestione Sottosezioni (Tabs)
tabs_list = sec_data["tabs"]
# Visualizzazione Tab
tab_titles = [t["label"] for t in tabs_list]
if mode: tab_titles.append("➕")

tabs = st.tabs(tab_titles)

for i, t in enumerate(tabs_list):
    with tabs[i]:
        if mode:
            t["label"] = st.text_input(f"Titolo Tab {i+1}", t["label"], key=f"lab_{selected_sec}_{i}")
            t["content"] = st.text_area("Contenuto Markdown/Immagini:", t["content"], height=400, key=f"txt_{selected_sec}_{i}")
            if st.button(f"Rimuovi Tab {t['label']}", key=f"del_{selected_sec}_{i}"):
                sec_data["tabs"].pop(i)
                st.rerun()
        else:
            st.markdown(f"<div class='section-card'>", unsafe_allow_html=True)
            st.markdown(t["content"])
            st.markdown("</div>", unsafe_allow_html=True)

# Tasto aggiunta tab
if mode and len(tabs) > len(tabs_list):
    with tabs[-1]:
        if st.button("➕ CREA NUOVA TAB QUI"):
            sec_data["tabs"].append({"label": "Nuovo", "content": ""})
            st.rerun()
