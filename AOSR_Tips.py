import streamlit as st
import json
import os
import requests
import base64
import time

# --- CONFIGURAZIONE GITHUB ---
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
    .main-header {
        background: linear-gradient(90deg, #161b22 0%, #30363d 50%, #161b22 100%);
        padding: 20px; border-radius: 10px; border-bottom: 4px solid #f39c12;
        text-align: center; margin-bottom: 30px; box-shadow: 0px 10px 20px rgba(0,0,0,0.5);
    }
    .main-title {
        font-family: 'Orbitron', sans-serif; color: #f39c12;
        font-size: 50px; font-weight: 700; text-transform: uppercase;
        letter-spacing: 5px; margin: 0;
    }
    .stMetric {
        background: rgba(22, 27, 34, 0.8); border: 1px solid #f39c12;
        border-radius: 15px !important; padding: 20px !important;
    }
    .section-card {
        background-color: #161b22; padding: 30px; border-radius: 20px;
        border-left: 8px solid #f39c12; margin-top: 20px;
    }
    .stButton>button {
        background: linear-gradient(45deg, #f39c12, #e67e22);
        color: white !important; font-family: 'Orbitron', sans-serif;
        font-weight: bold;
    }
    h1, h2, h3 { font-family: 'Orbitron', sans-serif; color: #f39c12 !important; }
    </style>
""", unsafe_allow_html=True)

# --- ENGINE DI RECUPERO DATI (CON FORZATURA CACHE) ---
def get_default_data():
    return {
        "config": {"titolo": "AOSR SQUAD", "motto": "Elite Soldiers"},
        "box1": {"label": "MEMBRI", "value": "100/100"},
        "box2": {"label": "POTENZA S1", "value": "25M"},
        "box3": {"label": "RANK", "value": "#1"},
        "news": "### 🚩 ORDINI DEL GIORNO\nBenvenuti al Comando.",
        "s6": "### ⚔️ SEASON 6", "academy": "### 🎓 TRAINING", "drone": "### 🤖 TECH"
    }

def load_db():
    if GITHUB_TOKEN and REPO_NAME:
        try:
            # Aggiungiamo un parametro casuale (t) per bypassare la cache di GitHub
            url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}?ref={BRANCH}&t={int(time.time())}"
            headers = {"Authorization": f"token {GITHUB_TOKEN}", "Cache-Control": "no-cache"}
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                data = json.loads(base64.b64decode(res.json()['content']).decode('utf-8'))
                return data
        except Exception as e:
            st.error(f"Errore caricamento: {e}")
    return get_default_data()

def save_db(data):
    with st.spinner("Sincronizzazione Cloud in corso..."):
        try:
            url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
            headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
            
            # 1. Recuperiamo lo SHA più recente
            r = requests.get(url, headers=headers, params={"ref": BRANCH, "t": int(time.time())})
            sha = r.json().get("sha") if r.status_code == 200 else None
            
            # 2. Prepariamo il contenuto
            content = base64.b64encode(json.dumps(data, indent=4).encode()).decode()
            payload = {"message": "AOSR Secure Save", "content": content, "branch": BRANCH}
            if sha: payload["sha"] = sha
            
            # 3. Invio
            res = requests.put(url, headers=headers, json=payload, timeout=15)
            if res.status_code in [200, 201]:
                st.success("✅ DATI SALVATI SU GITHUB!")
                time.sleep(1) # Diamo tempo a GitHub di digerire il file
                return True
            else:
                st.error(f"Errore GitHub: {res.text}")
        except Exception as e:
            st.error(f"Errore connessione: {e}")
    return False

# Gestione sessione: carichiamo i dati solo se non ci sono già o se forziamo il refresh
if 'db' not in st.session_state:
    st.session_state.db = load_db()

# --- SIDEBAR E NAVIGAZIONE ---
st.sidebar.markdown(f"# 🛡️ AOSR SQUAD")
page = st.sidebar.radio("MODULI TATTICI", ["📡 DASHBOARD", "⚔️ SEASON 6", "🎓 ACCADEMIA", "🤖 TECH"])

if page == "📡 DASHBOARD":
    st.markdown(f"""
        <div class='main-header'>
            <div class='main-title'>AOSR SQUAD</div>
            <div style='color: white; letter-spacing: 3px; font-family: Orbitron;'>{st.session_state.db['config'].get('motto')}</div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    b1, b2, b3 = st.session_state.db.get('box1', {}), st.session_state.db.get('box2', {}), st.session_state.db.get('box3', {})
    
    col1.metric(label=b1.get('label', 'MEMBRI'), value=b1.get('value', '0'))
    col2.metric(label=b2.get('label', 'POTENZA'), value=b2.get('value', '0'))
    col3.metric(label=b3.get('label', 'RANK'), value=b3.get('value', '0'))

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    c_t, c_e = st.columns([0.8, 0.2])
    with c_t: st.subheader("📢 DIRETTIVE DI GUERRA")
    with c_e: edit = st.toggle("MODIFICA", key="edit_news")
    
    if edit:
        val = st.text_area("Update", value=st.session_state.db.get("news", ""), height=200)
        if st.button("PUBBLICA ORDINI"):
            st.session_state.db["news"] = val
            if save_db(st.session_state.db):
                st.rerun()
    else:
        st.markdown(st.session_state.db.get("news"))
    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("🛠️ CONFIGURAZIONE RIQUADRI E HEADER"):
        c1, c2 = st.columns(2)
        nb1_l = c1.text_input("Etichetta Box 1", b1.get('label', 'MEMBRI'))
        nb1_v = c2.text_input("Valore Box 1", b1.get('value', '0'))
        c3, c4 = st.columns(2)
        nb2_l = c3.text_input("Etichetta Box 2", b2.get('label', 'POTENZA'))
        nb2_v = c4.text_input("Valore Box 2", b2.get('value', '0'))
        c5, c6 = st.columns(2)
        nb3_l = c5.text_input("Etichetta Box 3", b3.get('label', 'RANK'))
        nb3_v = c6.text_input("Valore Box 3", b3.get('value', '0'))
        
        st.divider()
        new_motto = st.text_input("Modifica Motto", st.session_state.db['config'].get('motto'))
        
        if st.button("SALVA CONFIGURAZIONE"):
            st.session_state.db['box1'] = {"label": nb1_l, "value": nb1_v}
            st.session_state.db['box2'] = {"label": nb2_l, "value": nb2_v}
            st.session_state.db['box3'] = {"label": nb3_l, "value": nb3_v}
            st.session_state.db['config']['motto'] = new_motto
            if save_db(st.session_state.db):
                st.rerun()
else:
    key_map = {"⚔️ SEASON 6": "s6", "🎓 ACCADEMIA": "academy", "🤖 TECH": "drone"}
    k = key_map[page]
    st.title(page)
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    edit_p = st.toggle("EDIT")
    if edit_p:
        val_p = st.text_area("Update", value=st.session_state.db.get(k, ""), height=400)
        if st.button("SALVA CONTENUTO"):
            st.session_state.db[k] = val_p
            if save_db(st.session_state.db):
                st.rerun()
    else:
        st.markdown(st.session_state.db.get(k))
    st.markdown("</div>", unsafe_allow_html=True)
