import os
import io
import markdown
from xhtml2pdf import pisa
from docx import Document
from pdf2docx import Converter # Per ora manteniamo, ma vedremo limiti

def read_file_in_byte(percorso_file: str) -> bytes | None:
    
    """
    Legge il contenuto di un file e lo restituisce come bytes.
    
    Args:
        percorso_file (str): Il percorso completo del file da leggere.
    
    Returns:
        bytes | None: Il contenuto del file in byte, oppure None se si verifica un errore.
    """
    try:
        with open(percorso_file, 'rb') as file:
            contenuto_byte = file.read()
        print(f"Contenuto del file '{percorso_file}' letto con successo in byte.")
        return contenuto_byte
    except FileNotFoundError:
        print(f"Errore: Il file '{percorso_file}' non è stato trovato.")
        return None
    except IOError as e:
        print(f"Errore durante la lettura del file '{percorso_file}': {e}")
        return None


def convert_md_to_html_in_memory(markdown_content: str) -> str:
    
    """
    Converte il contenuto Markdown (stringa) in HTML (stringa) direttamente in memoria.
    
    Args:
        markdown_content (str): Il contenuto Markdown da convertire.
    
    Returns:
        str: Il contenuto HTML ottenuto, oppure una stringa di errore se si verifica un problema.
    """
    try:
        html_content = markdown.markdown(markdown_content, extensions=['extra', 'codehilite'])
        return html_content
    except Exception as e:
        print(f"Errore durante la conversione Markdown a HTML in memoria: {e}")
        return "<html><body><p>Errore nella conversione HTML.</p></body></html>"

def convert_html_to_pdf_in_memory(html_content: str) -> bytes | None:
    """
    Converte il contenuto HTML (stringa) in PDF (bytes) direttamente in memoria.
    """
    try:
        # Usa BytesIO per catturare l'output PDF senza salvare su disco
        result_buffer = io.BytesIO()
        pisa_status = pisa.CreatePDF(
            html_content,    # Il contenuto HTML da convertire
            dest=result_buffer # Dove scrivere il PDF
        )
        if not pisa_status.err:
            result_buffer.seek(0) # Riporta il cursore all'inizio del buffer
            return result_buffer.getvalue() # Ottieni i bytes
        else:
            print(f"Errore PISA durante la conversione HTML a PDF: {pisa_status.err}")
            return None
    except Exception as e:
        print(f"Errore durante la conversione HTML a PDF in memoria: {e}")
        return None

def convert_md_to_pdf_in_memory(markdown_content: str) -> bytes | None:
    """
    Converte il contenuto Markdown (stringa) in PDF (bytes) passando per HTML,
    tutto direttamente in memoria.
    """
    html_content = convert_md_to_html_in_memory(markdown_content)
    if html_content:
        return convert_html_to_pdf_in_memory(html_content)
    return None

def convert_md_to_docx_in_memory(markdown_content: str) -> bytes | None:
    """
    Converte il contenuto Markdown (stringa) in DOCX (bytes) direttamente in memoria.
    Questo è un po' più complesso perché python-docx non ha un parser Markdown integrato.
    Il modo migliore sarebbe convertire Markdown a un formato intermedio che python-docx possa capire,
    o costruire il DOCX paragrafo per paragrafo.

    Data la tua precedente implementazione che passava per PDF, qui simuleremo un percorso analogo:
    Markdown -> PDF (in memoria) -> DOCX (ATTENZIONE: pdf2docx richiede file su disco, questo è un limite)
    """
    try:
        
        temp_pdf_path = "tmp/temp_export.pdf"
        temp_docx_path = "tmp/temp_export.docx"

        # Crea la directory tmp se non esiste
        os.makedirs("tmp", exist_ok=True)

        pdf_bytes = convert_md_to_pdf_in_memory(markdown_content)
        if pdf_bytes:
            with open(temp_pdf_path, "wb") as f:
                f.write(pdf_bytes)

            try:
                cv = Converter(temp_pdf_path)
                cv.convert(temp_docx_path, start=0, end=None) # Converte l'intero PDF
                cv.close()

                docx_bytes = read_file_in_byte(temp_docx_path)
                return docx_bytes
            except Exception as e:
                print(f"Errore durante la conversione PDF a DOCX: {e}")
                return None
            finally:
                # Pulizia dei file temporanei
                if os.path.exists(temp_pdf_path):
                    os.remove(temp_pdf_path)
                if os.path.exists(temp_docx_path):
                    os.remove(temp_docx_path)
        return None
    except ImportError:
        print("Errore: Libreria 'pdf2docx' non installata. Per l'esportazione DOCX, esegui 'pip install pdf2docx'.")
        # Fornisci un fallback in byte per Streamlit
        return b"Errore: Libreria pdf2docx non trovata."
    except Exception as e:
        print(f"Errore generale durante la conversione Markdown a DOCX: {e}")
        return b"Errore nella conversione DOCX."