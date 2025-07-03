import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'


from transformers import pipeline
import soundfile as sf

# -*- coding: utf-8 -*-

def convert_audio_to_text(audio_filepath,whisper_model="base"):
    """
    Converte un file audio .wav in testo utilizzando il modello Whisper passato.

    Args:
        audio_filepath (str): Il percorso completo del file audio .wav da trascrivere.

    Returns:
        str: Il testo trascritto dal file audio, oppure None in caso di errore.
    """
    if not os.path.exists(audio_filepath):
        print(f"Errore: Il file '{audio_filepath}' non esiste.")
        return None

    if not audio_filepath.lower().endswith(".wav"):
        print(f"Errore: Il file '{audio_filepath}' non è un file .wav. Si prega di fornire un file .wav.")
        return None

    try:
        # Verifica se il file .wav è valido e leggibile
        with sf.SoundFile(audio_filepath, 'r') as f:
            samplerate = f.samplerate
            channels = f.channels
            duration = len(f) / samplerate
            print(f"Caricamento del file audio: {audio_filepath}")
            print(f"Frequenza di campionamento: {samplerate} Hz")
            print(f"Canali: {channels}")
            print(f"Durata: {duration:.2f} secondi")

        print(f"Inizializzazione del modello Whisper '{whisper_model}'...")
        # Inizializza la pipeline di riconoscimento vocale con il modello 'tiny'
        # Se hai una GPU e vuoi usarla, puoi specificare device=0 (per la prima GPU)
        # transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-tiny", device=0)
        transcriber = pipeline("automatic-speech-recognition", model=f"openai/whisper-{whisper_model}")
        print("Modello caricato. Trascrizione in corso...")

        # Esegui la trascrizione
        result = transcriber(audio_filepath,generate_kwargs={"language": "it"})

        if result and "text" in result:
            return result["text"]
        else:
            print("Nessun testo trovato nel risultato della trascrizione.")
            return None

    except Exception as e:
        print(f"Si è verificato un errore durante la trascrizione: {e}")
        return None
    
import subprocess

def convert_to_whisper_format(input_path: str, output_path: str = "converted_for_whisper.wav"):
    """
    Converte un file audio in formato WAV mono, 16 kHz, 16-bit PCM.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File non trovato: {input_path}")

    command = [
        "ffmpeg",
        "-i", input_path,
        "-ac", "1",           # mono
        "-ar", "16000",       # 16 kHz
        "-acodec", "pcm_s16le",  # WAV PCM 16-bit little endian
        output_path,
        "-y"  # sovrascrive se esiste
    ]

    print(f"Converto {input_path} → {output_path}")
    subprocess.run(command, check=True)
    print("Conversione completata.")

# Esempio d'uso:
# convert_to_whisper_format("mio_audio.wav")

# Esegui la trascrizione

if __name__ == '__main__':
    print("--- Trascrizione Audio Esempio ---")
    transcribed_text = convert_audio_to_text("file.wav")
    try:
        if transcribed_text:
            print("\n--- Testo Trascritto ---")
            print(transcribed_text)
            print("-----------------------")
        else:
            print("\nLa trascrizione non è riuscita.")
    except ValueError as e:
        print(f"Errore: {e}")