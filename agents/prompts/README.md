# Prompt

Due famiglie di prompt: quello con cui è partito il build, e quelli che girano dentro
il prodotto.

## Prompt di build

[`brief-iniziale.md`](brief-iniziale.md) — il brief funzionale consegnato a Claude Code
all'inizio, conservato **senza modifiche**. È la prova di dove è servita la revisione
umana: confrontandolo con il codice finale si vedono le correzioni descritte in
[`../WORKFLOW.md`](../WORKFLOW.md) §5.

| Nel brief | Nel prototipo | Perché |
|---|---|---|
| «rispondi come se le facessi davvero» | Il modello usa solo `<DATI_VERIFICATI>` | Le date e gli ospedali venivano inventati |
| `claude-sonnet-4-6`, `max_tokens: 300` | `claude-haiku-4-5`, `max_tokens: 700` | 300 troncava il JSON della chiamata a funzione |
| Tutto in un solo `index.html` | `index.html` + `data.js` + `app.js` | Separare i dati dal codice rende verificabile la regola anti-invenzione |
| Nessuna tracciabilità | Marcatori `[Pn]` ed evidenziazione del paragrafo | «Semplificare senza tradire» deve essere controllabile |

## Prompt di prodotto

Vivono in [`app/data.js`](../../app/data.js), insieme ai dati, perché nessun dato di
dominio deve stare altrove. Qui solo la descrizione.

### `buildSystemPrompt(memoria, prenotazioni)` — chi parla con Mario

Struttura, nell'ordine:

1. **Ruolo e registro.** Figlio paziente al telefono, frasi corte, del tu, un passo alla volta.
2. **Regole sui dati, non derogabili.**
   - usa solo `<DATI_VERIFICATI>`; se un dato non c'è, dillo e rimanda allo sportello;
   - la `<MEMORIA>` non è fonte di fatti;
   - quando spieghi la lettera chiudi con il marcatore `[Pn]` e ripeti importi e date letterali;
   - per prenotare chiama `conferma_prenotazione`, mai «ho prenotato» prima del risultato.
3. **Profilo di Mario** (JSON).
4. **`<DATI_VERIFICATI>`**: slot CUP, prenotazioni già confermate, testo della lettera
   diviso in paragrafi, contatti.
5. **`<MEMORIA>`** (solo se esiste): la scheda scritta dall'archivista.
6. **Confini**: niente diagnosi, farmaci, consulenza legale o fiscale.

Unico strumento: `conferma_prenotazione` (`TOOL_CONFERMA_PRENOTAZIONE`). L'`enum` di
`slot_id` è generato dagli slot esistenti, e `eseguiTool` in `app/app.js` ricontrolla
lo slot prima di generare il codice.

### `buildPromptArchivista()` — chi scrive la memoria

Gira a chiamata chiusa, senza strumenti. Riceve scheda precedente, trascrizione e fatti
verificati della chiamata (`buildRichiestaArchivista`) e restituisce solo markdown con
sezioni fisse: *Chi è*, *Dove si blocca*, *Pratiche concluse*, *In sospeso*, *Note per
la prossima chiamata*. Non può inferire, non annota valutazioni mediche, non riporta
codici fiscali né chiavi.

## Come si verifica che i prompt reggano

- [`/controlla-grounding`](../claude-code/commands/controlla-grounding.md) controlla che
  le tre regole sui dati siano ancora nel prompt, non ammorbidite.
- [`app/test.html`](../../app/test.html) verifica in automatico che il prompt contenga la
  regola anti-invenzione e la clausola sulla memoria.
- [`/verifica-flussi`](../claude-code/commands/verifica-flussi.md) esegue la prova dal
  vivo: a «c'è posto venerdì pomeriggio?» VoceAmica deve dire che non ha quel dato.
