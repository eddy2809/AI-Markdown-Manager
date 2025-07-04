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

def clean_text(text_to_add: str) -> str:
    """
    Funzione di utilità che chiama un agente specializzato nella correzione di errori grammaticali o ortografia. 
    Non è un tool.
    Viene utilizzato prima di aggiungere testo al documento markdown.
    """
    result_cleaner = cleaning_agent.invoke({"messages": [{"role": "user", "content": text_to_add}]})
    cleaned_text = result_cleaner['messages'][-1].content
    return cleaned_text

@tool
def organize_text(current_document: str, text_to_add: str) -> str:
    """
    Usa questo tool per organizzare in sezioni SOLAMENTE quando ricevi un testo senza indicazioni sulle sezioni
    """
    input_organizer = f"TESTO:\n{clean_text(text_to_add)}"

    result_cleaner = organizer_agent.invoke({"messages": [{"role": "user", "content": input_organizer}]})
    cleaned_text = result_cleaner['messages'][-1].content
    
    input_modifier = f"DOCUMENTO ATTUALE:\n{current_document}\n\nCOMANDO: Aggiungi il seguente testo markdown: '{cleaned_text}'"

    result_modifier = modifier_agent.invoke({"messages": [{"role": "user", "content": input_modifier}]})
    new_document = result_modifier['messages'][-1].content
    return new_document

# Tool per modificare il documento esistente
@tool
def modify_document(command: str, current_document: str) -> str:
    """
    Usa questo tool per creare e modificare documenti markdown.
    Il testo deve provenire dall'utente.
    L'input deve essere un comando chiaro che descrive la modifica.
    """
    
    input_modifier = f"DOCUMENTO ATTUALE:\n{current_document}\n\nCOMANDO:\n{clean_text(command)}"

    result = modifier_agent.invoke({"messages": [{"role": "user", "content": input_modifier}]})
    new_document = result['messages'][-1].content

    return new_document

# Tool per recuperare informazioni dal documento
@tool
def retrieve_document(query: str, current_document: str) -> str:
    """
    Usa questo tool per cercare e recuperare informazioni o sezioni dal documento corrente.
    L'input deve essere una domanda (es. 'mostrami la sezione Y', 'che cosa ho scritto?, 'mostrami il documento').
    """
    input_retrieval = f"DOCUMENTO ATTUALE:\n{current_document}\n\nRICHIESTA:\n{query}"

    result_retrieval = retrieval_agent.invoke({"messages": [{"role": "user", "content": input_retrieval}]})
    document_retrieved = result_retrieval['messages'][-1].content

    return document_retrieved

    
@tool
def open_file(filename: str) -> str:
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
def save_file(filename: str, content: str) -> str:
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
    
    explainer_result = explainer_agent.invoke({"messages": [{"role": "user", "content": conversation}]})
    explanation = explainer_result['messages'][-1].content

    return explanation
    
# Funzione di utilità per formattare i tool nel prompt
def format_tools_for_prompt(tools):
    tool_descriptions = []
    for tool in tools:
        tool_descriptions.append(f"- {tool.name}: {tool.description}\n  Argomenti: {tool.args}")
    return "\n".join(tool_descriptions)

# Funzione per restituire i tool, formattati per essere utilizzati nel planner_prompt
def get_tools():
    
    tools = [
        modify_document,
        retrieve_document,
        organize_text,
        explain_capabilities,
        open_file,
        save_file
    ]
    
    return tools