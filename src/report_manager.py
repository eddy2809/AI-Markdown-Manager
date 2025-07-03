from typing import TypedDict
from src.nodes import *

class ConfigSchema(TypedDict):
    input: str
    plan: list[str]
    past_steps: list[str]
    response: str
    document_content: str
    
class ReportManager():
    def __init__(self):
        # 1. Inizializzare il grafo con il nostro stato personalizzato
        self.workflow = StateGraph(ConfigSchema)

        # 2. Aggiungere i nodi che abbiamo creato
        self.workflow.add_node("planner", planner_node)
        self.workflow.add_node("executor", executor_node)

        # 3. Definire il punto di partenza del grafo
        self.workflow.set_entry_point("planner")

        # 4. Aggiungere i collegamenti tra i nodi
        # Dopo il planner, si va sempre all'executor
        self.workflow.add_edge('planner', 'executor')

        # Dopo l'executor, usiamo la nostra funzione per decidere dove andare
        self.workflow.add_conditional_edges(
            "executor",
            should_continue,
            {
                "executor": "executor", # Se la funzione restituisce "executor", torna al nodo executor
                END: END              # Se la funzione restituisce END, termina il grafo
            }
        )

        # 5. Compilare il grafo per renderlo eseguibile
        self.app = self.workflow.compile()

        # Definiamo lo stato iniziale con il comando e il documento vuoto
        self.current_state: ConfigSchema = {
            "input": "",
            "plan": [],
            "past_steps": [],
            "response": "",
            "document_content": ""
        }
        
    def run(self, input):
        
        try:
            self.current_state["input"] = input
            self.current_state = self.app.invoke(self.current_state)
        except Exception as e:
            self.current_state['response'] = str(e)
        
    def get_answer(self):
        
        if self.current_state['response'] == "markdown":
            return self.current_state['document_content']
        else:
            return self.current_state['response']
        
    def get_md_document(self):
        return self.current_state['document_content']