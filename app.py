import streamlit as st
from audiorecorder import audiorecorder
from transcribe import *
from src.report_manager import ReportManager
from src.convert import *


# --- 1. IMPOSTAZIONI E FUNZIONI PLACEHOLDER ---
st.set_page_config(page_title="Agente Intelligente", page_icon="🤖", layout="wide")
st.title("🤖 Chat con il tuo Agente Intelligente")

# (Le tue funzioni placeholder rimangono qui)
def get_agent_response(prompt):
    return f"Risposta dell'agente per: '{prompt}'"

def export_chat(history, format_type):
    content_markdown = ""
    for msg in history:
        content_markdown += f"**{msg['role'].capitalize()}**: {msg['content']}\n\n"

    if format_type == "Markdown":
        # Restituisce i byte della stringa Markdown
        return content_markdown.encode("utf-8")

    elif format_type == "DOCX":
        # Chiama la nuova funzione in-memory
        return convert_md_to_docx_in_memory(content_markdown)

    elif format_type == "HTML":
        # Chiama la nuova funzione in-memory, ottieni la stringa HTML, poi codificala in bytes
        html_string = convert_md_to_html_in_memory(content_markdown)
        return html_string.encode("utf-8")

    elif format_type == "PDF":
        # Chiama la nuova funzione in-memory
        return convert_md_to_pdf_in_memory(content_markdown)

    # Fallback sicuro
    st.warning(f"Formato '{format_type}' non gestito. Restituisco Markdown codificato.")
    return content_markdown.encode("utf-8")


# --- 2. INIZIALIZZAZIONE E LOGICA DI STATO ---
# Questo blocco ora gestisce la logica PRIMA di disegnare i widget

# Inizializzazione degli stati (solo la prima volta)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processing_audio" not in st.session_state:
    st.session_state.processing_audio = False
if "audio_to_process" not in st.session_state:
    st.session_state.audio_to_process = None
if "user_input" not in st.session_state:
    st.session_state.user_input = ""
    
if "ai_manager" not in st.session_state:
    st.session_state.ai_manager = ReportManager()

# LOGICA SPOSTATA QUI: Se siamo in stato di elaborazione, esegui la conversione
if st.session_state.processing_audio:
    with st.spinner("Conversione audio in testo in corso..."):
        # Recupera l'audio salvato
        audio_to_process = st.session_state.audio_to_process
        
        # Esporta e converti
        audio_to_process.export("temp/audio.wav", format="wav")
        transcript = convert_audio_to_text("temp/audio.wav")
        
        # MODIFICA SICURA: Assegna il testo allo stato PRIMA che il widget venga disegnato
        st.session_state.user_input = transcript
        
        # Resetta gli stati
        st.session_state.processing_audio = False
        st.session_state.audio_to_process = None
        # Non è necessario st.rerun() qui, lo script continuerà e disegnerà la UI aggiornata
        
# --- 3. VISUALIZZAZIONE DELLA CRONOLOGIA CHAT ---
# Spostiamo la visualizzazione dei messaggi in un contenitore principale
# Questo assicura che appaia sempre sopra la barra di input
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- 4. FUNZIONE CALLBACK PER PROCESSARE L'INPUT ---
def process_input():
    # Prende il testo dalla chiave di session_state associata al text_input
    prompt = st.session_state.user_input
    if not prompt:
        return

    # Aggiungi il messaggio utente alla cronologia
    st.session_state.messages.append({"role": "user", "content": prompt})

    print("\n\n\n--------------------Prompt-------------", prompt, '\n\n\n')
    
    # Ottieni la risposta dell'agente
    with st.spinner("L'agente sta pensando..."):
        st.session_state.ai_manager.run(input=prompt)
        response = st.session_state.ai_manager.get_answer()
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Svuota la casella di testo dopo l'invio
        st.session_state.user_input = ""
    



# --- 5. SEZIONE DI INPUT PERSISTENTE IN BASSO ---
# Usiamo st.container() per raggruppare i widget di input
input_container = st.container()
with input_container:
    # Creiamo le colonne per il layout
    col1, col2, col3 = st.columns([0.75, 0.1, 0.15])

    with col1:
        # Casella di testo che chiama la callback su invio (tasto Enter)
        # ... dentro la col1
        st.text_input(
            "Scrivi il tuo messaggio...",
            key="user_input",
            on_change=process_input,
            label_visibility="collapsed",
            # RIGA DA AGGIUNGERE
            disabled=st.session_state.processing_audio 
        )

    with col2:
        # Pulsante "Invia" che chiama la stessa callback al click
        st.button("Invia", on_click=process_input, use_container_width=True)
    
    with col3:
        # Pulsante microfono: non invia dati, ma attiva/disattiva la registrazione
        if st.button("🎙️ Registra", use_container_width=True):
            # Inverte lo stato di registrazione (True -> False, False -> True)
            st.session_state.recording = not st.session_state.get('recording', False)

    # Logica per mostrare il registratore audio se lo stato è attivo
    # --- NUOVA LOGICA DI GESTIONE AUDIO ---

    # Questo blocco gestisce la visualizzazione del widget audiorecorder
# ... all'interno di "with input_container":

    # ... (le 3 colonne con text_input, button Invia e button Registra)

    # Logica per mostrare il registratore audio (ORA MOLTO PIÙ SEMPLICE)
    if st.session_state.get('recording', False):
        st.info("Registrazione audio attiva...")
        audio = audiorecorder("Start", "Stop", key="recorder")
        
        # Se la registrazione è finita, imposta gli stati e fai un rerun
        if len(audio) > 0:
            st.session_state.audio_to_process = audio
            st.session_state.processing_audio = True
            st.session_state.recording = False # Disattiva subito la registrazione
            st.rerun()

# --- 6. SIDEBAR PER L'ESPORTAZIONE ---
with st.sidebar:
    # (Il codice della sidebar rimane invariato)
    st.header("Esporta Chat")
    export_format = st.selectbox("Scegli formato", ["Markdown", "HTML", "PDF", "DOCX"])
    if st.download_button(label=f"Esporta come {export_format}", data=export_chat(st.session_state.messages,export_format), file_name=f"file_esportato.{export_format.lower()}"):
        st.success(f"Chat esportata con successo in formato {export_format}!")