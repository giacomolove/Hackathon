---
description: Controlla che nessun dato di dominio sia sfuggito da app/data.js verso il codice o i prompt, e che il tool resti allineato agli slot esistenti.
---

Controlla staticamente l'invariante architetturale di VoceAmica: **ogni dato che
l'assistente può pronunciare esiste in `app/data.js`**. Questa è una verifica di
codice, non richiede di avviare l'applicazione.

Esegui questi controlli e riporta ogni violazione con file e riga.

**1. Dati sfuggiti in `app.js`.** Cerca in `app/app.js` date, orari, importi in euro,
   indirizzi, numeri di telefono e codici di prestazione. L'unico testo con contenuto
   di dominio ammesso in `app.js` è la costante `SALUTO` e i messaggi di servizio
   rivolti a Mario (errori, sollecito di silenzio). Qualunque altro dato concreto
   è una violazione: va spostato in `data.js`.

**2. Coerenza del tool.** Confronta l'`enum` di `slot_id` nello schema di
   `TOOL_CONFERMA_PRENOTAZIONE` con gli `id` effettivi di `CUP_SLOTS`. Devono
   corrispondere esattamente. Un `enum` più largo degli slot esistenti permette al
   modello di scegliere uno slot inesistente.

**3. Validazione lato client.** Verifica che `eseguiTool` continui a cercare lo slot
   in `CUP_SLOTS` e a restituire un errore se non lo trova, invece di fidarsi
   dell'input del modello.

**4. Regole di grounding nel prompt.** Verifica che `buildSystemPrompt` contenga
   ancora tutte e tre le regole: divieto di inventare dati, obbligo del marcatore di
   paragrafo con ripetizione letterale di importi e scadenze, obbligo di chiamare la
   funzione prima di dichiarare una prenotazione fatta. Se una è stata accorciata o
   ammorbidita, segnalalo: sono la difesa principale del progetto.

**5. Parametri dell'API.** Controlla in `app/app.js` che il modello sia
   `claude-haiku-4-5`, che `max_tokens` sia almeno 700, che l'header
   `anthropic-dangerous-direct-browser-access` sia presente, e che **non** vengano
   inviati `thinking` né `output_config.effort`.

**6. Igiene dell'output.** Verifica che il testo proveniente dal modello venga
   inserito nel DOM con `textContent` e non con `innerHTML`.

Se tutti i controlli passano, dillo in una riga. Non proporre refactoring:
questo comando verifica, non riscrive.
