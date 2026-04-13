import streamlit as st
import json
import os

# --- FUNZIONI DI SERVIZIO PER SALVATAGGIO DATI ---
DB_FILE = "data_alleanza.json"

def carica_dati():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {
        "meta_squadra_1": "Inserisci qui la formazione meta...",
        "drone_tips": "Consigli per il drone S5...",
        "gear_priority": "Priorità armamenti..."
    }

def salva_dati(dati):
    with open(DB_FILE, "w") as f:
        json.dump(dati, f)

# Inizializzazione dati
if 'database' not in st.session_state:
    st.session_state.database = carica_dati()

# --- INTERFACCIA ---
st.title("🛡️ Manuale Collaborativo Last War S5")

menu = st.sidebar.radio("Sezione:", ["Meta Formazioni", "Drone & Chip", "Armamenti"])

# --- LOGICA SEZIONE MODIFICABILE ---
def sezione_interattiva(chiave_db, titolo):
    st.header(titolo)
    
    # Stato della modifica (attivo/disattivo)
    edit_mode = st.toggle(f"Modalità Modifica {titolo}", key=f"tog_{chiave_db}")
    
    if edit_mode:
        # Area di testo per modificare il contenuto
        nuovo_testo = st.text_area("Modifica il contenuto (supporta Markdown):", 
                                   value=st.session_state.database[chiave_db], 
                                   height=300)
        if st.button(f"Salva {titolo}"):
            st.session_state.database[chiave_db] = nuovo_testo
            salva_dati(st.session_state.database)
            st.success("Dati aggiornati con successo!")
            st.rerun()
    else:
        # Visualizzazione normale
        st.markdown(st.session_state.database[chiave_db])

# --- RENDER DELLE SEZIONI ---
if menu == "Meta Formazioni":
    sezione_interattiva("meta_squadra_1", "⚔️ Meta Formazioni Season 5")

elif menu == "Drone & Chip":
    sezione_interattiva("drone_tips", "🤖 Strategia Drone e Chip")

elif menu == "Armamenti":
    sezione_interattiva("gear_priority", "🛠️ Guida Armamenti Mythic")
