# AI Markdown Manager

AI Markdown Manager è un'applicazione che consente di interagire, tramite interfaccia Streamlit, con agenti intelligenti specializzati nella redazione di documenti Markdown. L'applicazione è in grado di fare le seguenti cose:
- creare documenti Markdown;
- modificare documenti;
- organizzare autonomamente un testo in sezioni e sottosezioni;
- salvare e aprire file in formato Markdown, passando il percorso completo;
- visualizzare specifiche sezioni o parti di un documento;

L'interfaccia Streamlit permette di:
- scrivere prompt agli agenti e visualizzarne la risposta;
- dettare i prompt, facendo uso del modello [whisper-base](https://huggingface.co/openai/whisper-base) che viene eseguito in locale;
- esportare l'intera conversazione oppure il documento prodotto nei formati: HTML, PDF, Markdown e DOCX;

Il progetto è stato sviluppato come parte del corso "Agenti Intelligenti e Machine Learning", erogato dall'azienda Aitho (https://aitho.it/) presso l'università di Catania.

L'architettura scelta per il progetto, coerentemente con i contenuti del corso, è l'architettura multi-agente **Plan-Execute**. In questa architettura, l'agente Planner scompone il prompt in compiti da eseguire e crea un piano da passare all'Executor, il quale esegue i compiti usando i tool specificati dal Planner. Per ognuna delle attività descritte è presente un relativo tool. Ad eccezione dell'apertura e salvataggio file, gli altri tool fanno uso di agenti react specializzati nella relativa attività (come l'organizzazione del testo).

L'intero progetto fa uso dei modelli Mistral, attraverso una chiave API ottenibile gratuitamente registrandosi alla piattaforma (https://mistral.ai/). Come impostazione predefinita, il modello utilizzato per gli agenti è `mistral-small-latest`

Come requisito richiesto per la realizzazione, una ingente parte del codice (superiore al 50%) è stato scritto in **Vibe Coding**. Per questo proposito è stato utilizzato **Gemini 2.5 Pro**. 

Team di sviluppo: **Edoardo Tantari e Raffaele Terracino.**

## Installazione ed esecuzione
Le istruzioni per installare ed eseguire l'applicazione sono le seguenti:
- Installare Python 3.12 (altre versioni non sono supportate)
- Installare Poetry seguendo la guida ufficiale: https://python-poetry.org/docs/
- Eseguire il comando `poetry install`
- Copiare il file .env.example, rinominarlo in .env ed inserire la propria chiave API Mistral nel campo `MISTRAL_API_KEY`
- Per poter effettuare la dettatura, è necessario installare FFMPEG sul proprio sistema seguendo la guida al link: https://ffmpeg.org/download.html
- Eseguire l'applicazione con il comando `poetry run streamlit run app/app.py`

**Nota importante**: il primo avvio dell'applicazione potrebbe chiedere circa un minuto a causa del download e setup del modello Whisper per la dettatura.**

## Struttura del progetto
- `app`: contiene l'applicazione Streamlit da eseguire;
- `src`: contiene l'architettura Plan-Execute realizzata; in particolare:
  - `agents.py`: contiene la definizione degli agenti specializzati nelle attività relative alla redazione di markdown;
  - `tools.py`: contiene le definizioni dei tool da eseguire;
  - `nodes.py`: contiene le definizioni dei nodi Planner ed Executor;
  - `report_manager.py`: classe che istanzia il grafo Langchain per creare l'architettura. Contiene il metodo `run` che permette di interagire con gli agenti attraverso un prompt;
  - `transcribe.py`: permette di utilizzare il modello Whisper per la trascrizione audio;
  - `convert.py`: contiene la logica per l'esportazione della chat e del documento nei formati menzionati.
- `notebook`: contiene un esempio di main in cui testare al volo le funzionalità dell'architettura

# Linee Guida per il prompting
Gli agenti costruiti non hanno memoria dei comandi precedenti ma soltanto del documento markdown corrente.
Pertanto, per avere i migliori risultati, è importante formattare bene i prompt indicando esplicitamente sezioni, testo da aggiungere e comandi..
Esempi:
- "Crea un nuovo documento con sezione 'Introduzione' vuota";
- "Nella sezione Introduzione, aggiungi il seguente testo: 'Ciao! Questo è il mio documento'";
- "Nella sezione Star Wars, genera una lista contente tutti i film della saga";


# Esempi di utilizzo
Nel seguente screenshot, l'input è un testo sulla regina Elisabetta. Gli agenti lo organizzano autonomamente in sezioni. Quando arriva una seconda parte, gli agenti dapprima lo organizzano e successivamente lo aggiungono al documento creato.

![Esempio di inferenza](images/esempio_app.png)

Un esempio di conversazione completa è il seguente: [Esempio completo](examples/esempio_chat.pdf)
