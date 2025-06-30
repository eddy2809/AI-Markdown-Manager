import marimo

__generated_with = "0.14.9"
app = marimo.App(width="medium")


@app.cell
def _():
    # Cella 1: Import delle librerie necessarie (versione corretta)
    import marimo as mo
    import os
    from langchain_mistralai.chat_models import ChatMistralAI
    from langchain_core.messages import HumanMessage
    from dotenv import load_dotenv
    return ChatMistralAI, HumanMessage, load_dotenv, mo, os


@app.cell
def _(load_dotenv, os):
    load_dotenv(".env")
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
    return (MISTRAL_API_KEY,)


@app.cell
def _(MISTRAL_API_KEY, mo):
    if MISTRAL_API_KEY:
        output = mo.md("Chiave API di Mistral trovata nelle variabili d'ambiente.")
    else:
        output = mo.md(
            """
            ### 🔑 Inserisci la tua API Key di Mistral

            La tua API key non è stata trovata come variabile d'ambiente.
            Perfavore inseriscila nel file .env
            """
        )
    output
    return


@app.cell
def _():
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.prebuilt import create_react_agent
    from langchain.agents import Tool

    return MemorySaver, create_react_agent


@app.cell
def _(ChatMistralAI, MISTRAL_API_KEY, MemorySaver):
    memory = MemorySaver()

    llm = ChatMistralAI(
        name="mistral-small-latest",
        temperature=0.7,
        api_key=MISTRAL_API_KEY
    )

    return llm, memory


@app.cell
def _(create_react_agent, llm, memory):
    react_agent = create_react_agent(
        model=llm,
        checkpointer=memory,
        tools=[]
    )
    return (react_agent,)


@app.cell
def _(HumanMessage, react_agent):
    def invoke_react_agent(message, debug=False):
        text = getattr(message, "content", message)[-1].content

        response = react_agent.invoke(
            {"messages": HumanMessage(content=text)},
            config={
                "configurable": {
                    "session_id": "default",
                    "thread_id": "default",
                    "recursion_limit": 1,
                }
            },
            debug=debug,
        )
        return response["messages"][-1].content
    return (invoke_react_agent,)


@app.cell
def _(invoke_react_agent, mo):
    mo.ui.chat(
        invoke_react_agent,
    )
    return


@app.cell
def _(mo):
    mic = mo.ui.microphone()
    return (mic,)


@app.cell
def _(mic):
    mic
    return


@app.cell
def _(mic, mo):
    mo.audio(mic.value)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
