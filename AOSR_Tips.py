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

# --- UI APPARISCENTE (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@500;700&display=swap');
    
    .main { background: #05070a; font-family: 'Rajdhani', sans-serif; }
    
    .main-header {
        background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
        padding: 40px; border-radius: 20px; border: 2px solid #f39c12;
        text-align: center; margin-bottom: 30px;
        box-shadow: 0 0 40px rgba(243, 156, 18, 0.2);
    }
    .main-title {
        font-family: 'Orbitron', sans-serif; color: #f39c12;
        font-size: 55px; letter-spacing: 10px; text-shadow: 0 0 25px #f39c12;
        margin-bottom: 10px;
    }

    /* Cards e Tabs */
    .stMetric { background: rgba(22, 27, 34, 0.85) !important; border: 1px solid #f39c12 !important; border-radius: 15px !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 15px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: #0d1117; border-radius: 8px 8px 0 0;
        color: #f39c12; border: 1px solid #30363d; font-family: 'Orbitron';
    }
    .stTabs [aria-selected="true"] { 
        background-color: #f39c12 !important; color: black !important; font-weight: bold;
    }

    /* Box Contenuto (per immagini) */
    .section-card {
        background: rgba(22, 27, 34, 0.6); backdrop-filter: blur(15px);
        padding: 30px; border-radius: 20px; border: 1px solid #30363d;
        border-left: 10px solid #f39c12; margin-top: 20px;
    }
    /* Stile per le immagini renderizzate in Markdown */
    .rendered-markdown img {
        max-width: 100%; height: auto; border-radius: 10px; 
        border: 2px solid #f39c12; box-shadow: 0 0 15px #f39c12;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATABASE ENGINE ---
def get_default_data():
    return {
        "config": {"motto": "HONOR - STRENGTH - STRATEGY"},
        "boxes": [{"l": "MEMBRI", "v": "100/100"}, {"l": "POTENZA S1", "v": "0M"}, {"l": "RANK", "v": "#0"}],
        "news": "### 🚩 DIRETTIVE SUPREME\nInserire ordini qui.",
        "meta": {"t1": "### 🏆 TIER LIST", "t2": "### 🤝 SINERGIE", "t3": "### 🛡️ COUNTER"},
        "tech": {"t1": "### 🧪 RICERCHE", "t2": "### ⚙️ GEAR EROI", "t3": "### 🤖 DRONE"},
        "decors": {"t1": "### 🎨 SKIN & SET", "t2": "### 🏯 STATUE", "t3": "### 📊 UPGRADES"},
        "routine": {"t1": "### 🌅 START DAY", "t2": "### 📅 EVENTI", "t3": "### 🔄 RESET"}
    }

def load_db():
    try:
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{DB_FILE}?t={int(time.time())}"
        res = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
        if res.status_code == 200:
            return json.loads(base64.b64decode(res.json()['content']).decode())
    except: pass
    return get_default_data()

def save_db(data):
    with st.spinner("💾 Sincronizzazione in corso..."):
        try:
            url = f"https://api.github.com/repos/{REPO_NAME}/contents/{DB_FILE}"
            headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
            r = requests.get(url, headers=headers)
            sha = r.json().get("sha") if r.status_code == 200 else None
            content = base64.b64encode(json.dumps(data, indent=4).encode()).decode()
            payload = {"message": "AOSR Overlord Titan Update", "content": content, "sha": sha}
            requests.put(url, json=payload, headers=headers)
            st.success("✅ DATI SALVATI SUL CLOUD")
            time.sleep(1)
            st.rerun()
        except: st.error("Errore di sincronizzazione")

if 'db' not in st.session_state:
    st.session_state.db = load_db()

# --- SIDEBAR ---
st.sidebar.markdown("<h1 style='color:#f39c12; font-family:Orbitron; text-align:center;'>AOSR COMMAND</h1>", unsafe_allow_html=True)
menu = st.sidebar.radio("SISTEMI ATTIVI", ["📡 DASHBOARD", "⚔️ META & SQUAD", "🧬 TECH & GEAR", "🏯 DECORAZIONI", "📋 ROUTINE"])

# --- TOOL ANTEPRIMA ---
with st.expander("🖼️ TOOL CARICAMENTO IMMAGINI (Anteprima)"):
    st.write("Copia il link di Imgur qui sotto per vedere se funziona:")
    test_url = st.text_input("URL Immagine (Imgur):", placeholder="https://i.imgur.com/...")
    if test_url:
        st.image(test_url, caption="Anteprima", use_container_width=True)
        st.code(f"![Immagine]({test_url})", language="markdown")

# --- PAGINE ---
if menu == "📡 DASHBOARD":
    st.markdown(f"<div class='main-header'><div class='main-title'>AOSR SQUAD</div><div style='color:white;'>{st.session_state.db['config']['motto']}</div></div>", unsafe_allow_html=True)
    
    # Riquadri superiori
    cols = st.columns(3)
    for i, b in enumerate(st.session_state.db['boxes']):
        cols[i].metric(b['l'], b['v'])

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    c1, c2 = st.columns([0.8, 0.2])
    c1.subheader("📢 DIRETTIVE DI GUERRA")
    if c2.toggle("EDIT"):
        new_news = st.text_area("Update:", st.session_state.db['news'], height=200)
        
        # Modifica riquadri
        st.divider()
        st.write("### Modifica Statistiche")
        for i in range(3):
            st.session_state.db['boxes'][i]['l'] = st.text_input(f"Etichetta Box {i+1}", st.session_state.db['boxes'][i]['l'])
            st.session_state.db['boxes'][i]['v'] = st.text_input(f"Valore Box {i+1}", st.session_state.db['boxes'][i]['v'])
        
        if st.button("💾 SALVA DASHBOARD"):
            st.session_state.db['news'] = new_news
            save_db(st.session_state.db)
    else:
        st.markdown(st.session_state.db['news'])
    st.markdown("</div>", unsafe_allow_html=True)

# --- PAGINE MODULARI CON SUPPORTO IMMAGINI ---
else:
    page_map = {
        "⚔️ META & SQUAD": ("meta", ["🏆 TIER LIST", "🤝 SINERGIE", "🛡️ COUNTER"]),
        "🧬 TECH & GEAR": ("tech", ["🧪 RICERCHE", "⚙️ GEAR EROI", "🤖 DRONE"]),
        "🏯 DECORAZIONI": ("decors", ["🎨 SKIN & SET", "💎 STATUE", "📊 UPGRADES"]),
        "📋 ROUTINE": ("routine", ["🌅 START DAY", "📅 EVENTI", "🔄 RESET"])
    }
    
    key, labels = page_map[menu]
    st.title(menu)
    
    tabs = st.tabs(labels)
    for i, t in enumerate(tabs):
        with t:
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            
            # Recuperiamo il testo Markdown salvato
            t_key = f"t{i+1}"
            content = st.session_state.db[key].get(t_key, "")
            
            c_ed, c_v = st.columns([0.2, 0.8])
            with c_ed: edit = st.toggle("EDIT", key=f"ed_{menu}_{i}")
            
            if edit:
                # Sezione di editing
                new_v = st.text_area("Incolla qui il codice dell'immagine (![Img](url)):", value=content, height=400, key=f"ta_{menu}_{i}")
                if st.button("💾 SALVA SCHEDA", key=f"btn_{menu}_{i}"):
                    st.session_state.db[key][t_key] = new_v
                    save_db(st.session_state.db)
            else:
                # Sezione di visualizzazione (con supporto immagini)
                st.markdown(f"<div class='rendered-markdown'>", unsafe_allow_html=True)
                st.markdown(content)
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
