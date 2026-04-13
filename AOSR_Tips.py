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

# --- STYLE AOSR (IL LOOK ORIGINALE) ---
st.set_page_config(page_title="AOSR SQUAD: COMMAND CENTER", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .stMetric { 
        background-color: #161b22; 
        border: 1px solid #30363d; 
        padding: 15px; 
        border-radius: 10px; 
        border-top: 3px solid #f39c12; 
    }
    .section-card { 
        padding: 25px; 
        border-radius: 15px; 
        border-left: 5px solid #f39c12; 
        background-color: #1c2128; 
        margin-bottom: 20px; 
        box-shadow: 5px 5px 15px rgba(0,0,0,0.3);
    }
    .main-title { 
        color: #f39c12; 
        font-size: 45px; 
        font-weight: bold; 
        text-align: center; 
        text-transform: uppercase; 
        letter-spacing: 2px;
        margin-bottom: 5px;
    }
    .stButton>button { 
        width: 100%; 
        background-color: #f39c12; 
        color: black; 
        font-weight: bold; 
        border-radius: 5px;
    }
    h1, h2, h3 { color: #f39c12 !important; }
    p { color: #c9d1d9; }
    </style>
""", unsafe_allow_html=True)

# --- ENGINE DI CARICAMENTO E SALVATAGGIO (PROTEZIONE TOTALE) ---
def get_default_data():
    return {
        "config": {"titolo": "AOSR SQUAD", "server": "#XXX", "motto": "Elite Soldiers, Unstoppable Force."},
        "stats": {"Membri": "100/100", "S1_Media": "25.0M", "Power_Rank": "#1"},
        "news": "### 📢 BENVENUTI AOSR\nClicca su EDIT per inserire le direttive.",
        "s6_meta": "### ⚔️ SEASON 6\nStrategie in fase di elaborazione.",
        "academy": "### 🎓 ACCADEMIA\nParametri di crescita per i ragazzi.",
        "drone": "### 🤖 TECH DRONE\nFocus componenti."
    }

def load_db():
    if GITHUB_TOKEN and REPO_NAME:
        try:
            url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}?ref={BRANCH}"
            headers = {"Authorization": f"token {GITHUB_TOKEN}"}
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                content = base64.b64decode(res.json()['content']).decode('utf-8')
                data = json.loads(content)
                # Check chiavi mancanti per evitare KeyError
                default = get_default_data()
                for k in default:
                    if k not in data: data[k] = default[k]
                return data
        except: pass
    return get_default_data()

def save_db(data):
    if GITHUB_TOKEN and REPO_NAME:
        try:
            url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
            headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
            r = requests.get(url, headers=headers)
            sha = r.json().get("sha") if r.status_code == 200 else None
            content_b64 = base64.b64encode(json.dumps(data, indent=4).encode()).decode()
            payload = {"message": "AOSR Squad Update", "content": content_b64, "branch": BRANCH}
            if sha: payload["sha"] = sha
            requests.put(url, headers=headers, json=payload, timeout=10)
        except: st.error("Errore di sincronizzazione con GitHub.")

if 'db' not in st.session_state:
    st.session_state.db = load_db()

# --- SIDEBAR NAV ---
st.sidebar.markdown(f"<h2 style='text-align: center;'>🛡️ {st.session_state.db['config'].get('titolo')}</h2>", unsafe_allow_html=True)
page = st.sidebar.selectbox("MENU TATTICO", ["📡 DASHBOARD", "⚔️ SEASON 6", "🎓 ACCADEMIA", "🤖 DRONE & GEAR"])

# --- FUNZIONE RENDER SEZIONI ---
def render_section(key, title):
    st.markdown(f"<div class='section-card'>", unsafe_allow_html=True)
    col_t, col_e = st.columns([0.85, 0.15])
    with col_t: st.subheader(title)
    with col_e: edit = st.toggle("EDIT", key="t_"+key)
    
    content = st.session_state.db.get(key, "")
    if edit:
        new_val = st.text_area("Update:", value=content, height=250, key="a_"+key)
        if st.button("💾 SALVA", key="b_"+key):
            st.session_state.db[key] = new_val
            save_db(st.session_state.db)
            st.rerun()
    else:
        st.markdown(content)
    st.markdown("</div>", unsafe_allow_html=True)

# --- PAGINE ---
if page == "📡 DASHBOARD":
    st.markdown(f"<div class='main-title'>{st.session_state.db['config'].get('titolo')}</div>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #888;'>{st.session_state.db['config'].get('motto')}</p>", unsafe_allow_html=True)

    # Expander per modificare le stats (Membri, Potenza, Rank)
    with st.expander("⚙️ PANNELLO DI CONTROLLO STATISTICHE"):
        c_ed1, c_ed2, c_ed3 = st.columns(3)
        stats = st.session_state.db.get("stats", {})
        new_m = c_ed1.text_input("Membri", stats.get("Membri", "100"))
        new_p = c_ed2.text_input("Potenza S1", stats.get("S1_Media", "20M"))
        new_r = c_ed3.text_input("Rank Server", stats.get("Power_Rank", "#1"))
        if st.button("AGGIORNA NUMERI"):
            st.session_state.db["stats"] = {"Membri": new_m, "S1_Media": new_p, "Power_Rank": new_r}
            save_db(st.session_state.db)
            st.rerun()

    st.divider()
    
    # Metriche visive
    stats = st.session_state.db.get("stats", {})
    col1, col2, col3 = st.columns(3)
    col1.metric("Membri Alleanza", stats.get("Membri", "N/A"))
    col2.metric("Media Potenza S1", stats.get("S1_Media", "N/A"))
    col3.metric("Rank Server", stats.get("Power_Rank", "N/A"))
    
    st.divider()
    render_section("news", "📢 DIRETTIVE DI GUERRA")

elif page == "⚔️ SEASON 6":
    st.title("⚔️ Strategia Season 6")
    render_section("s6_meta", "🔥 Meta e Nuovi Eroi")

elif page == "🎓 ACCADEMIA":
    st.title("🎓 Centro Addestramento")
    render_section("academy", "📝 Crescita Ragazzi")

elif page == "🤖 DRONE & GEAR":
    st.title("🤖 Reparto Tecnico")
    render_section("drone", "🛠️ Drone & Equipaggiamento")
