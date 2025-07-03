import json
from src.agents import *
from src.tools import *
from langgraph.graph import StateGraph, END

tool_list = get_tools()

def planner_node(state) -> dict:
    """
    Questo nodo genera il piano d'azione.
    """
    print("--- NODO: Planner ---")

    # Il prompt finale per il nostro Planner
    PLANNER_PROMPT_TEMPLATE = f"""
    Sei un pianificatore di task esperto. Il tuo compito è analizzare la richiesta dell'utente e scomporla in una sequenza di passi da eseguire usando i tool a tua disposizione.

    # TOOL DISPONIBILI
    {format_tools_for_prompt(tools=tool_list)}
    # ISTRUZIONI
    - Analizza la richiesta e crea un piano step-by-step.
    - Ogni passo del piano deve essere una chiamata a uno dei tool disponibili.
    - Restituisci il piano come una lista JSON valida `[ ]`. IMPORTANTE: non inserire nulla prima e dopo le parentesi quadre. Ogni elemento della lista è un dizionario con due chiavi: "tool_name" (il nome del tool da usare) e "args" (un dizionario con gli argomenti per quel tool).
    - Estrai gli argomenti direttamente dalla richiesta dell'utente.
    - Se la richiesta è una semplice conversazione (es. "ciao"), spiega i tool che hai a disposizione.

    # ESEMPIO
    Richiesta: "Apri 'report_vecchio.md', cancella la sezione 'Note' e salva tutto come 'report_nuovo.md'."
    Output:
    [
        {{"tool_name": "apri_file", "args": {{"filename": "report_vecchio.md"}}}},
        {{"tool_name": "modifica_documento", "args": {{"comando": "cancella la sezione 'Note'"}}}},
        {{"tool_name": "salva_file", "args": {{"filename": "report_nuovo.md"}}}}
    ]
    """.replace("    ", "")


    # Combiniamo il template del prompt con l'input specifico dell'utente
    prompt = PLANNER_PROMPT_TEMPLATE + f"\n\n# RICHIESTA REALE\nRichiesta: \"{state['input']}\"\nOutput:"

    # Chiamiamo l'LLM per generare il piano
    response = model.invoke(prompt)
    llm_output = response.content

    try:
        # Validiamo e carichiamo l'output JSON in una lista Python
        
        if llm_output.startswith("```json") and llm_output.endswith("```"):
            llm_output = llm_output.removeprefix("```json").removesuffix("```")
        
        plan = json.loads(llm_output)

        if not isinstance(plan, list):
            print("Errore: Il piano generato non è una lista.")
            print("Piano generato: ", plan)
            
            return {"plan": []} # Piano vuoto in caso di formato non valido

        print(f"Piano generato: {plan}")
        # Aggiorniamo lo stato del grafo con il nuovo piano
        return {"plan": plan}
    except json.JSONDecodeError:
        print(f"Errore di decodifica JSON: L'LLM ha restituito un output malformato.\n{llm_output}")
        return {"plan": [], "response": llm_output} # Piano vuoto in caso di errore
    
    
# Creiamo un dizionario per un accesso rapido ai tool tramite il loro nome

tool_map = {tool.name: tool for tool in tool_list}

def executor_node(state) -> dict:
    """
    Questo nodo esegue un singolo passo del piano.
    """
    print("--- NODO: Executor ---")

    # Se il piano è vuoto, non fare nulla
    if not state['plan']:
        print("Il piano è vuoto. Nessuna azione da eseguire.")
        return {}

    # Prendi il primo passo dal piano
    plan = state['plan']
    step = plan.pop(0)
    tool_name = step.get("tool_name")
    args = step.get("args", {})

    print(f"Esecuzione task: {tool_name} con argomenti: {args}")

    # Cerca il tool corrispondente
    if tool_name not in tool_map:
        result = f"Errore: Tool '{tool_name}' non trovato."
        return {"past_steps": [(step, result)]}

    # Prepara gli argomenti per il tool
    tool_to_call = tool_map[tool_name]
    kwargs = args.copy() # Copia gli argomenti dal piano

    # --- Logica di Assemblaggio Argomenti ---
    # Controlla se il tool ha bisogno del contenuto del documento e glielo fornisce
    # leggendolo dallo stato del grafo.
    if "documento_attuale" in tool_to_call.args:
        kwargs["documento_attuale"] = state.get("document_content", "")

    if "content" in tool_to_call.args and "content" not in kwargs:
        kwargs["content"] = state.get("document_content", "")
    # --- Fine Logica di Assemblaggio ---

    try:
        # Esegui il tool con gli argomenti assemblati
        result = tool_to_call.invoke(kwargs)
    except Exception as e:
        result = f"Errore durante l'esecuzione del tool '{tool_name}': {e}"
    
    print(result)

    # Aggiorna lo stato del documento se il tool lo modifica
    new_document_content = state.get("document_content", "")
    if tool_name in ["crea_nuovo_documento", "modifica_documento", "apri_file"]:
        # Questi tool restituiscono il nuovo contenuto del documento
        new_document_content = result

    # Salva il risultato per la cronologia
    return {
        "plan": plan, # Aggiorna il piano (abbiamo rimosso un elemento)
        "past_steps": [(step, result)],
        "document_content": new_document_content # Aggiorna il contenuto del documento
    }
    

def should_continue(state) -> str:
    """
    Decide se continuare con l'esecuzione del piano o terminare.
    """
    if state["plan"]:
        # Se ci sono ancora passi nel piano, torna all'executor
        return "executor"
    else:
        # Se il piano è vuoto, termina il flusso
        return END