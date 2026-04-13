import streamlit as st
import pandas as pd
import json
import os

# --- FIX DATABASE & INITIALIZATION ---
DB_FILE = "alliance_pro_data.json"

def load_pro_data():
    # Definiamo TUTTE le chiavi necessarie per evitare KeyError
    default_data = {
        "news": "### 📢 Benvenuti Comandanti!\nInizia la preparazione alla **Season 6**. Focus: Crescita Cadetti.",
        "meta_s1": "### ⚔️ S1 Meta (Season 5 Final/S6 Ready)\n*Dati in aggiornamento...*",
        "drone_status": "Focus: Chip Livello 20+.",
        "gear_priority": "Priorità: Cannone e Radar Mitici.",
        "daily_duel": {
            "Lunedì": "Radar", "Martedì": "Costruzione", "Mercoledì": "Ricerca", 
            "Giovedì": "Addestramento", "Venerdì": "Eroi", "Sabato": "Guerra", "Domenica": "Libero"
        },
        "s6_prep": "### ❄️ Road to Season 6\n1. Accumulo Exp Eroe\n2. Risparmio Casse Scelta\n3. Ottimizzazione Squadre B e C."
    }
    
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            data = json.load(f)
            # Merge con default per aggiungere chiavi mancanti (Fix per il tuo errore)
            for key, value in default_data.items():
                if key not in data:
                    data[key] = value
            return data
    return default_data

# Inizializzazione sicura
if 'db' not in st.session_state:
    st.session_state.db = load_pro_data()

# --- FUNZIONE RENDER EDITABILE (Migliorata con gestione errori) ---
def render_editable_block(key, title):
    st.markdown(f"<div class='section-box'>", unsafe_allow_html=True)
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.subheader(title)
    with col2:
        edit_mode = st.toggle("EDIT", key=f"tgl_{key}")
    
    # Recupero valore con fallback per evitare crash
    content_value = st.session_state.db.get(key, "Dati mancanti. Clicca su EDIT per inserirli.")
    
    if edit_mode:
        new_content = st.text_area("Update:", value=content_value, height=300, key=f"area_{key}")
        if st.button("💾 SALVA", key=f"save_{key}"):
            st.session_state.db[key] = new_content
            with open(DB_FILE, "w") as f:
                json.dump(st.session_state.db, f, indent=4)
            st.success("Dati salvati!")
            st.rerun()
    else:
        st.markdown(content_value)
    st.markdown("</div>", unsafe_allow_html=True)
