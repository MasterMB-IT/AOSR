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

# --- STYLE AOSR ULTIMATE (MANTENUTO E MIGLIORATO) ---
st.set_page_config(page_title="AOSR SQUAD HQ", layout="wide")

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
        box-shadow: 0 0 15px rgba(243, 156, 18, 0.2);
    }
    .section-card {
        background-color: #161b22; padding: 30px; border-radius: 20px;
        border-left: 8px solid #f39c12; margin-top: 20px;
    }
    .stButton>button {
        background: linear-gradient(45deg, #f39c12, #e67e22);
        color: white !important; font-family: 'Orbitron', sans-serif;
        border: none; font-weight: bold; height: 3em;
    }
    h1, h2, h3 { font-family: 'Orbitron', sans-serif; color: #f39c12 !important; }
    </style>
""", unsafe_allow_html=True)

# --- ENGINE ---
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
    default = get_default_data()
    if GITHUB_TOKEN and REPO_NAME:
        try:
            url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}?ref={BRANCH}"
            headers = {"Authorization": f"token {GITHUB_TOKEN}"}
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                data = json.loads(base64.b64decode(res.json()['content']).decode('utf-8'))
                # Verifica integrità chiavi
                for key in default:
                    if key not in data: data[key] = default[key]
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
    except: st.error("Errore di sincronizzazione GitHub")

if 'db' not in st.session_state:
    st.session_state.db = load_db()

# --- SIDEBAR ---
st.sidebar.markdown(f"# 🛡️ {st.session_state.db['config'].get('titolo')}")
page = st.sidebar.radio("MODULI TATTICI", ["📡 DASHBOARD", "⚔️ SEASON 6", "🎓 ACCADEMIA", "🤖 TECH"])

if page == "📡 DASHBOARD":
    # HEADER FISSO AOSR SQUAD
    st.markdown(f"""
        <div class='main-header'>
            <div class='main-title'>AOSR SQUAD</div>
            <div style='color: white; letter-spacing: 3px; font-family: Orbitron;'>{st.session_state.db['config'].get('motto')}</div>
        </div>
    """, unsafe_allow_html=True)

    # I TRE RIQUADRI EDITABILI
    col1, col2, col3 = st.columns(3)
    b1, b2, b3 = st.session_state.db['box1'], st.session_state.db['box2'], st.session_state.db['box3']
    
    col1.metric(label=b1['label'], value=b1['value'])
    col2.metric(label=b2['label'], value=b2['value'])
    col3.metric(label=b3['label'], value=b3['value'])

    st.markdown("<br>", unsafe_allow_html=True)
    
    # SEZIONE NEWS
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

    # PANNELLO DI CONTROLLO AVANZATO PER I RIQUADRI
    with st.expander("🛠️ CONFIGURAZIONE RIQUADRI E HEADER"):
        st.write("### Modifica i tre box superiori")
        c1, c2 = st.columns(2)
        nb1_l = c1.text_input("Etichetta Box 1", b1['label'])
        nb1_v = c2.text_input("Valore Box 1", b1['value'])
        
        c3, c4 = st.columns(2)
        nb2_l = c3.text_input("Etichetta Box 2", b2['label'])
        nb2_v = c4.text_input("Valore Box 2", b2['value'])
        
        c5, c6 = st.columns(2)
        nb3_l = c5.text_input("Etichetta Box 3", b3['label'])
        nb3_v = c6.text_input("Valore Box 3", b3['value'])
        
        st.divider()
        st.write("### Motto Sotto il Titolo")
        new_motto = st.text_input("Modifica Motto", st.session_state.db['config'].get('motto'))
        
        if st.button("SALVA TUTTE LE MODIFICHE"):
            st.session_state.db['box1'] = {"label": nb1_l, "value": nb1_v}
            st.session_state.db['box2'] = {"label": nb2_l, "value": nb2_v}
            st.session_state.db['box3'] = {"label": nb3_l, "value": nb3_v}
            st.session_state.db['config']['motto'] = new_motto
            save_db(st.session_state.db)
            st.rerun()

else:
    # Altre pagine (S6, Accademia, Tech)
    key_map = {"⚔️ SEASON 6": "s6", "🎓 ACCADEMIA": "academy", "🤖 TECH": "drone"}
    k = key_map[page]
    st.title(page)
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    edit_p = st.toggle("EDIT")
    if edit_p:
        val_p = st.text_area("Update content", value=st.session_state.db.get(k, ""), height=400)
        if st.button("SALVA"):
            st.session_state.db[k] = val_p
            save_db(st.session_state.db)
            st.rerun()
    else:
        st.markdown(st.session_state.db.get(k))
    st.markdown("</div>", unsafe_allow_html=True)
