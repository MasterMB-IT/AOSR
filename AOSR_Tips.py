import streamlit as st
import json
import requests
import base64
import time
import os

# --- CONFIGURAZIONE GITHUB ---
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO_NAME = st.secrets.get("REPO_NAME", "")
BRANCH = "main"
DB_FILE = "aosr_squad_db.json"

st.set_page_config(page_title="AOSR COMMAND CENTER", layout="wide")

# --- FUNZIONE PER CARICARE FILE SU GITHUB ---
def upload_file_to_github(uploaded_file):
    """Carica un file fisico nella cartella 'img/' del tuo repository GitHub"""
    file_path = f"img/{uploaded_file.name}"
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{file_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    # Controlla se il file esiste già per ottenere lo SHA
    res = requests.get(url, headers=headers)
    sha = res.json().get("sha") if res.status_code == 200 else None
    
    # Codifica il file in Base64
    base64_content = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
    
    payload = {
        "message": f"Upload immagine: {uploaded_file.name}",
        "content": base64_content,
        "branch": BRANCH
    }
    if sha: payload["sha"] = sha

    with st.spinner(f"Trasmissione file {uploaded_file.name} in corso..."):
        r = requests.put(url, json=payload, headers=headers)
        if r.status_code in [200, 201]:
            # Costruisce l'URL pubblico dell'immagine caricata
            raw_url = f"https://raw.githubusercontent.com/{REPO_NAME}/{BRANCH}/{file_path}"
            return raw_url
        else:
            st.error(f"Errore caricamento: {r.json().get('message')}")
            return None

# --- DATABASE ENGINE ---
def load_db():
    try:
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{DB_FILE}?t={int(time.time())}"
        res = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
        if res.status_code == 200:
            return json.loads(base64.b64decode(res.json()['content']).decode())
    except: pass
    return {"news": "Benvenuto", "meta": {"t1": ""}} # Default minimo

def save_db(data):
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{DB_FILE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    sha = r.json().get("sha") if r.status_code == 200 else None
    content = base64.b64encode(json.dumps(data, indent=4).encode()).decode()
    payload = {"message": "Update DB", "content": content, "sha": sha}
    requests.put(url, json=payload, headers=headers)
    st.success("✅ DATABASE SINCRONIZZATO")
    time.sleep(1)
    st.rerun()

if 'db' not in st.session_state:
    st.session_state.db = load_db()

# --- UI ---
st.title("🛡️ AOSR FILE MANAGER")

# --- SEZIONE CARICAMENTO ---
st.markdown("### 📤 CARICA IMMAGINE DI GIOCO")
uploaded_file = st.file_uploader("Trascina qui lo screenshot", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Anteprima Locale", width=300)
    if st.button("🚀 INVIA AL SERVER GITHUB"):
        img_url = upload_file_to_github(uploaded_file)
        if img_url:
            st.success(f"File caricato con successo!")
            st.code(f"![Descrizione]({img_url})", language="markdown")
            st.info("Copia il codice qui sopra e incollalo nella sezione dove vuoi far apparire l'immagine.")

st.divider()

# --- ESEMPIO DI EDITING SEZIONE ---
st.subheader("📝 MODIFICA SEZIONE TATTICA")
tab_selezionata = st.selectbox("Scegli sezione:", ["meta", "tech", "routine"])
t_key = "t1" # Esempio semplificato

current_content = st.session_state.db.get(tab_selezionata, {}).get(t_key, "")
new_content = st.text_area("Contenuto (Incolla qui il codice dell'immagine):", value=current_content, height=300)

if st.button("💾 SALVA MODIFICHE"):
    if tab_selezionata not in st.session_state.db: st.session_state.db[tab_selezionata] = {}
    st.session_state.db[tab_selezionata][t_key] = new_content
    save_db(st.session_state.db)

st.markdown("---")
st.markdown("### 👁️ ANTEPRIMA VISIVA")
st.markdown(current_content)
