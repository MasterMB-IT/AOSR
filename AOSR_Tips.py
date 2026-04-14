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

st.set_page_config(page_title="AOSR MASTER ARCHITECT", layout="wide")

# --- CSS CUSTOM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@500;700&display=swap');
    .stApp { background: #05070a; color: white; font-family: 'Rajdhani', sans-serif; }
    .section-card {
        background: rgba(22, 27, 34, 0.7); padding: 25px; border-radius: 15px;
        border-left: 5px solid #f39c12; margin-bottom: 20px; border: 1px solid #30363d;
    }
    .edit-box { background: #1c2128; border: 1px dashed #f39c12; padding: 10px; border-radius: 10px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- ENGINE ---
def load_db():
    try:
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{DB_FILE}?t={int(time.time())}"
        res = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
        if res.status_code == 200:
            return json.loads(base64.b64decode(res.json()['content']).decode())
    except: pass
    return {
        "motto": "HONOR - STRENGTH",
        "sections": {
            "METE": {"titolo": "⚔️ ANALISI META", "tabs": [{"label": "Tier List", "content": ""}]},
            "TECH": {"titolo": "🧬 TECNOLOGIE", "tabs": [{"label": "Ricerche", "content": ""}]}
        }
    }

def save_db(data):
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{DB_FILE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    sha = r.json().get("sha") if r.status_code == 200 else None
    content = base64.b64encode(json.dumps(data, indent=4).encode()).decode()
    payload = {"message": "Master Update", "content": content, "sha": sha}
    if requests.put(url, json=payload, headers=headers).status_code in [200, 201]:
        st.toast("✅ SISTEMA AGGIORNATO", icon="🛡️")
        time.sleep(1)
        st.rerun()

if 'db' not in st.session_state:
    st.session_state.db = load_db()

# --- HEADER & MASTER SWITCH ---
c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    st.markdown(f"<h1 style='color:#f39c12; font-family:Orbitron;'>AOSR OVERLORD</h1>", unsafe_allow_html=True)
with c2:
    mode = st.toggle("🛠️ MODALITÀ ARCHITETTO (EDIT)", value=False)
with c3:
    if st.button("💾 SALVA CONFIGURAZIONE", use_container_width=True):
        save_db(st.session_state.db)

# --- TOOL IMMAGINI NELLA SIDEBAR ---
with st.sidebar:
    st.title("🖼️ MEDIA CENTER")
    img_file = st.file_uploader("Carica Immagine", type=['png','jpg'])
    if img_file and st.button("GENERA CODICE"):
        # Logica upload veloce (usa cartella img/)
        path = f"img/{img_file.name}"
        b64 = base64.b64encode(img_file.getvalue()).decode()
        requests.put(f"https://api.github.com/repos/{REPO_NAME}/contents/{path}", 
                     json={"message":"img","content":b64}, headers={"Authorization":f"token {GITHUB_TOKEN}"})
        st.code(f"![Img](https://raw.githubusercontent.com/{REPO_NAME}/{BRANCH}/{path})")

# --- RENDER DINAMICO ---
for sec_id, sec_data in list(st.session_state.db["sections"].items()):
    with st.container():
        # Titolo Sezione Editabile
        if mode:
            c_tit, c_del = st.columns([0.9, 0.1])
            sec_data["titolo"] = c_tit.text_input(f"Titolo Sezione {sec_id}", sec_data["titolo"], key=f"title_{sec_id}")
            if c_del.button("🗑️", key=f"del_sec_{sec_id}"):
                del st.session_state.db["sections"][sec_id]
                st.rerun()
        else:
            st.header(sec_data["titolo"])

        # Gestione Tabs
        tabs_list = sec_data["tabs"]
        tab_obj = st.tabs([t["label"] for t in tabs_list] + (["➕ Aggiungi Tab"] if mode else []))

        for i, t in enumerate(tabs_list):
            with tab_obj[i]:
                st.markdown("<div class='section-card'>", unsafe_allow_html=True)
                if mode:
                    t["label"] = st.text_input("Nome Sottosezione:", t["label"], key=f"lab_{sec_id}_{i}")
                    t["content"] = st.text_area("Contenuto (Markdown/Immagini):", t["content"], height=300, key=f"cont_{sec_id}_{i}")
                    if st.button(f"Elimina {t['label']}", key=f"del_tab_{sec_id}_{i}"):
                        sec_data["tabs"].pop(i)
                        st.rerun()
                else:
                    st.markdown(t["content"])
                st.markdown("</div>", unsafe_allow_html=True)
        
        # Logica per aggiungere nuovo Tab
        if mode and len(tab_obj) > len(tabs_list):
            with tab_obj[-1]:
                if st.button("➕ CREA NUOVA SOTTOSEZIONE", key=f"add_tab_{sec_id}"):
                    sec_data["tabs"].append({"label": "Nuova Tab", "content": ""})
                    st.rerun()

st.divider()

# --- AGGIUNGI NUOVA SEZIONE PRINCIPALE ---
if mode:
    if st.button("🚀 AGGIUNGI NUOVA SEZIONE PRINCIPALE"):
        new_id = f"SEC_{int(time.time())}"
        st.session_state.db["sections"][new_id] = {"titolo": "NUOVA SEZIONE", "tabs": [{"label": "Inizio", "content": ""}]}
        st.rerun()
