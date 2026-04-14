import streamlit as st
import json
import requests
import base64
import time

# --- CONFIGURAZIONE GITHUB ---
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO_NAME = st.secrets.get("REPO_NAME", "")
BRANCH = "main"
DB_FILE = "aosr_squad_db.json"

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="AOSR COMMAND CENTER", layout="wide", initial_sidebar_state="expanded")

# --- UI MILITARY-TECH (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500;700&display=swap');
    
    .main { background: #05070a; font-family: 'Rajdhani', sans-serif; }
    
    .main-header {
        background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
        padding: 40px; border-radius: 20px; border: 2px solid #f39c12;
        text-align: center; margin-bottom: 30px; box-shadow: 0 0 40px rgba(243, 156, 18, 0.2);
    }
    .main-title {
        font-family: 'Orbitron', sans-serif; color: #f39c12;
        font-size: clamp(30px, 5vw, 60px); letter-spacing: 10px; text-shadow: 0 0 25px #f39c12;
        margin-bottom: 10px;
    }
    .stMetric {
        background: rgba(22, 27, 34, 0.85) !important;
        border: 1px solid #f39c12 !important; border-radius: 15px !important;
        padding: 20px !important; box-shadow: 0 0 15px rgba(243, 156, 18, 0.1);
    }
    .section-card {
        background: rgba(22, 27, 34, 0.6); backdrop-filter: blur(15px);
        padding: 30px; border-radius: 20px; border: 1px solid #30363d;
        border-left: 10px solid #f39c12; margin-top: 20px;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: #0d1117; border-radius: 8px 8px 0 0;
        color: #f39c12; border: 1px solid #30363d; font-family: 'Orbitron';
    }
    .stTabs [aria-selected="true"] { 
        background-color: #f39c12 !important; color: black !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- CORE FUNCTIONS (GITHUB & DB) ---
def load_db():
    try:
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{DB_FILE}?t={int(time.time())}"
        res = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
        if res.status_code == 200:
            data = json.loads(base64.b64decode(res.json()['content']).decode())
            # Assicurati che le chiavi esistano per evitare KeyError
            default = get_default_data()
            for k in default:
                if k not in data: data[k] = default[k]
            return data
    except: pass
    return get_default_data()

def save_db(data):
    try:
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{DB_FILE}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        r = requests.get(url, headers=headers)
        sha = r.json().get("sha") if r.status_code == 200 else None
        content = base64.b64encode(json.dumps(data, indent=4).encode()).decode()
        payload = {"message": "AOSR Overlord Sync", "content": content, "sha": sha}
        requests.put(url, json=payload, headers=headers)
        st.success("🛰️ SISTEMA AGGIORNATO")
        time.sleep(1)
        st.rerun()
    except Exception as e:
        st.error(f"Errore: {e}")

def upload_image(uploaded_file):
    """Carica il file fisico su GitHub nella cartella img/"""
    file_path = f"img/{uploaded_file.name.replace(' ', '_')}"
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{file_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    res = requests.get(url, headers=headers)
    sha = res.json().get("sha") if res.status_code == 200 else None
    
    base64_content = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
    payload = {"message": "Upload Img", "content": base64_content, "branch": BRANCH}
    if sha: payload["sha"] = sha

    r = requests.put(url, json=payload, headers=headers)
    if r.status_code in [200, 201]:
        return f"https://raw.githubusercontent.com/{REPO_NAME}/{BRANCH}/{file_path}"
    return None

def get_default_data():
    return {
        "config": {"motto": "HONOR - STRENGTH - STRATEGY"},
        "boxes": [{"l": "MEMBRI", "v": "100/100"}, {"l": "POTENZA S1", "v": "0M"}, {"l": "RANK", "v": "#0"}],
        "news": "### 🚩 DIRETTIVE HQ\nInserire ordini qui.",
        "meta": {"t1": "Tier List", "t2": "Sinergie", "t3": "Counter"},
        "tech": {"t1": "Ricerche", "t2": "Gear Eroi", "t3": "Drone"},
        "decors": {"t1": "Skin & Set", "t2": "Statue", "t3": "Investimenti"},
        "routine": {"t1": "Checklist", "t2": "Eventi", "t3": "Reset"}
    }

# --- INITIALIZATION ---
if 'db' not in st.session_state:
    st.session_state.db = load_db()

# --- SIDEBAR ---
st.sidebar.markdown("<h1 style='color:#f39c12; font-family:Orbitron; text-align:center;'>AOSR HQ</h1>", unsafe_allow_html=True)
menu = st.sidebar.radio("SISTEMI ATTIVI", ["📡 DASHBOARD", "⚔️ META & SQUAD", "🧬 TECH & GEAR", "🏯 DECORAZIONI", "📋 ROUTINE"])

# --- TOOL CARICAMENTO FILE (COMUNE) ---
def file_upload_ui():
    with st.expander("📤 CARICAMENTO SCREENSHOT DI GIOCO"):
        f = st.file_uploader("Seleziona immagine", type=['png', 'jpg', 'jpeg'])
        if f:
            st.image(f, width=200)
            if st.button("🚀 CARICA SU GITHUB"):
                link = upload_image(f)
                if link:
                    st.success("Caricato!")
                    st.code(f"![Immagine]({link})")
                    st.caption("Copia il codice sopra e incollalo nell'editor qui sotto.")

# --- PAGINA: DASHBOARD ---
if menu == "📡 DASHBOARD":
    st.markdown(f"""<div class='main-header'>
        <div class='main-title'>AOSR SQUAD</div>
        <div style='color:white; letter-spacing:5px;'>{st.session_state.db['config']['motto']}</div>
    </div>""", unsafe_allow_html=True)
    
    cols = st.columns(3)
    for i, b in enumerate(st.session_state.db['boxes']):
        cols[i].metric(b['l'], b['v'])

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    c1, c2 = st.columns([0.8, 0.2])
    c1.subheader("📢 DIRETTIVE DI GUERRA")
    if c2.toggle("MODIFICA"):
        new_news = st.text_area("News:", st.session_state.db['news'], height=200)
        st.divider()
        st.write("### Modifica Box Superiori")
        for i in range(3):
            st.session_state.db['boxes'][i]['l'] = st.text_input(f"Etichetta Box {i+1}", st.session_state.db['boxes'][i]['l'])
            st.session_state.db['boxes'][i]['v'] = st.text_input(f"Valore Box {i+1}", st.session_state.db['boxes'][i]['v'])
        if st.button("💾 SALVA DASHBOARD"):
            st.session_state.db['news'] = new_news
            save_db(st.session_state.db)
    else:
        st.markdown(st.session_state.db['news'])
    st.markdown("</div>", unsafe_allow_html=True)

# --- PAGINE MODULARI ---
else:
    page_map = {
        "⚔️ META & SQUAD": ("meta", ["🏆 TIER LIST", "🤝 SINERGIE", "🛡️ COUNTER"]),
        "🧬 TECH & GEAR": ("tech", ["🧪 RICERCHE", "⚙️ GEAR EROI", "🤖 DRONE"]),
        "🏯 DECORAZIONI": ("decors", ["🎨 SKIN & SET", "💎 STATUE", "📊 INVESTIMENTI"]),
        "📋 ROUTINE": ("routine", ["🌅 START DAY", "📅 EVENTI", "🔄 RESET"])
    }
    key, labels = page_map[menu]
    st.title(menu)
    file_upload_ui()
    
    tabs = st.tabs(labels)
    for i, t in enumerate(tabs):
        with t:
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            t_key = f"t{i+1}"
            edit = st.toggle("EDIT", key=f"ed_{menu}_{i}")
            if edit:
                new_v = st.text_area("Testo/Codice Immagine:", st.session_state.db[key].get(t_key, ""), height=400, key=f"ta_{menu}_{i}")
                if st.button("💾 SALVA", key=f"btn_{menu}_{i}"):
                    st.session_state.db[key][t_key] = new_v
                    save_db(st.session_state.db)
            else:
                st.markdown(st.session_state.db[key].get(t_key, "Nessun dato."))
            st.markdown("</div>", unsafe_allow_html=True)
