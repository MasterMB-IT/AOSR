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

# --- DESIGN CYBER-MILITARY (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500;700&display=swap');
    
    .main { background: #05070a; font-family: 'Rajdhani', sans-serif; }

    /* Header e Titolo */
    .main-header {
        background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
        padding: 40px; border-radius: 20px; border: 2px solid #f39c12;
        text-align: center; margin-bottom: 30px;
        box-shadow: 0 0 40px rgba(243, 156, 18, 0.2);
    }
    .main-title {
        font-family: 'Orbitron', sans-serif; color: #f39c12;
        font-size: 60px; letter-spacing: 10px; text-shadow: 0 0 25px #f39c12;
        margin-bottom: 10px;
    }

    /* Cards Statistiche */
    .stMetric {
        background: rgba(22, 27, 34, 0.85) !important;
        border: 1px solid #f39c12 !important;
        border-radius: 15px !important;
        box-shadow: 0 0 15px rgba(243, 156, 18, 0.1);
        padding: 20px !important;
    }

    /* Tabs Stilizzati */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        height: 60px; background-color: #0d1117; border-radius: 10px 10px 0 0;
        color: #f39c12; border: 1px solid #30363d; font-family: 'Orbitron';
        transition: 0.3s;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #f39c12 !important; color: black !important;
        box-shadow: 0 0 20px rgba(243, 156, 18, 0.4);
    }

    /* Box Contenuto */
    .section-card {
        background: rgba(22, 27, 34, 0.6); backdrop-filter: blur(15px);
        padding: 35px; border-radius: 20px; border: 1px solid #30363d;
        border-left: 10px solid #f39c12; margin-top: 20px;
    }

    /* Anteprima Immagini */
    .img-preview { border: 2px dashed #f39c12; padding: 10px; border-radius: 10px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- LOGICA DATABASE ---
def get_default_data():
    return {
        "config": {"motto": "HONOR - STRENGTH - STRATEGY"},
        "boxes": [
            {"l": "MEMBRI", "v": "100/100"}, 
            {"l": "POTENZA S1", "v": "25.0M"}, 
            {"l": "RANK SERVER", "v": "#1"}
        ],
        "news": "### 📢 DIRETTIVE SUPREME\nBenvenuto al terminale AOSR.",
        "meta": {"t1": "### 🏆 TIER LIST", "t2": "### 🤝 SINERGIE", "t3": "### 🛡️ COUNTER"},
        "tech": {"t1": "### 🧪 RICERCHE", "t2": "### ⚙️ GEAR EROI", "t3": "### 🤖 DRONE"},
        "decors": {"t1": "### 🎨 SKIN", "t2": "### 🏯 STATUE", "t3": "### 📊 UPGRADES"},
        "routine": {"t1": "### 🌅 START DAY", "t2": "### 📅 EVENTI", "t3": "### 🔄 RESET"}
    }

def load_db():
    try:
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}?t={int(time.time())}"
        res = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
        if res.status_code == 200:
            data = json.loads(base64.b64decode(res.json()['content']).decode())
            # Fix per migrazione chiavi (evita KeyError boxes)
            if 'boxes' not in data: data['boxes'] = get_default_data()['boxes']
            return data
    except: pass
    return get_default_data()

def save_db(data):
    with st.spinner("💾 Sincronizzazione in corso..."):
        try:
            url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
            headers = {"Authorization": f"token {GITHUB_TOKEN}"}
            r = requests.get(url, headers=headers)
            sha = r.json().get("sha") if r.status_code == 200 else None
            content = base64.b64encode(json.dumps(data, indent=4).encode()).decode()
            payload = {"message": "AOSR Overlord Sync", "content": content, "sha": sha}
            requests.put(url, json=payload, headers=headers)
            st.success("🛰️ COMANDO INVIATO CON SUCCESSO!")
            time.sleep(1)
            st.rerun()
    except: st.error("❌ ERRORE DI COMUNICAZIONE")

if 'db' not in st.session_state:
    st.session_state.db = load_db()

# --- SIDEBAR ---
st.sidebar.markdown("<h1 style='color:#f39c12; font-family:Orbitron; text-align:center;'>AOSR OVERLORD</h1>", unsafe_allow_html=True)
menu = st.sidebar.radio("SISTEMI ATTIVI", ["📡 DASHBOARD", "⚔️ META & SQUAD", "🧬 TECH & GEAR", "🏯 DECORAZIONI", "📋 ROUTINE"])

# --- TOOL ANTEPRIMA IMMAGINI ---
def image_uploader_tool(key_suffix):
    with st.expander("🖼️ CARICATORE IMMAGINI ISTANTANEO"):
        st.info("Incolla qui l'URL dell'immagine (Imgur) per vederla subito.")
        img_url = st.text_input("URL Immagine:", key=f"url_{key_suffix}", placeholder="https://i.imgur.com/...")
        if img_url:
            st.markdown("<div class='img-preview'>", unsafe_allow_html=True)
            st.image(img_url, caption="Anteprima Immagine", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            st.code(f"![Immagine]({img_url})", language="markdown")
            st.caption("Copia il codice sopra e incollalo nel testo della sezione.")

# --- PAGINE ---
if menu == "📡 DASHBOARD":
    st.markdown(f"""<div class='main-header'>
        <div class='main-title'>AOSR SQUAD</div>
        <div style='color:#8b949e; letter-spacing:5px;'>{st.session_state.db['config']['motto']}</div>
    </div>""", unsafe_allow_html=True)
    
    # Riquadri superiori
    cols = st.columns(3)
    for i, b in enumerate(st.session_state.db['boxes']):
        cols[i].metric(b['l'], b['v'])

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    c1, c2 = st.columns([0.8, 0.2])
    c1.subheader("📢 ORDINI DEL GIORNO")
    if c2.toggle("EDIT"):
        new_news = st.text_area("Update:", st.session_state.db['news'], height=200)
        # Modifica riquadri
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

else:
    page_map = {
        "⚔️ META & SQUAD": ("meta", ["🏆 TIER LIST", "🤝 SINERGIE", "🛡️ COUNTER"]),
        "🧬 TECH & GEAR": ("tech", ["🧪 RICERCHE", "⚙️ GEAR EROI", "🤖 DRONE"]),
        "🏯 DECORAZIONI": ("decors", ["🎨 SKIN & SET", "💎 STATUE", "📊 INVESTIMENTI"]),
        "📋 ROUTINE": ("routine", ["🌅 START DAY", "📅 EVENTI", "🔄 RESET"])
    }
    key, labels = page_map[menu]
    st.title(menu)
    
    # Tool caricamento immagini sempre visibile in cima alle sezioni
    image_uploader_tool(menu)
    
    tabs = st.tabs(labels)
    for i, t in enumerate(tabs):
        with t:
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            t_key = f"t{i+1}"
            edit = st.toggle("MODIFICA", key=f"ed_{menu}_{i}")
            if edit:
                new_v = st.text_area("Inserisci testo e codice immagine:", st.session_state.db[key].get(t_key, ""), height=400, key=f"ta_{menu}_{i}")
                if st.button("💾 CONFERMA MODIFICHE", key=f"btn_{menu}_{i}"):
                    st.session_state.db[key][t_key] = new_v
                    save_db(st.session_state.db)
            else:
                st.markdown(st.session_state.db[key].get(t_key, "Nessun dato."))
            st.markdown("</div>", unsafe_allow_html=True)
