import streamlit as st
import pandas as pd
import json
import os

# --- STYLE ---
st.set_page_config(page_title="LW: COMMAND CENTER S6", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; }
    .section-card { 
        padding: 25px; border-radius: 15px; border-left: 5px solid #f39c12; 
        background-color: #1c2128; margin-bottom: 20px;
    }
    h1, h2, h3 { color: #f39c12 !important; }
    </style>
""", unsafe_allow_html=True)

# --- DATABASE ENGINE (ULTRA ROBUSTO) ---
DB_FILE = "alliance_pro_data_v2.json"

def get_defaults():
    return {
        "news": "### 🚩 OBIETTIVI PRE-SEASON 6\nFocus: Crescita Cadetti e accumulo risorse.",
        "s6_meta": "### ⚔️ TREND SEASON 6\nAnalisi in corso...",
        "academy": "### 🎓 ACCADEMIA CADETTI\nInserire linee guida per i nuovi membri.",
        "drone": "### 🤖 TECH DRONE\nPriorità: Attacco.",
        "stats": {"Membri": "100", "S1_Media": "22M", "Power_Rank": "#1"}
    }

def load_db():
    defaults = get_defaults()
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
            # Verifica che tutte le chiavi base esistano, altrimenti usa default
            for key in defaults:
                if key not in data:
                    data[key] = defaults[key]
            return data
        except:
            return defaults
    return defaults

if 'db' not in st.session_state:
    st.session_state.db = load_db()

def save():
    with open(DB_FILE, "w") as f:
        json.dump(st.session_state.db, f, indent=4)

# --- UI LOGIC ---
st.sidebar.title("🛡️ S6 COMMAND")
page = st.sidebar.selectbox("MODULO TATTICO", ["DASHBOARD", "SEASON 6 PREP", "ACCADEMIA", "DRONE & GEAR"])

def pro_section(key, title):
    st.markdown(f"<div class='section-card'>", unsafe_allow_html=True)
    col_t, col_e = st.columns([0.8, 0.2])
    with col_t: st.subheader(title)
    with col_e: edit = st.toggle("MODIFICA", key="t_"+key)
    
    content = st.session_state.db.get(key, "Dati non trovati.")
    
    if edit:
        new_val = st.text_area("Update", value=content if isinstance(content, str) else str(content), height=250, key="a_"+key)
        if st.button("SALVA", key="b_"+key):
            st.session_state.db[key] = new_val
            save()
            st.rerun()
    else:
        st.markdown(content)
    st.markdown("</div>", unsafe_allow_html=True)

# --- PAGES ---
if page == "DASHBOARD":
    st.title("📡 Tactical Overview")
    
    # Recupero sicuro delle statistiche
    stats = st.session_state.db.get("stats", get_defaults()["stats"])
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Membri Alleanza", stats.get("Membri", "N/A"))
    c2.metric("Media Potenza S1", stats.get("S1_Media", "N/A"))
    c3.metric("Rank Server", stats.get("Power_Rank", "N/A"))
    
    pro_section("news", "📢 DIRETTIVE DI GUERRA")

elif page == "SEASON 6 PREP":
    st.title("❄️ Road to Season 6")
    pro_section("s6_meta", "⚔️ Analisi Meta & Nuovi Eroi")

elif page == "ACCADEMIA":
    st.title("🎓 Accademia")
    pro_section("academy", "📝 Crescita Ragazzi")

elif page == "DRONE & GEAR":
    st.title("🛠️ Reparto Armamenti")
    pro_section("drone", "🤖 Drone & Gear")
