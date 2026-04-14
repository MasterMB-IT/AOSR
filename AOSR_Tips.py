import streamlit as st
import json
import requests
import base64
import time

# --- CONFIGURAZIONE GITHUB ---
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO_NAME = st.secrets.get("REPO_NAME", "")
BRANCH = "main"
DB_FILE = "aosr_titan_db.json"

st.set_page_config(page_title="AOSR TITAN COMMAND", layout="wide", initial_sidebar_state="expanded")

# --- UI DESIGN (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@500;700&display=swap');
    .stApp { background: #05070a; font-family: 'Rajdhani', sans-serif; }
    .main-header {
        background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
        padding: 30px; border-radius: 15px; border: 2px solid #f39c12;
        text-align: center; margin-bottom: 25px;
    }
    .main-title {
        font-family: 'Orbitron', sans-serif; color: #f39c12;
        font-size: 45px; letter-spacing: 5px; text-shadow: 0 0 15px #f39c12;
    }
    .section-card {
        background: rgba(22, 27, 34, 0.7); padding: 25px; border-radius: 15px;
        border-left: 5px solid #f39c12; margin-bottom: 20px; border-top: 1px solid #30363d;
    }
    .rendered-markdown img {
        max-width: 100%; height: auto; border-radius: 10px; border: 1px solid #f39c12;
        margin-top: 10px; box-shadow: 0 0 10px rgba(243, 156, 18, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# --- ENGINE DI SICUREZZA (ANTI-CRASH) ---
def get_safe_defaults():
    return {
        "config": {"motto": "HONOR - STRENGTH - STRATEGY"},
        "boxes": [{"l": "MEMBRI", "v": "0"}, {"l": "POTENZA", "v": "0M"}, {"l": "RANK", "v": "#0"}],
        "news": "### 🚩 DIRETTIVE\nInserire ordini qui.",
        "meta": {"t1": "", "t2": "", "t3": ""},
        "tech": {"t1": "", "t2": "", "t3": ""},
        "decors": {"t1": "", "t2": "", "t3": ""},
        "routine": {"t1": "", "t2": "", "t3": ""}
    }

def load_db():
    try:
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{DB_FILE}?t={int(time.time())}"
        res = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
        if res.status_code == 200:
            data = json.loads(base64.b64decode(res.json()['content']).decode())
            # Verifica integrità: se mancano pezzi, aggiungili dai default
            defaults = get_safe_defaults()
            for key in defaults:
                if key not in data: data[key] = defaults[key]
            return data
    except Exception: pass
    return get_safe_defaults()

def save_db(data):
    try:
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{DB_FILE}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        r = requests.get(url, headers=headers)
        sha = r.json().get("sha") if r.status_code == 200 else None
        content = base64.b64encode(json.dumps(data, indent=4).encode()).decode()
        payload = {"message": "AOSR Titan Sync", "content": content, "sha": sha}
        res = requests.put(url, json=payload, headers=headers)
        if res.status_code in [200, 201]:
            st.success("✅ SINCRONIZZAZIONE COMPLETATA")
            time.sleep(1)
            st.rerun()
    except Exception as e:
        st.error(f"❌ ERRORE GITHUB: {e}")

if 'db' not in st.session_state:
    st.session_state.db = load_db()

# --- SIDEBAR: GESTIONE IMMAGINI ---
st.sidebar.title("🖼️ MEDIA MANAGER")
f = st.sidebar.file_uploader("Carica Screenshot", type=['png','jpg','jpeg'])
if f:
    if st.sidebar.button("🚀 GENERA LINK"):
        # Logica upload immagine
        path = f"img/{f.name.replace(' ', '_')}"
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{path}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        res_check = requests.get(url, headers=headers)
        sha = res_check.json().get("sha") if res_check.status_code == 200 else None
        img_content = base64.b64encode(f.getvalue()).decode()
        payload = {"message": "Upload Img", "content": img_content, "sha": sha}
        r = requests.put(url, json=payload, headers=headers)
        if r.status_code in [200, 201]:
            img_url = f"https://raw.githubusercontent.com/{REPO_NAME}/{BRANCH}/{path}"
            st.sidebar.code(f"![Titolo]({img_url})")
            st.sidebar.success("Copia il codice sopra!")

# --- MENU PRINCIPALE ---
menu = st.sidebar.radio("SISTEMI", ["📡 DASHBOARD", "⚔️ META", "🧬 TECH", "🏯 DECORAZIONI", "📋 ROUTINE"])

if menu == "📡 DASHBOARD":
    # Risoluzione Errore image_81004b.png: Verifica chiavi prima di stampare
    motto = st.session_state.db.get('config', {}).get('motto', "HONOR - STRENGTH")
    st.markdown(f"<div class='main-header'><div class='main-title'>AOSR SQUAD</div><div style='color:white;'>{motto}</div></div>", unsafe_allow_html=True)
    
    # Riquadri Statistiche
    boxes = st.session_state.db.get('boxes', get_safe_defaults()['boxes'])
    cols = st.columns(3)
    for i, b in enumerate(boxes):
        cols[i].metric(b.get('l', 'INFO'), b.get('v', '0'))

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    if st.toggle("MODIFICA DASHBOARD"):
        new_news = st.text_area("Ordini:", st.session_state.db.get('news', ""), height=200)
        # Modifica label statistiche
        for i in range(3):
            boxes[i]['l'] = st.text_input(f"Etichetta {i+1}", boxes[i].get('l', ''))
            boxes[i]['v'] = st.text_input(f"Valore {i+1}", boxes[i].get('v', ''))
        if st.button("💾 SALVA TUTTO"):
            st.session_state.db['news'] = new_news
            st.session_state.db['boxes'] = boxes
            save_db(st.session_state.db)
    else:
        st.markdown(st.session_state.db.get('news', ''))
    st.markdown("</div>", unsafe_allow_html=True)

else:
    # Gestione Sezioni con Immagini
    mapping = {"⚔️ META": "meta", "🧬 TECH": "tech", "🏯 DECORAZIONI": "decors", "📋 ROUTINE": "routine"}
    sec_key = mapping[menu]
    st.title(menu)
    
    tabs = st.tabs(["SEZIONE 1", "SEZIONE 2", "SEZIONE 3"])
    for i, tab in enumerate(tabs):
        with tab:
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            t_key = f"t{i+1}"
            content = st.session_state.db[sec_key].get(t_key, "")
            
            if st.toggle(f"MODIFICA {menu} {i+1}"):
                new_v = st.text_area("Testo + Immagini:", content, height=300, key=f"area_{sec_key}_{i}")
                if st.button("💾 SALVA", key=f"btn_{sec_key}_{i}"):
                    st.session_state.db[sec_key][t_key] = new_v
                    save_db(st.session_state.db)
            else:
                st.markdown(content)
            st.markdown("</div>", unsafe_allow_html=True)
