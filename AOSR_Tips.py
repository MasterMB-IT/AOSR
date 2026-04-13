import streamlit as st
import pandas as pd

# Configurazione Pagina
st.set_page_config(page_title="Last War: Elite Handbook", layout="wide")

# --- SIDEBAR (Navigazione) ---
st.sidebar.title("🛡️ Mega Diario Alleanza")
menu = st.sidebar.radio(
    "Vai a:",
    ["Dashboard Home", "Meta Formazioni (S5)", "Armamenti & Gear", "Drone & Chip", "Calendario Strategico"]
)

# --- SEZIONE 1: DASHBOARD HOME ---
if menu == "Dashboard Home":
    st.title("🚀 Benvenuti nel Manuale Elite - Season 5")
    st.markdown("""
    Questo diario è lo strumento strategico ufficiale della nostra Alleanza. 
    L'obiettivo è massimizzare il rendimento in guerra e ottimizzare le risorse.
    
    **Focus Attuale:** Ottimizzazione Squadre per Capital War e Duel.
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("💡 **Consiglio del giorno:** Controlla i buff dei chip del drone prima del Duel di oggi!")
    with col2:
        st.warning("⚠️ **Reminder S5:** Focus sui Cristalli Stagionali per la Squadra 1.")

# --- SEZIONE 2: META FORMAZIONI ---
elif menu == "Meta Formazioni (S5)":
    st.title("⚔️ Formazioni Meta Consigliate")
    
    tipo_squadra = st.selectbox("Seleziona Squadra:", ["Squadra 1 (Main - Carri)", "Squadra 2 (Elicotteri)", "Squadra 3 (Missili)"])
    
    if tipo_squadra == "Squadra 1 (Main - Carri)":
        st.subheader("La Formazione Dominante S5")
        st.image("https://via.placeholder.com/800x400.png?text=Layout+Eroi+Posizioni+1-5", caption="Schema Posizionamento")
        
        st.write("**Composizione:**")
        st.table(pd.DataFrame({
            'Posizione': [1, 2, 3, 4, 5],
            'Eroe': ['Murphy (UR)', 'Williams (UR)', 'Kimberly (UR)', 'Stetmann (UR)', 'Marshall (UR)'],
            'Ruolo': ['Tank / Buff Dmg', 'Tank / Difesa', 'Main DPS', 'Support DPS', 'Buffer']
        }))
        
        with st.expander("Perché questa formazione?"):
            st.write("Dettagli sulle sinergie, ordine di attivazione delle skill e posizionamento tattico...")

# --- SEZIONE 3: ARMAMENTI & GEAR ---
elif menu == "Armamenti & Gear":
    st.title("🛠️ Ottimizzazione Armamenti")
    
    st.subheader("Priorità Raffinamento (Mythic/Rosso)")
    st.markdown("""
    1. **Cannone (DPS):** Priorità assoluta per Kimberly.
    2. **Armatura (Tank):** Per Murphy/Williams per resistere ai primi colpi.
    3. **Radar:** Cruciale per la riduzione danno critico.
    """)
    
    # Esempio di calcolatore o tabella comparativa
    st.write("### Statistiche Secondarie Focus")
    st.dataframe(pd.DataFrame({
        'Pezzo': ['Cannone', 'Armatura', 'Radar', 'Chip'],
        'Stat Primaria': ['Attacco', 'HP', 'Difesa', 'HP'],
        'Stat Secondaria S5': ['Critico %', 'Rid. Danno %', 'Evasione', 'Resistenza Crit.']
    }))

# --- SEZIONE 4: DRONE & CHIP ---
elif menu == "Drone & Chip":
    st.title("🤖 Drone e Componenti Tattici")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Livello Drone Suggerito", "150+", "+5% per ogni 10 lvl")
    with col_b:
        st.metric("Focus Chip", "Attacco / Danno Skill")

    st.markdown("""
    ### Configurazione Chip Ideale
    - **Slot 1 & 2:** Chip Attacco (Danni critici e perforazione)
    - **Slot 3 & 4:** Chip Difesa (Riduzione danno e HP)
    """)

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.write("✍️ *Aggiornato dai Comandanti dell'Alleanza*")
