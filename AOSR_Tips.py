import streamlit as st
import pandas as pd
import json
import os

# --- STYLE INJECTION (DARK MILITARY AOSR STYLE) ---
st.set_page_config(page_title="AOSR SQUAD: COMMAND CENTER", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; border-top: 3px solid #f39c12; }
    .section-card { 
        padding: 25px; border-radius: 15px; border-left: 5px solid #f39c12; 
        background-color: #1c2128; margin-bottom: 20px; box-shadow: 5px 5px 15px rgba(0,0,0,0.3);
    }
    .main-title {
        color: #f39c12; font-size: 50px; font-weight: bold; text-align: center;
        text-transform: uppercase; letter-spacing: 2px; text-shadow: 2px 2px 10px rgba(243, 156, 18, 0.5);
        margin-bottom: 10px;
    }
    .stButton>button { width: 100%; background-color: #f39c12; color: black; font-weight: bold; border-radius: 5px; }
    h1, h2, h3 { color: #f39c12 !important; }
    </style>
""", unsafe_allow_html=True)

# --- DATABASE ENGINE ---
DB_FILE = "aosr_squad_db.json"

def get_defaults():
    return {
        "config": {
            "titolo_display": "AOSR SQUAD",
            "server": "#XXX",
            "motto": "Elite Soldiers, Unstoppable Force."
        },
        "stats": {
            "Membri": "100/100",
            "S1_Media": "25.0M",
            "Power_Rank": "#1"
        },
        "news": "### 🚩 DIRETTIVE PRE-SEASON 6\nInserire qui gli ordini per la squadra AOSR.",
        "s6_meta": "### ⚔️ TREND SEASON 6\nAnalisi eroi e formazioni.",
        "academy": "### 🎓 ACCADEMIA CADETTI\nLinee guida crescita nuovi membri.",
        "drone": "### 🤖 TECH DRONE\nFocus componenti e chip."
    }

def load_db():
    defaults = get_defaults()
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
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
st.sidebar.markdown(f"<h2 style='text-align: center;'>{st.session_state.db['config']['titolo_display']}</h2>", unsafe_allow_html=True)
st.sidebar.write(f"**Server:** {st.session_state.db['config']['server']}")
st.sidebar.divider()
page = st.sidebar.selectbox("MODULO TATTICO", ["📡 DASHBOARD", "⚔️ SEASON 6", "🎓 ACCADEMIA", "🤖 DRONE & GEAR"])

# --- FUNZIONE EDITABILE UNIVERSALE ---
def pro_section(key, title):
    st.markdown(f"<div class='section-card'>", unsafe_allow_html=True)
    col_t, col_e = st.columns([0.8, 0.2])
    with col_t: st.subheader(title)
    with col_e: edit = st.toggle("EDIT", key="t_"+key)
    
    content = st.session_state.db.get(key, "")
    if edit:
        new_val = st.text_area("Modifica Contenuto", value=content, height=250, key="a_"+key)
        if st.button("💾 SALVA MODIFICHE", key="b_"+key):
            st.session_state.db[key] = new_val
            save()
            st.rerun()
    else:
        st.markdown(content)
    st.markdown("</div>", unsafe_allow_html=True)

# --- PAGINE ---
if page == "📡 DASHBOARD":
    # Titolo AOSR SQUAD in alto
    st.markdown(f"<div class='main-title'>{st.session_state.db['config']['titolo_display']}</div>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #888;'>{st.session_state.db['config']['motto']}</p>", unsafe_allow_html=True)

    # --- PANNELLO DI CONTROLLO DASHBOARD ---
    with st.expander("🛠️ PANNELLO DI CONTROLLO (Gestione AOSR)"):
        c_app1, c_app2, c_app3 = st.columns(3)
        edit_titolo = c_app1.text_input("Titolo Squadra", st.session_state.db['config']['titolo_display'])
        edit_server = c_app2.text_input("Server", st.session_state.db['config']['server'])
        edit_motto = c_app3.text_input("Motto Squadra", st.session_state.db['config']['motto'])
        
        c_st1, c_st2, c_st3 = st.columns(3)
        edit_membri = c_st1.text_input("Membri", st.session_state.db['stats']['Membri'])
        edit_potenza = c_st2.text_input("Media Potenza S1", st.session_state.db['stats']['S1_Media'])
        edit_rank = c_st3.text_input("Rank Server", st.session_state.db['stats']['Power_Rank'])
        
        if st.button("💾 APPLICA MODIFICHE"):
            st.session_state.db['config'] = {"titolo_display": edit_titolo, "server": edit_server, "motto": edit_motto}
            st.session_state.db['stats'] = {"Membri": edit_membri, "S1_Media": edit_potenza, "Power_Rank": edit_rank}
            save()
            st.rerun()

    st.divider()

    # Visualizzazione Metriche
    stats = st.session_state.db['stats']
    c1, c2, c3 = st.columns(3)
    c1.metric("Membri Alleanza", stats['Membri'])
    c2.metric("Potenza Media S1", stats['S1_Media'])
    c3.metric("Rank Server", stats['Power_Rank'])
    
    st.divider()
    pro_section("news", "📢 DIRETTIVE DI GUERRA")

elif page == "⚔️ SEASON 6":
    st.title("⚔️ SEASON 6 STRATEGY")
    pro_section("s6_meta", "🔥 Meta e Nuovi Eroi")

elif page == "🎓 ACCADEMIA":
    st.title("🎓 ACCADEMIA CADETTI")
    pro_section("academy", "📝 Programma Crescita")

elif page == "🤖 DRONE & GEAR":
    st.title("🤖 REPARTO TECNICO")
    pro_section("drone", "🛠️ Ottimizzazione Drone & Equipaggiamento")
