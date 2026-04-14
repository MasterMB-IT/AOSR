import streamlit as st
import json
import requests
import base64
import time

# --- CONFIGURAZIONE GITHUB ---
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO_NAME = st.secrets.get("REPO_NAME", "")
FILE_PATH = "aosr_squad_db.json"
BRANCH = "main"

st.set_page_config(page_title="AOSR OVERLORD TERMINAL", layout="wide", initial_sidebar_state="expanded")

# --- DESIGN ESTREMO (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500;700&display=swap');
    
    .main { background: #05070a; }
    font-family: 'Rajdhani', sans-serif;

    /* Header e Titoli */
    .main-header {
        background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
        padding: 30px; border-radius: 15px; border: 1px solid #f39c12;
        text-align: center; margin-bottom: 30px;
        box-shadow: 0 0 30px rgba(243, 156, 18, 0.15);
    }
    .main-title {
        font-family: 'Orbitron', sans-serif; color: #f39c12;
        font-size: 55px; letter-spacing: 8px; text-shadow: 0 0 20px #f39c12;
    }

    /* Cards e Tabs */
    .section-card {
        background: rgba(22, 27, 34, 0.7); backdrop-filter: blur(10px);
        padding: 25px; border-radius: 15px; border: 1px solid #30363d;
        margin-bottom: 20px; border-left: 5px solid #f39c12;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 15px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: #0d1117; border-radius: 8px 8px 0 0;
        color: #8b949e; border: 1px solid #30363d; font-family: 'Orbitron';
    }
    .stTabs [aria-selected="true"] { 
        background-color: #f39c12 !important; color: black !important; font-weight: bold;
    }

    /* Bottoni */
    .stButton>button {
        width: 100%; border: none; padding: 15px;
        background: linear-gradient(90deg, #f39c12, #e67e22);
        color: black; font-family: 'Orbitron'; font-weight: 700;
        border-radius: 5px; cursor: pointer; transition: 0.3s;
    }
    .stButton>button:hover { box-shadow: 0 0 20px #f39c12; transform: scale(1.02); }
    </style>
""", unsafe_allow_html=True)

# --- DATABASE ENGINE ---
def get_default_data():
    return {
        "config": {"motto": "VICTORY THROUGH SCIENCE"},
        "boxes": [{"l": "MEMBRI", "v": "100/100"}, {"l": "POTENZA S1", "v": "25M"}, {"l": "RANK", "v": "#1"}],
        "news": "### 🚩 DIRETTIVE HQ\nInserire ordini qui.",
        "meta": {"t1": "Tier List", "t2": "Sinergie", "t3": "Counter"},
        "tech": {"t1": "Ricerche", "t2": "Gear", "t3": "Drone"},
        "decors": {"t1": "Skin", "t2": "Statue", "t3": "Budget"},
        "routine": {"t1": "Mattina", "t2": "Eventi", "t3": "Reset"}
    }

def load_db():
    try:
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}?t={int(time.time())}"
        res = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
        if res.status_code == 200:
            return json.loads(base64.b64decode(res.json()['content']).decode())
    except: pass
    return get_default_data()

def save_db(data):
    try:
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        r = requests.get(url, headers=headers)
        sha = r.json().get("sha") if r.status_code == 200 else None
        content = base64.b64encode(json.dumps(data, indent=4).encode()).decode()
        payload = {"message": "AOSR Update", "content": content, "sha": sha}
        requests.put(url, json=payload, headers=headers)
        st.success("✅ SINCRONIZZAZIONE COMPLETATA")
        time.sleep(1)
        st.rerun()
    except: st.error("Errore di rete")

if 'db' not in st.session_state:
    st.session_state.db = load_db()

# --- SIDEBAR ---
st.sidebar.markdown("<h1 style='color:#f39c12; font-family:Orbitron;'>AOSR HQ</h1>", unsafe_allow_html=True)
menu = st.sidebar.radio("SISTEMI ATTIVI", ["📡 DASHBOARD", "⚔️ META & SQUAD", "🧬 TECH & GEAR", "🏯 DECORAZIONI", "📋 ROUTINE"])

# --- TOOL: ANTEPRIMA IMMAGINE ISTANTANEA ---
def image_preview_tool():
    with st.expander("🖼️ TOOL CARICAMENTO IMMAGINI (Anteprima Rapida)"):
        st.write("Copia il link di Imgur qui sotto per vedere se funziona prima di salvarlo:")
        test_url = st.text_input("Incolla URL immagine (.png o .jpg):", placeholder="https://i.imgur.com/...")
        if test_url:
            st.image(test_url, caption="Anteprima", use_container_width=True)
            st.code(f"![Titolo]({test_url})", language="markdown")
            st.caption("Copia il codice sopra e incollalo nell'area di testo per usarlo.")

# --- PAGINA: DASHBOARD ---
if menu == "📡 DASHBOARD":
    st.markdown(f"<div class='main-header'><div class='main-title'>AOSR SQUAD</div><div style='color:white;'>{st.session_state.db['config']['motto']}</div></div>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    for i, b in enumerate(st.session_state.db['boxes']):
        cols[i].metric(b['l'], b['v'])

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    c1, c2 = st.columns([0.8, 0.2])
    c1.subheader("📢 DIRETTIVE DI GUERRA")
    if c2.toggle("EDIT"):
        new_news = st.text_area("Update:", st.session_state.db['news'], height=200)
        if st.button("PUBBLICA"):
            st.session_state.db['news'] = new_news
            save_db(st.session_state.db)
    else:
        st.markdown(st.session_state.db['news'])
    st.markdown("</div>", unsafe_allow_html=True)

# --- PAGINA: META / TECH / DECORS / ROUTINE (LOGICA UNIFICATA) ---
else:
    page_map = {
        "⚔️ META & SQUAD": ("meta", ["🏆 Tier List", "🤝 Sinergie", "🛡️ Counter"]),
        "🧬 TECH & GEAR": ("tech", ["🧪 Ricerche", "⚙️ Gear Eroi", "🤖 Drone"]),
        "🏯 DECORAZIONI": ("decors", ["🎨 Skin & Set", "💎 Statue", "📊 Investimenti"]),
        "📋 ROUTINE": ("routine", ["🌅 Start Day", "📅 Eventi", "🔄 Reset"])
    }
    
    key, tabs_labels = page_map[menu]
    st.title(menu)
    image_preview_tool()
    
    tabs = st.tabs(tabs_labels)
    for i, t in enumerate(tabs):
        with t:
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            t_key = f"t{i+1}"
            edit = st.toggle("EDIT", key=f"ed_{menu}_{i}")
            if edit:
                new_v = st.text_area("Testo & Immagini:", st.session_state.db[key].get(t_key, ""), height=400, key=f"ta_{menu}_{i}")
                if st.button("SALVA SCHEDA", key=f"btn_{menu}_{i}"):
                    st.session_state.db[key][t_key] = new_v
                    save_db(st.session_state.db)
            else:
                st.markdown(st.session_state.db[key].get(t_key, "Nessun dato."))
            st.markdown("</div>", unsafe_allow_html=True)
