import streamlit as st
import pandas as pd
import json
import os

# --- CONFIGURAZIONE ESTETICA (STILE GIOCO) ---
st.set_page_config(page_title="Last War Command Center", layout="wide")

def local_css():
    st.markdown("""
        <style>
        /* Sfondo e colori base */
        .main { background-color: #0e1117; color: #e0e0e0; }
        .stButton>button { 
            background-color: #f39c12; color: black; font-weight: bold; 
            border-radius: 5px; border: none; width: 100%;
        }
        .stButton>button:hover { background-color: #d48400; border: 1px solid white; }
        
        /* Sidebar stile militare */
        [data-testid="stSidebar"] { background-color: #1a1c23; border-right: 2px solid #f39c12; }
        
        /* Header stile Season 5 */
        .game-header {
            background: linear-gradient(90deg, #1f4068, #1b1b2f);
            padding: 20px;
            border-radius: 10px;
            border-left: 10px solid #f39c12;
            margin-bottom: 25px;
        }
        
        /* Box info */
        .stAlert { background-color: #162447; border: 1px solid #1f4068; color: #00d4ff; }
        </style>
    """, unsafe_allow_html=True)

local_css()

# --- GESTIONE DATI ---
DB_FILE = "advanced_data.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {
        "SQUAD_1": {"desc": "Dati Squadra 1...", "table": [["Kim", "5*", "Cannone Rosso"]]},
        "DRONE": "Priorità Chip: 1. Attacco, 2. HP...",
        "BOSS_STRAT": "Strategie per Boss Season 5..."
    }

def save_data(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

# --- BARRA LATERALE (NAVIGAZIONE AVANZATA) ---
with st.sidebar:
    st.image("https://img.freepik.com/premium-vector/shield-warrior-logo-design_100735-45.jpg", width=100) # Placeholder logo
    st.title("COMMAND CENTER")
    st.subheader("Season 5: Warpath")
    
    mode = st.radio("SISTEMI OPERATIVI:", 
                   ["📊 Dashboard", "⚔️ Meta Formazioni", "🤖 Drone & Chip", "💎 Risorse & S5", "🛠️ Pannello Admin"])
    
    st.divider()
    st.info("💡 Livello Alleanza: TOP 1\nServer: #XXX")

# --- LOGICA APPLICAZIONE ---

# Funzione universale per rendere una sezione modificabile
def editable_section(key, title, type="text"):
    st.markdown(f"<div class='game-header'><h2>{title}</h2></div>", unsafe_allow_html=True)
    
    col_view, col_edit = st.columns([0.8, 0.2])
    
    with col_edit:
        edit_btn = st.toggle("📝 MODIFICA", key=f"tgl_{key}")
    
    if edit_btn:
        if type == "text":
            new_val = st.text_area("Aggiorna Manuale:", value=st.session_state.db.get(key, ""), height=300)
            if st.button("SALVA MODIFICHE", key=f"btn_{key}"):
                st.session_state.db[key] = new_val
                save_data(st.session_state.db)
                st.rerun()
        elif type == "table":
            st.warning("Usa il Pannello Admin per gestire tabelle complesse.")
    else:
        st.markdown(st.session_state.db.get(key, "Nessun dato inserito."))

# --- PAGINE ---

if mode == "📊 Dashboard":
    st.markdown("<div class='game-header'><h1>DASHBOARD COMANDO</h1></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Status Guerra", "ATTIVO", delta="Capital War Sabato")
    c2.metric("Potenza Media S1", "25.4M", delta="+1.2M")
    c3.metric("Obiettivo Settimanale", "Livello 100", delta="In corso")
    
    st.divider()
    editable_section("news", "📢 ULTIME DIRETTIVE")

elif mode == "⚔️ Meta Formazioni":
    editable_section("SQUAD_1", "🔥 SQUADRA 1 - IL META ATTUALE")
    with st.expander("📊 Calcolatore Danni (Simulatore)"):
        atk = st.number_input("Attacco Eroe", 1000, 1000000)
        bonus = st.slider("Bonus Legame (%)", 0, 40, 20)
        total = atk * (1 + bonus/100)
        st.success(f"Potenza Stimata: {total:,.0f}")

elif mode == "🤖 Drone & Chip":
    editable_section("DRONE", "🤖 CONFIGURAZIONE DRONE OPTIMAL")

elif mode == "💎 Risorse & S5":
    editable_section("BOSS_STRAT", "💎 GESTIONE CRISTALLI E BOSS S5")

elif mode == "🛠️ Pannello Admin":
    st.title("⚙️ Impostazioni Avanzate")
    if st.button("RESET DATABASE (ATTENZIONE)"):
        if st.checkbox("Confermo il reset"):
            st.session_state.db = load_data()
            save_data(st.session_state.db)
            st.rerun()
