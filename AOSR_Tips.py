import streamlit as st
import pandas as pd
import json
import os

# --- STYLE INJECTION (DARK MILITARY) ---
st.set_page_config(page_title="LW: COMMAND CENTER S6", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; }
    .stTextArea textarea { background-color: #0d1117; color: #f39c12; border: 1px solid #f39c12; }
    .section-card { 
        padding: 25px; border-radius: 15px; border-left: 5px solid #f39c12; 
        background-color: #1c2128; margin-bottom: 20px; box-shadow: 5px 5px 15px rgba(0,0,0,0.5);
    }
    h1, h2, h3 { color: #f39c12 !important; }
    </style>
""", unsafe_allow_html=True)

# --- DATABASE ENGINE ---
DB_FILE = "alliance_pro_data_v2.json"

def init_db():
    defaults = {
        "news": "### 🚩 OBIETTIVI PRE-SEASON 6\n1. Portare la S1 a 25M+ di potenza.\n2. Accumulare 500+ Casse Scelta Eroe.",
        "s6_meta": "### ⚔️ TREND SEASON 6\n*Focus sulla difesa e contrattacco. Eroi consigliati...*",
        "academy": "### 🎓 ACCADEMIA CADETTI\nRegole per la crescita dei nuovi membri...",
        "drone": "### 🤖 TECH DRONE\nPriorità componenti: Attacco > HP > Difesa.",
        "stats": {"Membri": 100, "S1_Media": "22M", "Power_Rank": "#1"}
    }
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            data = json.load(f)
            for k, v in defaults.items():
                if k not in data: data[k] = v
            return data
    return defaults

if 'db' not in st.session_state:
    st.session_state.db = init_db()

def save():
    with open(DB_FILE, "w") as f:
        json.dump(st.session_state.db, f, indent=4)

# --- UI LOGIC ---
st.sidebar.image("https://img.icons8.com/color/512/military-rank.png", width=80)
st.sidebar.title("S6 COMMAND")
page = st.sidebar.selectbox("MODULO TATTICO", ["DASHBOARD", "SEASON 6 PREP", "ACCADEMIA", "DRONE & GEAR"])

def pro_section(key, title):
    st.markdown(f"<div class='section-card'>", unsafe_allow_html=True)
    col_t, col_e = st.columns([0.8, 0.2])
    with col_t: st.subheader(title)
    with col_e: edit = st.toggle("MODIFICA", key="t_"+key)
    
    if edit:
        new_val = st.text_area("Update", value=st.session_state.db.get(key, ""), height=250, key="a_"+key)
        if st.button("SALVA", key="b_"+key):
            st.session_state.db[key] = new_val
            save()
            st.success("Dati criptati e salvati.")
            st.rerun()
    else:
        st.markdown(st.session_state.db.get(key, ""))
    st.markdown("</div>", unsafe_allow_html=True)

# --- PAGES ---
if page == "DASHBOARD":
    st.title("📡 Tactical Overview")
    c1, c2, c3 = st.columns(3)
    c1.metric("Membri Alleanza", st.session_state.db['stats']['Membri'])
    c2.metric("Media Potenza S1", st.session_state.db['stats']['S1_Media'])
    c3.metric("Rank Server", st.session_state.db['stats']['Power_Rank'])
    pro_section("news", "📢 DIRETTIVE DI GUERRA")

elif page == "SEASON 6 PREP":
    st.title("❄️ Road to Season 6")
    pro_section("s6_meta", "⚔️ Analisi Meta & Nuovi Eroi")

elif page == "ACCADEMIA":
    st.title("🎓 Accademia di Addestramento")
    pro_section("academy", "📝 Guida alla Crescita Ragazzi")

elif page == "DRONE & GEAR":
    st.title("🛠️ Reparto Armamenti")
    pro_section("drone", "🤖 Drone & Componenti")
