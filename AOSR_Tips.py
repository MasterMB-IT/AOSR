import streamlit as st
import pandas as pd
import json
import os

# --- STYLE INJECTION (DARK MILITARY) ---
st.set_page_config(page_title="LW: TOTAL COMMAND", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; border-top: 3px solid #f39c12; }
    .section-card { 
        padding: 25px; border-radius: 15px; border-left: 5px solid #f39c12; 
        background-color: #1c2128; margin-bottom: 20px; box-shadow: 5px 5px 15px rgba(0,0,0,0.3);
    }
    .stButton>button { width: 100%; background-color: #f39c12; color: black; font-weight: bold; }
    h1, h2, h3 { color: #f39c12 !important; }
    </style>
""", unsafe_allow_html=True)

# --- DATABASE ENGINE ---
DB_FILE = "alliance_full_control_db.json"

def get_defaults():
    return {
        "config": {
            "titolo_app": "LW: COMMAND CENTER S6",
            "server": "#000",
            "motto": "Per l'Alleanza!"
        },
        "stats": {
            "Membri": "100/100",
            "S1_Media": "25.0M",
            "Power_Rank": "#1"
        },
        "news": "### 🚩 DIRETTIVE PRE-SEASON 6\nInserire qui gli ordini per i ragazzi.",
        "s6_meta": "### ⚔️ TREND SEASON 6\nAnalisi eroi e formazioni.",
        "academy": "### 🎓 ACCADEMIA CADETTI\nLinee guida crescita.",
        "drone": "### 🤖 TECH DRONE\nFocus componenti."
    }

def load_db():
    defaults = get_defaults()
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
            # Ripristino chiavi mancanti
            for k, v in defaults.items():
                if k not in data: data[k] = v
            return data
        except:
            return defaults
    return defaults

def save():
    with open(DB_FILE, "w") as f:
        json.dump(st.session_state.db, f, indent=4)

if 'db' not in st.session_state:
    st.session_state.db = load_db()

# --- SIDEBAR ---
st.sidebar.title(f"🛡️ {st.session_state.db['config']['titolo_app']}")
st.sidebar.write(f"Server: {st.session_state.db['config']['server']}")
page = st.sidebar.selectbox("MENU TATTICO", ["📡 DASHBOARD", "⚔️ SEASON 6", "🎓 ACCADEMIA", "🤖 DRONE & GEAR"])

# --- FUNZIONE EDITABILE UNIVERSALE ---
def pro_section(key, title):
    st.markdown(f"<div class='section-card'>", unsafe_allow_html=True)
    col_t, col_e = st.columns([0.8, 0.2])
    with col_t: st.subheader(title)
    with col_e: edit = st.toggle("EDIT", key="t_"+key)
    
    content = st.session_state.db.get(key, "")
    if edit:
        new_val = st.text_area("Modifica Contenuto", value=content, height=250, key="a_"+key)
        if st.button("SALVA MODIFICHE", key="b_"+key):
            st.session_state.db[key] = new_val
            save()
            st.rerun()
    else:
        st.markdown(content)
    st.markdown("</div>", unsafe_allow_html=True)

# --- PAGINE ---
if page == "📡 DASHBOARD":
    st.title(f"📡 {st.session_state.db['config']['titolo_app']}")
    st.caption(f"Motto: {st.session_state.db['config']['motto']}")

    # --- PANNELLO DI CONTROLLO DASHBOARD ---
    with st.expander("🛠️ PANNELLO DI CONTROLLO DASHBOARD (Accesso Totale)"):
        st.subheader("1. Modifica Parametri App")
        c_app1, c_app2, c_app3 = st.columns(3)
        edit_titolo = c_app1.text_input("Nome App/Alleanza", st.session_state.db['config']['titolo_app'])
        edit_server = c_app2.text_input("Numero Server", st.session_state.db['config']['server'])
        edit_motto = c_app3.text_input("Motto", st.session_state.db['config']['motto'])
        
        st.subheader("2. Modifica Statistiche Real-Time")
        c_st1, c_st2, c_st3 = st.columns(3)
        edit_membri = c_st1.text_input("Membri", st.session_state.db['stats']['Membri'])
        edit_potenza = c_st2.text_input("Media S1", st.session_state.db['stats']['S1_Media'])
        edit_rank = c_st3.text_input("Rank Server", st.session_state.db['stats']['Power_Rank'])
        
        if st.button("💾 APPLICA MODIFICHE GLOBALI"):
            st.session_state.db['config'] = {"titolo_app": edit_titolo, "server": edit_server, "motto": edit_motto}
            st.session_state.db['stats'] = {"Membri": edit_membri, "S1_Media": edit_potenza, "Power_Rank": edit_rank}
            save()
            st.success("Configurazione aggiornata!")
            st.rerun()

    st.divider()

    # Visualizzazione Metriche
    stats = st.session_state.db['stats']
    c1, c2, c3 = st.columns(3)
    c1.metric("Membri Alleanza", stats['Membri'])
    c2.metric("Media Potenza S1", stats['S1_Media'])
    c3.metric("Rank Server", stats['Power_Rank'])
    
    st.divider()
    
    # Direttive di Guerra
    pro_section("news", "📢 DIRETTIVE DI GUERRA")

elif page == "⚔️ SEASON 6":
    st.title("❄️ Strategia Season 6")
    pro_section("s6_meta", "⚔️ Analisi Meta & Pre-Season")

elif page == "🎓 ACCADEMIA":
    st.title("🎓 Centro Addestramento")
    pro_section("academy", "📝 Programma Crescita Ragazzi")

elif page == "🤖 DRONE & GEAR":
    st.title("🛠️ Reparto Tecnico")
    pro_section("drone", "🤖 Configurazione Drone & Chip")
