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

# --- UI APPARISCENTE (CSS) ---
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
        font-size: 50px; letter-spacing: 10px; text-shadow: 0 0 25px #f39c12;
    }
    .stMetric {
        background: rgba(22, 27, 34, 0.85) !important;
        border: 1px solid #f39c12 !important; border-radius: 15px !important;
    }
    .section-card {
        background: rgba(22, 27, 34, 0.6); backdrop-filter: blur(15px);
        padding: 30px; border-radius: 20px; border-left: 10px solid #f39c12;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATABASE ENGINE ---
def get_default_data():
    return {
        "config": {"motto": "HONOR - STRENGTH - STRATEGY"},
        "boxes": [{"l": "MEMBRI", "v": "100/100"}, {"l": "POTENZA S1", "v": "0M"}, {"l": "RANK", "v": "#0"}],
        "news": "### 🚩 DIRETTIVE HQ\nInserire ordini qui.",
        "meta": {"t1": "Tier List", "t2": "Sinergie", "t3": "Counter"},
        "tech": {"t1": "Ricerche", "t2": "Gear Eroi", "t3": "Drone"},
        "decors": {"t1": "Skin & Set", "t2": "Statue", "t3": "Investimenti"},
        "routine": {"t1": "Checklist Mattina", "t2": "Eventi", "t3": "Ottimizzazione"}
    }

def load_db():
    try:
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}?t={int(time.time())}"
        res = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
        if res.status_code == 200:
            content = base64.b64decode(res.json()['content']).decode('utf-8')
            return json.loads(content)
    except Exception:
        pass
    return get_default_data()

def save_db(data):
    with st.spinner("🛰️ SINCRONIZZAZIONE..."):
        try:
            url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
            headers = {"Authorization": f"token {GITHUB_TOKEN}"}
            r = requests.get(url, headers=headers)
            sha = r.json().get("sha") if r.status_code == 200 else None
            content = base64.b64encode(json.dumps(data, indent=4).encode()).decode()
            payload = {"message": "AOSR Overlord Update", "content": content, "sha": sha}
            res = requests.put(url, json=payload, headers=headers)
            if res.status_code in [200, 201]:
                st.success("✅ COMANDO RICEVUTO")
                time.sleep(1)
                st.rerun()
        except Exception as e:
            st.error(f"❌ ERRORE CRITICO: {e}")

if 'db' not in st.session_state:
    st.session_state.db = load_db()

# --- SIDEBAR ---
st.sidebar.markdown("<h2 style='color:#f39c12; font-family:Orbitron;'>AOSR COMMAND</h2>", unsafe_allow_html=True)
menu = st.sidebar.radio("SISTEMI ATTIVI", ["📡 DASHBOARD", "⚔️ META & SQUAD", "🧬 TECH & GEAR", "🏯 DECORAZIONI", "📋 ROUTINE"])

# --- TOOL ANTEPRIMA ---
def image_tool():
    with st.expander("🖼️ TOOL CARICAMENTO IMMAGINI"):
        url = st.text_input("Incolla link Imgur/URL immagine:", placeholder="https://i.imgur.com/...")
        if url:
            st.image(url, use_container_width=True)
            st.code(f"![Titolo]({url})")

# --- RENDER PAGINE ---
if menu == "📡 DASHBOARD":
    st.markdown(f"<div class='main-header'><div class='main-title'>AOSR SQUAD</div><div style='color:white;'>{st.session_state.db['config']['motto']}</div></div>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    # Fix per evitare KeyError se boxes non esiste nel DB caricato
    boxes = st.session_state.db.get('boxes', get_default_data()['boxes'])
    for i, b in enumerate(boxes):
        cols[i].metric(b['l'], b['v'])

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    c1, c2 = st.columns([0.8, 0.2])
    c1.subheader("📢 DIRETTIVE SUPREME")
    if c2.toggle("MODIFICA"):
        new_news = st.text_area("Update News:", st.session_state.db.get('news', ""), height=200)
        st.divider()
        st.write("### Modifica Statistiche")
        for i in range(3):
            boxes[i]['l'] = st.text_input(f"Label {i+1}", boxes[i]['l'], key=f"l{i}")
            boxes[i]['v'] = st.text_input(f"Valore {i+1}", boxes[i]['v'], key=f"v{i}")
        if st.button("💾 SALVA DASHBOARD"):
            st.session_state.db['news'] = new_news
            st.session_state.db['boxes'] = boxes
            save_db(st.session_state.db)
    else:
        st.markdown(st.session_state.db.get('news', 'Nessun ordine.'))
    st.markdown("</div>", unsafe_allow_html=True)

else:
    page_map = {
        "⚔️ META & SQUAD": ("meta", ["🏆 Tier List", "🤝 Sinergie", "🛡️ Counter"]),
        "🧬 TECH & GEAR": ("tech", ["🧪 Ricerche", "⚙️ Gear Eroi", "🤖 Drone"]),
        "🏯 DECORAZIONI": ("decors", ["🎨 Skin & Set", "🏯 Statue", "📊 Upgrade"]),
        "📋 ROUTINE": ("routine", ["🌅 Start Day", "📅 Eventi", "🔄 Reset"])
    }
    key, labels = page_map[menu]
    st.title(menu)
    image_tool()
    
    tabs = st.tabs(labels)
    for i, t in enumerate(tabs):
        with t:
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            t_key = f"t{i+1}"
            content = st.session_state.db.get(key, {}).get(t_key, "Vuoto.")
            if st.toggle("EDIT", key=f"ed_{menu}_{i}"):
                new_v = st.text_area("Contenuto (Markdown + Immagini):", content, height=400, key=f"ta_{menu}_{i}")
                if st.button("💾 SALVA", key=f"b_{menu}_{i}"):
                    if key not in st.session_state.db: st.session_state.db[key] = {}
                    st.session_state.db[key][t_key] = new_v
                    save_db(st.session_state.db)
            else:
                st.markdown(content)
            st.markdown("</div>", unsafe_allow_html=True)
