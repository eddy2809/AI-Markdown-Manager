from langchain_core.tools import tool
from src.agents import *
from typing import Optional


model = get_model()
cleaning_agent = create_cleaning_agent(model=model)
modifier_agent = create_modifier_agent(model=model)
organizer_agent = create_organizer_agent(model=model)
retrieval_agent = create_retrieval_agent(model=model)

# Tool per creare un nuovo documento (unisce pulizia e organizzazione)
@tool
def crea_nuovo_documento(testo_grezzo: str, titolo: Optional[str] = None) -> str:
    """
    Usa questo tool per creare un nuovo report partendo da un testo grezzo.
    Pulisce il testo e lo organizza in sezioni.
    """
    
    # 1. Chiama l'agente di pulizia
    testo_pulito_dict = cleaning_agent.invoke({"messages": [{"role": "user", "content": testo_grezzo}]})
    testo_pulito = testo_pulito_dict['messages'][-1].content

    # 2. Chiama l'agente di organizzazione
    input_organizzazione = f"Testo: {testo_pulito}"

    if titolo:
        input_organizzazione += f"\nTitolo suggerito: {titolo}"

    documento_organizzato_dict = organizer_agent.invoke({"messages": [{"role": "user", "content": input_organizzazione}]})
    documento_organizzato = documento_organizzato_dict['messages'][-1].content

    return documento_organizzato

# Tool per modificare il documento esistente
@tool
def modifica_documento(comando: str, documento_attuale: str) -> str:
    """
    Usa questo tool per modificare, aggiungere, cancellare o riscrivere parti del documento corrente.
    L'input deve essere un comando chiaro che descrive la modifica.
    """
    input_modifica = f"DOCUMENTO ATTUALE:\n{documento_attuale}\n\nCOMANDO:\n{comando}"

    documento_modificato_dict = modifier_agent.invoke({"messages": [{"role": "user", "content": input_modifica}]})
    documento_modificato = documento_modificato_dict['messages'][-1].content

    return documento_modificato

# Tool per recuperare informazioni dal documento
@tool
def recupera_informazioni(query: str, documento_attuale: str) -> str:
    """
    Usa questo tool per cercare e recuperare informazioni o sezioni dal documento corrente.
    L'input deve essere una domanda (es. 'mostrami la sezione Y').
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
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(content)
        return f"File '{filename}' salvato con successo."
    except Exception as e:
        return f"Errore durante il salvataggio del file: {e}"
    
    
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
    
    
# Funzione di utilità per formattare i tool nel prompt
def format_tools_for_prompt(tools):
    tool_descriptions = []
    for tool in tools:
        tool_descriptions.append(f"- {tool.name}: {tool.description}\n  Argomenti: {tool.args}")
    return "\n".join(tool_descriptions)

# Funzione per restituire i tool, formattati per essere utilizzati nel planner_prompt
def get_tools():
    
    lista_tools = [
        crea_nuovo_documento,
        modifica_documento,
        recupera_informazioni,
        apri_file,
        salva_file
    ]
    
    return lista_tools