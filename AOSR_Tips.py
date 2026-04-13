import streamlit as st
import pandas as pd
import json
import os

# --- INIZIALIZZAZIONE E STYLE ---
st.set_page_config(page_title="LAST WAR: ELITE COMMAND", layout="wide")

def apply_pro_style():
    st.markdown("""
        <style>
        .main { background-color: #0b0e11; color: #f0f0f0; }
        .stTabs [data-baseweb="tab-list"] { gap: 24px; }
        .stTabs [data-baseweb="tab"] { 
            height: 50px; background-color: #1a1c23; border-radius: 5px 5px 0 0;
            color: #f39c12; font-weight: bold; border: 1px solid #333;
        }
        .stTabs [aria-selected="true"] { background-color: #f39c12 !format; color: black !important; }
        .section-box { 
            padding: 20px; border-radius: 10px; border: 1px solid #f39c12; 
            background-color: #161a21; margin-bottom: 20px;
        }
        .ur-text { color: #f39c12; font-weight: bold; text-shadow: 0px 0px 5px #f39c12; }
        </style>
    """, unsafe_allow_html=True)

apply_pro_style()

# --- ENGINE GESTIONE DATI (PERSISTENZA) ---
DB_FILE = "alliance_pro_data.json"

def load_pro_data():
    default_data = {
        "meta_s1": "### ⚔️ S1 Meta (Carri)\n1. **Murphy** (P1 - Tank/Buff)\n2. **Williams** (P2 - Tank/Defense)\n3. **Kimberly** (P3 - Burst DPS)\n4. **Stetmann** (P4 - AoE DPS)\n5. **Marshall** (P5 - Support)",
        "drone_status": "Focus Chip: Componenti Attacco Liv. 20+ richiesti per S5.",
        "daily_duel": {"Lunedì": "Radar", "Martedì": "Costruzione", "Mercoledì": "Ricerca", "Giovedì": "Addestramento", "Venerdì": "Eroi", "Sabato": "Guerra", "Domenica": "Libero"},
        "gear_priority": "| Pezzo | Priorità | Focus Stat |\n|---|---|---|\n| Cannone | 1 | Critico |\n| Radar | 2 | Rid. Danno |"
    }
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return default_data

def save_pro_data(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

if 'db' not in st.session_state:
    st.session_state.db = load_pro_data()

# --- SIDEBAR & NAVIGAZIONE ---
with st.sidebar:
    st.markdown("<h1 style='color:#f39c12;'>🛡️ LW ELITE V1.5</h1>", unsafe_allow_html=True)
    st.write("**Stato Season:** ❄️ Season 5 (Winter War)")
    st.divider()
    page = st.radio("SISTEMI TATTICI", ["📡 Dashboard", "⚔️ Meta & Formazioni", "🤖 Drone & Gear", "📅 Duel Calendar", "⚙️ Admin Terminal"])

# --- FUNZIONE EDITABILE ---
def render_editable_block(key, title):
    st.markdown(f"<div class='section-box'>", unsafe_allow_html=True)
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.subheader(title)
    with col2:
        edit_mode = st.toggle("EDIT", key=f"tgl_{key}")
    
    if edit_mode:
        content = st.text_area("Aggiorna i dati tattici:", value=st.session_state.db[key], height=300, key=f"area_{key}")
        if st.button("💾 SALVA", key=f"save_{key}"):
            st.session_state.db[key] = content
            save_pro_data(st.session_state.db)
            st.success("Database aggiornato!")
            st.rerun()
    else:
        st.markdown(st.session_state.db[key])
    st.markdown("</div>", unsafe_allow_html=True)

# --- LOGICA PAGINE ---

if page == "📡 Dashboard":
    st.title("📡 Tactical Overview")
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Obiettivo VS Alleanza", "TOP 10", "Rank 1")
    with c2: st.metric("Squadra 1 Target", "28M Power", "+1.5M")
    with c3: st.metric("Risorse Accumulate", "85%", "Tier 9")
    
    st.divider()
    render_editable_block("news", "🚀 DIRETTIVE DI GUERRA")

elif page == "⚔️ Meta & Formazioni":
    st.title("⚔️ Combat Theory")
    tab1, tab2 = st.tabs(["Meta S1/S2", "Posizionamento Tattico"])
    
    with tab1:
        render_editable_block("meta_s1", "🔥 Formazioni Dominanti (Season 5)")
    
    with tab2:
        st.info("💡 **Tip Pro:** In S5, invertire Marshall e Stetmann può aumentare la sopravvivenza contro i team Elicottero.")
        st.image("https://via.placeholder.com/800x200?text=Schema+Posizionamento+P1+P2+P3+P4+P5", caption="Ordine di Ingaggio")

elif page == "🤖 Drone & Gear":
    st.title("🛠️ Tech & Arsenal")
    render_editable_block("gear_priority", "🔴 Priorità Equipaggiamento Mitico")
    render_editable_block("drone_status", "🤖 Ottimizzazione Componenti Drone")

elif page == "📅 Duel Calendar":
    st.title("📅 Programma Settimanale Duel")
    df_duel = pd.DataFrame([st.session_state.db["daily_duel"]]).T
    df_duel.columns = ["Focus Evento"]
    st.table(df_duel)
    
    if st.toggle("Modifica Calendario"):
        day = st.selectbox("Giorno", list(st.session_state.db["daily_duel"].keys()))
        val = st.text_input("Nuovo Focus", st.session_state.db["daily_duel"][day])
        if st.button("Aggiorna Giorno"):
            st.session_state.db["daily_duel"][day] = val
            save_pro_data(st.session_state.db)
            st.rerun()

elif page == "⚙️ Admin Terminal":
    st.title("⚙️ Alliance Management")
    st.write("Scarica il database attuale per backup:")
    st.download_button("Download JSON", json.dumps(st.session_state.db), "alliance_backup.json")
