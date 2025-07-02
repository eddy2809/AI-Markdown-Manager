import os
import markdown
from xhtml2pdf import pisa
from pdf2docx import Converter



def convert_md_to_html(input_md):
    """
    Converte un file Markdown in HTML usando solo la libreria Python-Markdown.
    """
    if not os.path.exists(input_md):
        print(f"Errore: Il file '{input_md}' non esiste.")
        return

    try:
        with open(input_md, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        html_content = markdown.markdown(markdown_content, extensions=['extra','codehilite'])
        # 'extra' aggiunge supporto per liste, tabelle, note a piè di pagina, ecc.
        # 'codehilite' per la sintassi evidenziata del codice (richiede Pygments)

        file_name, _ = os.path.splitext(input_md)
        output_html = f"{file_name}.html"

        with open(output_html, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"Conversione Markdown a HTML completata: '{output_html}'")

    except Exception as e:
        print(f"Errore durante la conversione in HTML: {e}")

    return html_content,file_name

    


def convert_html_to_pdf(html_string, pdf_path):
    with open(pdf_path, "wb") as pdf_file:
        pisa_status = pisa.CreatePDF(html_string, dest=pdf_file)
        
    return not pisa_status.err


def convert_pdf_to_docx(pdf_file):
    cv = Converter(pdf_file)
    cv.convert()   
    cv.close()

def convert_md_to_docx(md_file):
    html_content,file_name = convert_md_to_html(md_file)
    convert_html_to_pdf(html_content, f"{file_name}.pdf")
    convert_pdf_to_docx(f"{file_name}.pdf")


convert_md_to_docx("complex.md")