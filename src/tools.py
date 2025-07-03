from langchain_core.tools import tool
from src.agents import *
from typing import Optional
from httpx import HTTPStatusError

model = get_model()
cleaning_agent = create_cleaning_agent(model=model)
modifier_agent = create_modifier_agent(model=model)
organizer_agent = create_organizer_agent(model=model)
retrieval_agent = create_retrieval_agent(model=model)
explainer_agent = create_explainer_agent(model=model)

# Tool per creare un nuovo documento (unisce pulizia e organizzazione)
def clean_text(text_to_add: str) -> str:
    """
    Va usato prima di qualunque aggiunta, modifica oppure organizzazione.
    Usa questo tool per correggere errori di battitura e ortografia nel testo in input.
    """
    testo_pulito_dict = cleaning_agent.invoke({"messages": [{"role": "user", "content": text_to_add}]})
    testo_pulito = testo_pulito_dict['messages'][-1].content
    return testo_pulito

@tool
def organize_text(documento_attuale: str, text_to_add: str) -> str:
    """
    Usa questo tool per organizzare autonomamente in sezioni quando ricevi solo il testo come input
    """
    input_organize = f"TESTO:\n{clean_text(text_to_add)}"

    testo_organizzato_dict = organizer_agent.invoke({"messages": [{"role": "user", "content": input_organize}]})
    testo_organizzato = testo_organizzato_dict['messages'][-1].content
    
    input_modifica = f"DOCUMENTO ATTUALE:\n{documento_attuale}\n\nCOMANDO: Aggiungi il seguente testo markdown: '{testo_organizzato}'"

    documento_modificato_dict = modifier_agent.invoke({"messages": [{"role": "user", "content": input_modifica}]})
    documento_modificato = documento_modificato_dict['messages'][-1].content
    return documento_modificato

# Tool per modificare il documento esistente
@tool
def modifica_documento(comando: str, documento_attuale: str) -> str:
    """
    Questo tool va usato dopo l'organizzazione autonoma oppure quando l'utente lo chiede esplicitamente.
    Usa questo tool per modificare, aggiungere, cancellare o riscrivere parti del documento corrente.
    Il testo può provenire dall'utente oppure dall'organizzatore autonomo.
    L'input deve essere un comando chiaro che descrive la modifica.
    """
    
    input_modifica = f"DOCUMENTO ATTUALE:\n{documento_attuale}\n\nCOMANDO:\n{clean_text(comando)}"

    documento_modificato_dict = modifier_agent.invoke({"messages": [{"role": "user", "content": input_modifica}]})
    documento_modificato = documento_modificato_dict['messages'][-1].content

    return documento_modificato

# Tool per recuperare informazioni dal documento
@tool
def recupera_informazioni(query: str, documento_attuale: str) -> str:
    """
    Usa questo tool per cercare e recuperare informazioni o sezioni dal documento corrente.
    L'input deve essere una domanda (es. 'mostrami la sezione Y', 'che cosa ho scritto?, 'mostrami il documento').
    """
    input_recupero = f"DOCUMENTO ATTUALE:\n{documento_attuale}\n\nRICHIESTA:\n{query}"

    info_recuperate_dict = retrieval_agent.invoke({"messages": [{"role": "user", "content": input_recupero}]})
    info_recuperate = info_recuperate_dict['messages'][-1].content

    return info_recuperate

    
@tool
def apri_file(filename: str) -> str:
    """
    Usa questo tool per aprire un file di testo e leggerne il contenuto.
    L'input deve essere il nome del file.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Errore: File '{filename}' non trovato."
    except Exception as e:
        return f"Errore durante l'apertura del file: {e}"

@tool
def salva_file(filename: str, content: str) -> str:
    """
    Usa questo tool per salvare del testo in un file.
    L'input deve essere il nome del file e il contenuto da salvare.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"File '{filename}' salvato con successo."
    except Exception as e:
        return f"Errore durante il salvataggio del file: {e}"
    
@tool
def explain_capabilities(conversation: str):
    """
    Usa questo tool quando l'input è una conversazione semplice, senza nessun riferimento alla gestione di documenti.
    Questo tool spiega quali sono le funzioni che sei in grado di fare.
    """
    
    spiegazione_dict = retrieval_agent.invoke({"messages": [{"role": "user", "content": conversation}]})
    spiegazione = spiegazione_dict['messages'][-1].content

    return spiegazione
    
# Funzione di utilità per formattare i tool nel prompt
def format_tools_for_prompt(tools):
    tool_descriptions = []
    for tool in tools:
        tool_descriptions.append(f"- {tool.name}: {tool.description}\n  Argomenti: {tool.args}")
    return "\n".join(tool_descriptions)

# Funzione per restituire i tool, formattati per essere utilizzati nel planner_prompt
def get_tools():
    
    lista_tools = [
        modifica_documento,
        recupera_informazioni,
        organize_text,
        explain_capabilities,
        apri_file,
        salva_file
    ]
    
    return lista_tools