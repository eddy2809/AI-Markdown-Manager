import streamlit as st
from audiorecorder import audiorecorder
from src.transcribe import *
from src.report_manager import ReportManager
from src.convert import *


# --- 1. IMPOSTAZIONI E FUNZIONI DI UTILITY ---
st.set_page_config(page_title="AI Markdown Manager", page_icon="✍🏼", layout="wide")
st.title("✍🏼 AI Markdown Manager")

def get_agent_response(prompt):
    return f"Risposta dell'agente per: '{prompt}'"

def export_chat(history, format_type):
    content_markdown = ""
    for msg in history:
        content_markdown += f"**{msg['role'].capitalize()}**: {msg['content']}\n\n"

    if format_type == "Markdown":
        return content_markdown.encode("utf-8")

    elif format_type == "DOCX":
        return convert_md_to_docx_in_memory(content_markdown)

    elif format_type == "HTML":
        html_string = convert_md_to_html_in_memory(content_markdown)
        return html_string.encode("utf-8")

    elif format_type == "PDF":
        return convert_md_to_pdf_in_memory(content_markdown)

    st.warning(f"Formato '{format_type}' non gestito. Restituisco Markdown codificato.")
    return content_markdown.encode("utf-8")

def export_file(content_markdown, format_type):
    
    if format_type == "Markdown":
        return content_markdown.encode("utf-8")

    elif format_type == "DOCX":
        return convert_md_to_docx_in_memory(content_markdown)

    elif format_type == "HTML":
        html_string = convert_md_to_html_in_memory(content_markdown)
        return html_string.encode("utf-8")

    elif format_type == "PDF":
        return convert_md_to_pdf_in_memory(content_markdown)

    st.warning(f"Formato '{format_type}' non gestito. Restituisco Markdown codificato.")
    return content_markdown.encode("utf-8")


# --- 2. INIZIALIZZAZIONE E LOGICA DI STATO ---

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

#Logica di conversione audio (va fatta qui)
if st.session_state.processing_audio:
    with st.spinner("Conversione audio in testo in corso..."):
        # Recupera l'audio salvato
        audio_to_process = st.session_state.audio_to_process
        
        # Esporta e converti
        audio_to_process.export("tmp/audio.wav", format="wav")
        transcript = convert_audio_to_text("tmp/audio.wav")
        os.remove("tmp/audio.wav")
        
        # MODIFICA SICURA: Assegna il testo allo stato PRIMA che il widget venga disegnato
        st.session_state.user_input = transcript
        
        # Resetta gli stati
        st.session_state.processing_audio = False
        st.session_state.audio_to_process = None
        
# --- 3. VISUALIZZAZIONE DELLA CRONOLOGIA CHAT ---
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- 4. FUNZIONE CALLBACK PER PROCESSARE L'INPUT CON IL TASTO INVIO ---
def process_input():
    # Prende il testo dalla chiave di session_state associata al text_input
    prompt = st.session_state.user_input
    if not prompt:
        return


    # Ottieni la risposta dell'agente
    with st.spinner("L'agente sta pensando..."):
        st.session_state.ai_manager.run(input=prompt)
        response = st.session_state.ai_manager.get_answer()
        
        # Aggiungi il messaggio utente e la risposta alla cronologia
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": "".join(["\n", response])})
        
        # Svuota la casella di testo dopo l'invio
        st.session_state.user_input = ""
    

# --- 5. SEZIONE DI INPUT PERSISTENTE IN BASSO ---
input_container = st.container()
with input_container:
    # Creiamo le colonne per il layout
    col1, col2, col3 = st.columns([0.75, 0.1, 0.15])

    with col1:
        # Casella di testo che chiama la callback su invio (tasto Enter)
        st.text_input(
            "Scrivi il tuo messaggio...",
            key="user_input",
            label_visibility="collapsed",
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

    # Questo blocco gestisce la visualizzazione del widget audiorecorder

    # Logica per mostrare il registratore audio
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
    st.header("Esporta")
    export_format = st.selectbox("Scegli formato", ["Markdown", "HTML", "PDF", "DOCX"])
    
    if st.download_button(label=f"Esporta chat come {export_format}", data=export_chat(st.session_state.messages,export_format), file_name=f"file_esportato.{export_format.lower()}"):
        st.success(f"Chat esportata con successo in formato {export_format}!")
        
    if st.download_button(label=f"Esporta documento come {export_format}", data=export_file(st.session_state.ai_manager.get_md_document(),export_format), file_name=f"file_esportato.{export_format.lower()}"):
        st.success(f"Documento esportato con successo in formato {export_format}!")
    